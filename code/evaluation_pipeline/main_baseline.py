from agent import BaselineAgent
from tools import REACT_TOOLS 
from util import create_session
import json
import os
from langsmith import wrappers, traceable
from controller import select_llm, select_prompt_augmentation, get_arguments
from env import LANGCHAIN_API_KEY

os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
BENCHMARK = "final_benchmark.jsonl"
LLM = None
PROMPT_AUGMENTATION = None

from langsmith import wrappers, traceable
from datetime import datetime
 
@traceable
def predict(agent, function):
    prompt = PROMPT_AUGMENTATION(function)
    return agent.predict(prompt)
    
    

def experiment(benchmark):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    false_cwe = 0
    true_cwe = 0
    
    pc = 0
    pv = 0
    pb = 0
    pr = 0
    
    
    
    agent = BaselineAgent(
        llm=LLM
    )
    
    for item in benchmark:

            
        try:
            print(f"project: {item['project']}, vulnerability_introducing_commit: {item['vulnerability_introducing_commit']} vulnerability_fixed_commit: {item['vulnerability_fixed_commit']}")
            benign_function = item["non_vulnerable_function_body"]
            
            non_vulnerable_caller_graph = item["non_vulnerable_caller_graph"]
            non_vulnerable_callee_graph = item["non_vulnerable_callee_graph"]
            non_vulnerable_function_bodies = item["non_vulnerable_function_bodies"]
            create_session(non_vulnerable_callee_graph, non_vulnerable_caller_graph, non_vulnerable_function_bodies)
            
            benign_prediction, _ = predict(agent, benign_function)
            
            if benign_prediction == 1:
                fp += 1
            else:
                tn += 1 
            
            print("benign prediction: ", benign_prediction)

                
            vulnerable_function = item["vulnerable_function_body"]
            cwe = item["cwe"]
            
            vulnerable_caller_graph = item["vulnerable_caller_graph"]
            vulnerable_callee_graph = item["vulnerable_callee_graph"]
            vulnerable_function_bodies = item["vulnerable_function_bodies"]
            create_session(vulnerable_callee_graph, vulnerable_caller_graph, vulnerable_function_bodies)
            
            vulnerable_prediction, cwe_prediction = predict(agent, vulnerable_function)
            
            print("vulnerable prediction: ", vulnerable_prediction, "cwe prediction: ", cwe_prediction, "cwe: ", cwe)

            
            if cwe_prediction in cwe:
                true_cwe += 1
            else:
                false_cwe += 1
            
            
            if vulnerable_prediction == 1:
                tp += 1 
            else:
                fn += 1
                
            
            if benign_prediction == 0 and vulnerable_prediction == 0:
                pb += 1
            elif benign_prediction == 1 and vulnerable_prediction == 0:
                pr += 1 
            elif benign_prediction == 0 and vulnerable_prediction == 1:
                pc += 1 
            elif benign_prediction == 1 and vulnerable_prediction == 1:
                pv += 1
            
            
        
        except Exception:
            with open("error.txt", "a") as f:
                f.write(json.dumps(item) + "\n")
            continue
        
        print(f"TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
        print(f"True CWE: {true_cwe}, False CWE: {false_cwe}")
        print(f"PC: {pc}, PV: {pv}, PB: {pb}, PR: {pr}")
        print("="*30)  
        

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