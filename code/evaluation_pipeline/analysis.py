import json
import subprocess
from tqdm import tqdm
import os

def load_final_benchmark(file_path):
    with open(file_path, 'r') as file:
        data = [json.loads(line) for line in file]
    return data

file_path = '/Users/alperen/Projects/evaluation_pipeline/final_benchmark.jsonl'
benchmark_data = load_final_benchmark(file_path)

print(benchmark_data[0].keys())

total_lines = 0
total_files = 0
for elem in tqdm(benchmark_data):
    try:
        # vulnerable_function_body = elem['vulnerable_function_body']
        # non_vulnerable_function_body = elem['non_vulnerable_function_body']
        
        # num_lines_vulnerable = len(vulnerable_function_body.split('\n'))
        # num_lines_non_vulnerable = len(non_vulnerable_function_body.split('\n'))
        
        # total_lines += num_lines_vulnerable + num_lines_non_vulnerable
        
        project_url = elem['project_url']
        vulnerability_fixing_commit_id = elem['vulnerability_fixing_commit_id']

        # Clone the repository
        repo_name = project_url.split('/')[-1].replace('.git', '')
        subprocess.run(['git', 'clone', project_url, repo_name])

        # Checkout to the specific commit
        os.chdir(repo_name)
        subprocess.run(['git', 'checkout', vulnerability_fixing_commit_id])

        # Count the number of code files
        code_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.py', '.java', '.js', '.cpp', '.c', '.h')):
                    code_files.append(os.path.join(root, file))
        num_code_files = len(code_files)

        # Change back to the original directory
        os.chdir('..')

        print(f"Number of code files in {repo_name}: {num_code_files}")
        
        vulnerability_introducing_commit_id = elem['vulnerability_introducing_commit_id']

        # Clone the repository again for the introducing commit
        subprocess.run(['git', 'clone', project_url, repo_name + '_introducing'])

        # Checkout to the specific introducing commit
        os.chdir(repo_name + '_introducing')
        subprocess.run(['git', 'checkout', vulnerability_introducing_commit_id])

        # Count the number of code files
        code_files_introducing = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.py', '.java', '.js', '.cpp', '.c', '.h')):
                    code_files_introducing.append(os.path.join(root, file))
        num_code_files_introducing = len(code_files_introducing)

        # Change back to the original directory
        os.chdir('..')

        print(f"Number of code files in {repo_name}_introducing: {num_code_files_introducing}")
        
        total_files += num_code_files + num_code_files_introducing
    
    except Exception as e:
        continue

# print(total_lines / len(benchmark_data)*2)
print(total_files / len(benchmark_data)*2)