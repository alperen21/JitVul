#!/bin/bash

# Check if env.py exists
if [ ! -f "env.py" ]; then
    echo "env.py does not exist."
    echo "Please create env.py and place your OPENAI key there."
    exit 1
else
    echo "env.py exists."
fi

# Define models and prompts
models=("gpt-4o" "gpt-4o-mini" "ollama")
prompts=("prompt" "cot" "few-shot" "few-shot-cot")

# Loop through models and prompts for ReAct
for model in "${models[@]}"; do
    for prompt in "${prompts[@]}"; do
        log_file="${model}_${prompt}.log"
        python main.py --llm "$model" --temp 0 --prompt "$prompt" | tee "$log_file"
    done
done
