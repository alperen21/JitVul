#!/bin/bash

if [ ! -d "functional" ]; then # check if functional dataset exists
    echo "please put functional dataset under functional to continue execution"
    exit 1
fi

python commit.py && # run benchmark generation
python callgraph.py # add call graph information

echo "done"