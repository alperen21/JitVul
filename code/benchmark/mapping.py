import json

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data


data = load_jsonl('./functional/primevul_test.jsonl') + load_jsonl('./functional/primevul_train.jsonl') + load_jsonl('./functional/primevul_valid.jsonl')
print(data[1000]["file_name"])