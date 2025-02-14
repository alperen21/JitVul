from tqdm import tqdm
import subprocess
import platform
from collections import defaultdict
from pprint import pprint
import re
import os
from agent import Agent
import json
from clone import Cloner

repo_path = os.path.join(".","projects", "repo")

def extract_function_name(function_body: str) -> str:
    """
    Extract the function name from a given C/C++ function body, excluding keywords like 'static'.
    
    :param function_body: The string containing the C/C++ function body.
    :return: The extracted function name or None if no valid function name is found.
    """
    # Regex to match function definitions, avoiding keywords like 'static'
    pattern = r'\b(?:[a-zA-Z_]\w*\s+)*([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{'
    
    # Search for the pattern in the function body
    match = re.search(pattern, function_body)
    if match:
        return match.group(1)  # The function name is captured in the first group
    return None


def extract_all_function_names(input_text: str) -> list:
    """
    Extract all function names from the input text.
    
    :param input_text: The string containing the function definitions and calls.
    :return: A list of all unique function names found in the text.
    """
    # Use a regex to match function names followed by '()'
    function_names = re.findall(r'\b(\w+)\s*\(\)', input_text)
    
    # Return unique function names while maintaining order
    return list(dict.fromkeys(function_names))


def extract_call_hierarchy(input_text: str) -> dict:
    """
    Extract the call hierarchy from the input text and return it as a dictionary.
    
    :param input_text: The string containing the function definitions and their nested calls.
    :return: A dictionary representing the call hierarchy.
    """
    lines = input_text.splitlines()
    call_hierarchy = defaultdict(lambda: {"callers": []})
    stack = []
    current_function = None

    for line in lines:
        # Determine the current line's indentation
        stripped_line = line.strip()
        if not stripped_line:
            continue
        indentation = len(line) - len(stripped_line)
        
        # Check if the line represents a function definition
        if "()" in stripped_line and ":" in stripped_line:
            function_name = stripped_line.split("()")[0].strip()
            
            # Add the function to the hierarchy if not already present
            if function_name not in call_hierarchy:
                call_hierarchy[function_name] = {"callers": []}
            
            # Handle nested function calls
            if stack and indentation > stack[-1][1]:
                parent_function = stack[-1][0]
                call_hierarchy[parent_function]["callers"].append(function_name)
            
            # Update the current function and push to stack
            current_function = function_name
            stack.append((current_function, indentation))
        
        elif current_function and indentation > stack[-1][1]:
            # This line represents a function being called
            called_function = stripped_line.split("()")[0].strip()
            call_hierarchy[current_function]["callers"].append(called_function)
        else:
            # Pop the stack when indentation decreases
            while stack and stack[-1][1] >= indentation:
                stack.pop()
            if stack:
                current_function = stack[-1][0]
            else:
                current_function = None

    return dict(call_hierarchy)



def extract_function_block(input_text: str, function_name: str) -> str:
    """
    Extract the code block associated with a given function name from the input text.

    :param input_text: The string containing the function definitions and their contents.
    :param function_name: The name of the function to extract.
    :return: A string containing the function definition and its block, or an empty string if not found.
    """
    lines = input_text.splitlines()
    result = []
    inside_function = False
    indentation_level = None

    for line in lines:
        # Check if this line contains the desired function
        if line.strip().startswith(function_name + "()"):
            result.append(line)
            inside_function = True
            # Capture the base indentation level of the function definition
            indentation_level = len(line) - len(line.lstrip())
        elif inside_function:
            # Determine the indentation level of the current line
            current_indentation = len(line) - len(line.lstrip())
            # If the line is less indented or empty, exit the function block
            if line.strip() == "" or current_indentation <= indentation_level:
                break
            result.append(line)

    return "\n".join(result)


def create_c_tags(repo_path):
    command = f"cd {repo_path} && ctags -R .                             "
    if platform.system() == 'Darwin':
        command = "alias ctags=\"`brew --prefix`/bin/ctags\" && " + command
    
    process = subprocess.run(command, shell=True)
    
    if process.returncode != 0:
        raise Exception("Failed to create ctags")
    

def find_callees(file_path, function_name):
    global repo_path
    file_path = os.path.join(repo_path, file_path)
    process = subprocess.run(f"cflow {file_path}", shell=True, capture_output=True, text=True)
    output = process.stdout
    
    if process.returncode != 0:
        raise Exception("Failed to find callees" + process.stderr)
    
    function_block = extract_function_block(output, function_name)
    callee_graph = extract_call_hierarchy(function_block)
    return callee_graph

def find_callers(file_path, function_name):
    global repo_path
    file_path = os.path.join(repo_path, file_path)
    process = subprocess.run(f"cflow --reverse {file_path}", shell=True, capture_output=True, text=True)
    output = process.stdout
    
    if process.returncode != 0:
        raise Exception("Failed to find callees: ", process.stderr)
    
    function_block = extract_function_block(output, function_name)
    callee_graph = extract_call_hierarchy(function_block)
    return callee_graph
def get_filenames_for_function(input_text: str, function_name: str) -> list:
    """
    Extract filenames corresponding to a given function name from the input text.
    
    :param input_text: The string containing function names and their file paths.
    :param function_name: The name of the function to search for.
    :return: A list of filenames associated with the function name.
    """
    lines = input_text.splitlines()
    filenames = []

    for line in lines:
        # Split the line into components
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].strip() == function_name:
            filenames.append(parts[1].strip())

    return filenames

def extract_function_body(code, function_name):
    """
    Extract the body (including the outer braces) of a C/C++ function
    called `function_name` from the file at `file_path`.

    :param file_path: Path to the file containing the C/C++ code
    :param function_name: Name of the function to extract
    :return: A string of the function body (with braces), or None if not found
    """
    # Read the entire file as a single string

    # -------------------------------------------------------
    # 1) Find the start of the function definition:
    #    A simplified pattern that searches for:
    #      - some return type (or qualifiers/whitespace) 
    #      - the function name as a whole word
    #      - an argument list in parentheses
    #      - an opening brace '{'
    #
    #    Note: This regex is naive and can miss or mis-capture some forms,
    #          e.g. function pointers, macros, multiline definitions, etc.
    # -------------------------------------------------------
    pattern = re.compile(
        # Optional return type and qualifiers (e.g., 'static inline void')
        r'(?:[\w:\*\s]+)?'
        # Word boundary + function name + possible whitespace
        rf'\b{function_name}\b\s*'
        # Parentheses for argument list (not matching nested parentheses)
        r'\([^)]*\)\s*'
        # The opening brace
        r'\{'
    )

    match = pattern.search(code)
    if not match:
        # Could not find a function definition matching the pattern
        return None

    # -------------------------------------------------------
    # 2) Collect braces until they balance.
    #    We know `match.end()` points at the first character 
    #    AFTER the '{' matched by our regex, so we backtrack by 1 
    #    to start reading from the actual '{'.
    # -------------------------------------------------------
    start_index = match.end() - 1

    braces = 0
    function_body = []
    in_function = False

    for i in range(start_index, len(code)):
        char = code[i]
        function_body.append(char)

        if char == '{':
            # If this is our first '{', we start counting
            braces += 1
            in_function = True
        elif char == '}':
            braces -= 1

        if in_function and braces == 0:
            # We've just closed the outermost brace
            break

    # Join the captured characters into a string
    return ''.join(function_body) if function_body else None



def extract_function_bodies(file_path, start_function):
    global repo_path
    file_path = os.path.join(repo_path, file_path)  
    callee_process = subprocess.run(f"cflow --reverse {file_path}", shell=True, capture_output=True, text=True)
    
    if callee_process.returncode != 0:
        raise Exception("Failed to find callees")
    callers_process = subprocess.run(f"cflow {file_path}", shell=True, capture_output=True, text=True)
    
    if callers_process.returncode != 0:
        raise Exception("Failed to find callees")
    
    functions = extract_all_function_names(extract_function_block(callee_process.stdout, start_function)) + extract_all_function_names(extract_function_block(callers_process.stdout, start_function))
    
    create_c_tags(repo_path)
    
    ctags_path = os.path.join(repo_path, "tags")
    
    with open(ctags_path, 'r', encoding='latin-1') as file:
        ctags_content = file.read()
    
    # test = get_filenames_for_function(ctags_content, start_function)
    
    function_bodies = dict()
    for function in tqdm(functions):
        file_names = get_filenames_for_function(ctags_content, function)
        for file_name in file_names:
            with open(os.path.join(repo_path, file_name), 'r') as file:
                file_content = file.read()
            
            function_body = extract_function_body(file_content, function)#agent.extract_function(file_content, function)
            
            if function_body != "#NOT_FOUND#":
                function_bodies[function] = function_body     
            
    return function_bodies

def read_jsonl_file(file_path: str) -> list:
    """
    Read a JSONL (JSON Lines) file and return a list of dictionaries.

    :param file_path: The path to the JSONL file.
    :return: A list of dictionaries, each representing a JSON object from the file.
    """

    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))
    
    return data

def read_json_file(file_path: str) -> dict:
    """
    Read a JSON file and return its contents as a dictionary.

    :param file_path: The path to the JSON file.
    :return: A dictionary representing the JSON object from the file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data


if __name__ == '__main__':
    # caller_graph = find_callers('php-src/main/fastcgi.c', 'fcgi_init_request')  
    # callees_graph = find_callees('php-src/main/fastcgi.c', 'fcgi_init_request')
    # function_bodies = extract_function_bodies('php-src/main/fastcgi.c', 'fcgi_init_request')
    
    
    benchmark = read_jsonl_file("./new_benchmark.jsonl")
    mapping = read_json_file("./mapping.json")
    
    cloner = Cloner()
    
    for entry in tqdm(benchmark):
        cloner.remove_repo()
        url = entry['commit_url']
        file_name = entry['file_name']
        cloner.clone(url)
        
        vulnerability_fixing_commit = entry["vulnerability_fixing_commit_id"]
        cloner.checkout(vulnerability_fixing_commit)
        non_vulnerable_function_body = entry["non_vulnerable_function_body"]
        
        non_vulnerable_function_name = extract_function_name(non_vulnerable_function_body)
        entry["non_vulnerable_caller_graph"] = find_callers(file_name, non_vulnerable_function_name)  
        entry["non_vulnerable_callee_graph"] = find_callees(file_name, non_vulnerable_function_name)  
        entry["non_vulnerable_function_bodies"] = extract_function_bodies(file_name, non_vulnerable_function_name)
        
        vulnerability_introducing_commit = entry["vulnerability_introducing_commit_id"]
        cloner.checkout(vulnerability_introducing_commit)
        vulnerable_function_body = entry["non_vulnerable_function_body"]
        
        vulnerable_function_name = extract_function_name(vulnerable_function_body)
        entry["vulnerable_caller_graph"] = find_callers(file_name, vulnerable_function_name)  
        entry["vulnerable_callee_graph"] = find_callees(file_name, vulnerable_function_name)  
        entry["vulnerable_function_bodies"] = extract_function_bodies(file_name, vulnerable_function_name)
        
        with open("final_benchmark.jsonl", 'a') as file:
            file.write(json.dumps(entry) + "\n")

        
    print("done")


        
        
        
        
        
        
        

