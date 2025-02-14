import json
import random


def construct_prompt(function_body):
    return f"""
    You are a security researcher tasked with identifying vulnerabilities in a codebase. You have been given a function to analyze. 
    The function may or may not be vulnerable
    
    If you think it is vulnerable reply with @@VULNERABLE@@, otherwise reply with @@NOT VULNERABLE@@
    
    If you think the function is vulnerable, please provide the CWE number that you think is most relevant to the vulnerability in the form of @@CWE: <CWE_NUMBER>@@
    
    For example:
    
    @@VULNERABLE@@
    @@CWE: CWE-1234@@
    
    Here is the function:
    
    ```c
    {function_body}
    ```
    """



def construct_cot_prompt(function_body):
    return f"""
    You are a security researcher tasked with identifying vulnerabilities in a codebase. You have been given a function to analyze. 
    The function may or may not be vulnerable
    
    If you think it is vulnerable reply with @@VULNERABLE@@, otherwise reply with @@NOT VULNERABLE@@
    
    If you think the function is vulnerable, please provide the CWE number that you think is most relevant to the vulnerability in the form of @@CWE: <CWE_NUMBER>@@
    
    For example:
    
    @@VULNERABLE@@
    @@CWE: CWE-1234@@
    
    Here is the function:
    
    ```c
    {function_body}
    ```
    
    Solve this problem step by step. Carefully break down the reasoning process to arrive at the correct solution. Explain your reasoning at each step before providing the final answer.
    
    """

def construct_fewshot_prompt(function_body):
    with open('few-shots.json', 'r') as file:
        few_shots = json.load(file)

    examples = ""
    example = random.choice(few_shots)
    cwe = example["CWE"]
    vul_code = example["vul-code"]
    vul_explanation = example["vul-explanation"]
    sec_code = example["sec-code"]
    sec_explanation = example["sec-explanation"]
    
    examples += f"""
    Vulnerable code snippet:
    ```c
    {vul_code}
    ```
    Explanation: {vul_explanation}
    
    Secure code snippet:
    ```c
    {sec_code}
    ```
    Explanation: {sec_explanation}
    
    CWE: {cwe}
    """
    
        
    return f"""
    You are a security researcher tasked with identifying vulnerabilities in a codebase. You have been given a function to analyze. 
    The function may or may not be vulnerable
    
    If you think it is vulnerable reply with @@VULNERABLE@@, otherwise reply with @@NOT VULNERABLE@@
    
    If you think the function is vulnerable, please provide the CWE number that you think is most relevant to the vulnerability in the form of @@CWE: <CWE_NUMBER>@@
    
    For example:
    
    @@VULNERABLE@@
    @@CWE: CWE-1234@@
    
    Here is the function:
    
    ```c
    {function_body}
    ```
    
    example detections:
    
    {examples}     
    """
    

def construct_fewshot_cot_prompt(function_body):
    with open('few-shots.json', 'r') as file:
        few_shots = json.load(file)

    examples = ""
    example = random.choice(few_shots)
    cwe = example["CWE"]
    vul_code = example["vul-code"]
    vul_explanation = example["vul-explanation"]
    sec_code = example["sec-code"]
    sec_explanation = example["sec-explanation"]
    
    examples += f"""
    Vulnerable code snippet:
    ```c
    {vul_code}
    ```
    Explanation: {vul_explanation}
    
    Secure code snippet:
    ```c
    {sec_code}
    ```
    Explanation: {sec_explanation}
    
    CWE: {cwe}
    """
    
        
    return f"""
    You are a security researcher tasked with identifying vulnerabilities in a codebase. You have been given a function to analyze. 
    The function may or may not be vulnerable
    
    If you think it is vulnerable reply with @@VULNERABLE@@, otherwise reply with @@NOT VULNERABLE@@
    
    If you think the function is vulnerable, please provide the CWE number that you think is most relevant to the vulnerability in the form of @@CWE: <CWE_NUMBER>@@
    
    For example:
    
    @@VULNERABLE@@
    @@CWE: CWE-1234@@
    
    Here is the function:
    
    ```c
    {function_body}
    ```
    
    example detections:
    
    {examples}     
    
    Solve this problem step by step. Carefully break down the reasoning process to arrive at the correct solution. Explain your reasoning at each step before providing the final answer.
    """