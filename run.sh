#!/bin/bash

if [ ! -d "logs" ]; then
    $(mkdir logs)
    pushd logs 
fi
pushd logs
if [ ! -d "monitor" ]; then
        $(mkdir monitor)
fi
pushd monitor

numfiles=$(find . -maxdepth 1 -type f | wc -l)
oldMainFile="./glances$numfiles.csv"
for file in ./*.csv; do
    file="${file:2}"
    if [[ "$file" == "glances.csv" ]]; then
        $(mv $file $oldMainFile)
    fi
done
popd
popd

python3 monitor.py &
python3 app.py