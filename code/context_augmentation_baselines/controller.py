import argparse
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from prompt import construct_fewshot_prompt, construct_fewshot_cot_prompt, construct_prompt, construct_cot_prompt

def get_arguments():
    parser = argparse.ArgumentParser(description='Evaluation Pipeline Controller')

    parser.add_argument('--llm', type=str, required=True, help='LLM')
    parser.add_argument('--temp', type=float, required=True, help='temperature')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt augmentation')

    args = parser.parse_args()
    return args
    
    # print(f"Input file: {args.input}")

    # For example:
    # process_files(args.input, args.output, args.config)

def select_llm(args):
    temp = float(args.temp)
    
    if args.llm == "gpt-4o-mini":
        return ChatOpenAI(model="gpt-4o-mini", temperature=temp)
    elif args.llm == "ollama":
        return ChatOllama(model="llama3.1", temperature=temp)
    elif args.llm == "gpt-4o":
        return ChatOpenAI(model="gpt-4o", temperature=temp)
    else: 
        raise ValueError("Invalid LLM")

def select_prompt_augmentation(args):
    if args.prompt == "few-shot":
        return construct_fewshot_prompt
    elif args.prompt == "few-shot-cot":
        return construct_fewshot_cot_prompt
    elif args.prompt == "prompt":
        return construct_prompt
    elif args.prompt == "cot":
        return construct_cot_prompt
    else:
        raise ValueError("Invalid prompt augmentation")
    