from agent import Agent, BaselineAgent
from tools import REACT_TOOLS 
from util import create_session
import json
import os
from langsmith import wrappers, traceable
from controller import select_llm, select_prompt_augmentation, get_arguments
from env import LANGCHAIN_API_KEY 
from langsmith import wrappers, traceable
from datetime import datetime
from enum import Enum, auto
 

class PredictionOutcome(Enum):
    REACT_OVER_BASELINE = auto()
    BASELINE_OVER_REACT = auto()
    BOTH_BAD = auto()


os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
BENCHMARK = "final_benchmark.jsonl"
LLM = None
PROMPT_AUGMENTATION = None



@traceable
def predict(agent, function):
    prompt = PROMPT_AUGMENTATION(function)
    return agent.predict(prompt)
    
    

def react_predict(item, react_agent):
        benign_function = item["non_vulnerable_function_body"]

        non_vulnerable_caller_graph = item["non_vulnerable_caller_graph"]
        non_vulnerable_callee_graph = item["non_vulnerable_callee_graph"]
        non_vulnerable_function_bodies = item["non_vulnerable_function_bodies"]
        create_session(non_vulnerable_callee_graph, non_vulnerable_caller_graph, non_vulnerable_function_bodies)
        
        benign_prediction, _ = predict(react_agent, benign_function)
        
        vulnerable_function = item["vulnerable_function_body"]
        cwe = item["cwe"]
            
        vulnerable_caller_graph = item["vulnerable_caller_graph"]
        vulnerable_callee_graph = item["vulnerable_callee_graph"]
        vulnerable_function_bodies = item["vulnerable_function_bodies"]
        create_session(vulnerable_callee_graph, vulnerable_caller_graph, vulnerable_function_bodies)
        
        vulnerable_prediction, cwe_prediction = predict(react_agent, vulnerable_function)
        
        return {
            "benign_prediction": benign_prediction,
            "vulnerable_prediction": vulnerable_prediction,
        }

def baseline_predict(item, baseline_agent):
    benign_function = item["non_vulnerable_function_body"]
    benign_prediction, _ = predict(baseline_agent, benign_function)
    
    vulnerable_function = item["vulnerable_function_body"]
    vulnerable_prediction, cwe_prediction = predict(baseline_agent, vulnerable_function)

    
    
    return {
            "benign_prediction": benign_prediction,
            "vulnerable_prediction": vulnerable_prediction,
        }
    
def persist(index, prediction_outcome):
    file_name = None
    if prediction_outcome == PredictionOutcome.REACT_OVER_BASELINE:
        file_name = "react_over_baseline.txt"
    elif prediction_outcome == PredictionOutcome.BASELINE_OVER_REACT:
        file_name = "baseline_over_react.txt"
    elif prediction_outcome == PredictionOutcome.BOTH_BAD:
        file_name = "both_bad.txt"
        
    
    with open(file_name, "a") as f:
        f.write(f"{index}\n")
        
    
    
    

def experiment(benchmark):
    
    
    react_agent = Agent(llm=LLM, tools=REACT_TOOLS)
    baseline_agent = BaselineAgent(llm=LLM)
    

    for index, item in enumerate(benchmark):
        react_predictions = react_predict(item, react_agent)
        baseline_predictions = baseline_predict(item, baseline_agent)
        
        
        correct_react_prediction = react_predictions["vulnerable_prediction"] == 1 and react_predictions["benign_prediction"] == 0
        correct_baseline_prediction = baseline_predictions["vulnerable_prediction"] == 1 and baseline_predictions["benign_prediction"] == 0
        
        if correct_react_prediction and not correct_baseline_prediction:
            persist(index, PredictionOutcome.REACT_OVER_BASELINE)
            
        elif correct_baseline_prediction and not correct_react_prediction:
            persist(index, PredictionOutcome.BASELINE_OVER_REACT)
            
        elif not (correct_baseline_prediction or correct_react_prediction):
            persist(index, PredictionOutcome.BOTH_BAD)
            


def main():
    with open(BENCHMARK, "r") as f:
        benchmark = [json.loads(line) for line in f]

    args = get_arguments()
    global LLM
    LLM = select_llm(args)
    global PROMPT_AUGMENTATION
    PROMPT_AUGMENTATION = select_prompt_augmentation(args)
    
    
    today = datetime.today().strftime('%Y-%m-%d')
    
    experiment_name = f"{args.llm}_{args.prompt}_{args.temp}_{today}"    
    print(experiment_name)
    os.environ["LANGSMITH_PROJECT"] = experiment_name
    experiment(benchmark)
    

if __name__ == "__main__":
    main()