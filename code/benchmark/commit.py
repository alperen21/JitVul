import json
from clone import Cloner
from tqdm.auto import tqdm
import os
from agent import Agent

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def find_vulnerability_introducing_commit(cloner, vulnerable_function, vulnerable_file, vulnerability_fixing_commit):
    cloner.checkout_to_vulnerable(vulnerability_fixing_commit)
    file_contents = read_file(vulnerable_file)
    
    while vulnerable_function in file_contents:
        cloner.go_back_one_commit()
        
        try:
            if not os.path.exists(vulnerable_file):
                return cloner.get_current_commit_id()
            file_contents = read_file(vulnerable_file)
        except Exception:
            return cloner.get_current_commit_id()
        
    return cloner.get_current_commit_id()
    

def find_files(directory, file_name):
    matches = []
    for root, _, files in os.walk(directory):
        if file_name in files:
            matches.append(os.path.join(root, file_name))
    return matches

def find_file(file_name, function_body):
    repo_path = os.path.join('./projects/repo')
    file_paths = find_files(repo_path, file_name)
    
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        
        if check_if_function_exists(file_contents, function_body):
            return file_path

def check_if_function_exists(file_contents, function_body):
    return ''.join(function_body.split()) in ''.join(file_contents.split())

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_unique_cwes(data):
    unique_cwes = set()
    for item in data:
        if "cwe" in item:
                if item["cwe"] not in (['NVD-CWE-noinfo'], ['NVD-CWE-Other'], []):
                                unique_cwes.add(tuple(item["cwe"]))
    return unique_cwes
    
def sample_data(data, unique_cwes):
    sampled_data = []
    cwe_count = {}
    data = [item for item in data if 'linux' not in item['project'].lower() and 'imagemagick' not in item['project'].lower()]
    for item in data:
        if "cwe" in item:
            cwe_tuple = tuple(item["cwe"])
            if cwe_tuple in unique_cwes:
                if cwe_tuple not in cwe_count:
                    cwe_count[cwe_tuple] = 0
                if cwe_count[cwe_tuple] < 3:
                    sampled_data.append(item)
                    cwe_count[cwe_tuple] += 1
    return sampled_data

def preprocess_data(data):
    unique_cwes = set()
    for item in data:
        if "cwe" in item:
            unique_cwes.add(tuple(item["cwe"]))
            
            
    

    filtered_data = [item for item in data if item.get('target') == 1]
    unique_cwes = get_unique_cwes(filtered_data)
    filtered_data = sample_data(filtered_data, unique_cwes)
    
    return filtered_data

def append_to_jsonl(file_path, data):
    with open(file_path, 'a') as file:
        for item in data:
            file.write(json.dumps(item) + '\n')

def main():
    cloner = Cloner() 
    
    mapping = load_json('./mapping.json')
    # Load the jsonl file 
    data = load_jsonl('./functional/primevul_test.jsonl') + load_jsonl('./functional/primevul_train.jsonl') + load_jsonl('./functional/primevul_valid.jsonl')
    # Process the data
    data = preprocess_data(data)
    # For each repository
    for item in tqdm(data):
        cloner.remove_repo()
        # Gather the vulnerability fixing commit 
        if item['project'] not in mapping.keys():
            continue
        url = mapping[item['project']]
        
        item['vulnerability_fixing_commit_id'] = item.pop('commit_id')
        item['vulnerability_fixing_commit_url'] = item.pop('commit_url')
        item['vulnerability_fixing_commit_message'] = item.pop('commit_message')
        
        # Clone the repository
        cloner.clone(url)
        
        # Check out to vulnerable version 
        cloner.checkout_to_vulnerable(item['vulnerability_fixing_commit_id'])
        
        item['vulnerable_commit_id'] = cloner.get_current_commit_id()
        item['vulnerable_commit_message'] = cloner.get_current_commit_message()
        item['vulnerable_commit_url'] = cloner.get_current_commit_url()
        
        # Extract the function 

        function_body = item["func"]
        
        vulnerable_file = find_file(item['file_name'], function_body)
        
        if vulnerable_file is None:
            continue
        vulnerable_file = vulnerable_file.replace('./projects/repo/', '')
        item['file_name'] = vulnerable_file
        
        # Find the vulnerability introducing commit

        vulnerability_introducing_commit = find_vulnerability_introducing_commit(cloner, function_body, os.path.join("./projects/repo/",vulnerable_file), item['vulnerable_commit_id'])
        cloner.checkout(vulnerability_introducing_commit)
        item['vulnerability_introducing_commit_id'] = cloner.get_current_commit_id()
        item['vulnerability_introducing_commit_message'] = cloner.get_current_commit_message()
        item['vulnerability_introducing_commit_url'] = cloner.get_current_commit_url()

        cloner.checkout(item['vulnerability_fixing_commit_id'])
        agent = Agent()
        non_vulnerable_version = agent.find_other_version(function_body, read_file(os.path.join('./projects/repo/',vulnerable_file)))
        
        item['vulnerable_function_body'] = item.pop('func')
        item["non_vulnerable_function_body"] = non_vulnerable_version
        # Append the data to the jsonl file
        append_to_jsonl('new_benchmark.jsonl', [item])
        
        
        
        
        
    

if __name__ == '__main__':
    main()