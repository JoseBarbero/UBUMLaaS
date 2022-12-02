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

if [ -f "glances.csv" ];
then
    echo "An old glances file has been found. Refactoring..."
    sed -i '1d' glances.csv
    echo >> glances_history.csv
    echo glances.csv | xargs cat >> glances_history.csv
    rm glances.csv
    sed -i '/^[[:space:]]*$/d' glances_history.csv
fi


popd || exit
popd || exit

python3 monitor.py &
python3 app.py '0.0.0.0' 8081