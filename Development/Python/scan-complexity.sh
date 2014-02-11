#!/bin/bash

for filename in $( find -name "*.py" ); do
    echo "$filename"
    python -m mccabe --min 10 "$filename"
    echo
done
