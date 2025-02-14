from util import load_jsonl
from pprint import pprint
from agent import BaselineAgent
from cloner import Cloner
from controller import select_llm, select_prompt_augmentation, get_arguments
from context import get_context

PROMPT_AUGMENTATION = None
LLM = None

def clone(project_url, commit_id):
    cloner = Cloner()
    cloner.remove_repo()
    
    cloner.clone(project_url)
    cloner.checkout(commit_id)

def predict(agent, function, context):
    prompt = PROMPT_AUGMENTATION(function, context)
    return agent.predict(prompt)  

def experiment(project_url, commit_id, agent, function, context):
    clone(project_url, commit_id)
    label, cwe = predict(agent, function, context)
    return label, cwe
    
    
def main():
    benchmark = load_jsonl("benchmark.jsonl")
    
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
    
    agent = BaselineAgent(LLM)
    
    for item in benchmark:
        
        project_url = item["project_url"]
        vulnerability_introducing_commit_id = item["vulnerability_introducing_commit_id"]

        vulnerable_function_body = item["vulnerable_function_body"]
        cwe = item["cwe"]
        
        context = get_context(vulnerable_function_body)

        vulnerable_prediction, cwe_prediction = experiment(
            project_url, 
            commit_id = vulnerability_introducing_commit_id, 
            agent = agent,
            function = vulnerable_function_body,
            context = context
        )
        
        vulnerability_fixing_commit_id = item["vulnerability_fixing_commit_id"]
        non_vulnerable_function_body = item["non_vulnerable_function_body"]
        
        
        context = get_context(non_vulnerable_function_body)

        benign_prediction, _ = experiment(
            project_url, 
            commit_id = vulnerability_fixing_commit_id, 
            agent = agent,
            function = non_vulnerable_function_body,
            context = context
        )
        
        if vulnerable_prediction == 1 and benign_prediction == 1:
            pv += 1
            tp += 1
            fp += 1
            
        elif vulnerable_prediction == 1 and benign_prediction == 0:
            pc += 1
            tp += 1
            tn += 1
            
        elif vulnerable_prediction == 0 and benign_prediction == 1:
            pr += 1
            fn += 1
            fp += 1
            
        elif vulnerable_prediction == 0 and benign_prediction == 0:
            pb += 1
            fn += 1
            tn += 1
        
        if cwe_prediction in cwe:
            true_cwe += 1
        else:
            false_cwe += 1
        
        
        # break
    
    print()
    print(LLM)
    print(PROMPT_AUGMENTATION.__name__)
    print(f"TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
    print(f"True CWE: {true_cwe}, False CWE: {false_cwe}")
    print(f"PC: {pc}, PV: {pv}, PB: {pb}, PR: {pr}")
    print("="*30)  

if __name__ == "__main__":
    args = get_arguments()
    LLM = select_llm(args)
    PROMPT_AUGMENTATION = select_prompt_augmentation(args)
    
    
    main()