#!/bin/bash

if [ ! -d "logs" ]; then
    mkdir logs
    pushd logs || exit
fi
pushd logs || exit
if [ ! -d "monitor" ]; then
        mkdir monitor
fi
pushd monitor || exit

numFiles="$(find . -maxdepth 1 -type f | wc -l)"
oldMainFile="./glances$numFiles.csv"
for file in ./*.csv; do
    file="${file:2}"
    if [[ "$file" == "glances.csv" ]]; then
        mv "$file" "$oldMainFile"
    fi
done
popd || exit
popd || exit

python3 monitor.py &
python3 app.py