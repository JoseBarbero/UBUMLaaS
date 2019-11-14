#!/bin/bash

export SECRET_KEY=<app secret key>
export EMAIL_AC=<email>
export EMAIL_PASS=<email-password>
export FLASK_ENV=development #development or production
LIBFOLDER=/absolute/path/to/UBUMLaaS

export WEKA_HOME=$LIBFOLDER/lib/wekafiles/packages/

ruta="$WEKA_HOME/packages/"
packages=$(ls -l $ruta)

pack=()
IFS=$'\n'       # make newlines the only separator
#rev |cut -d" " -f1 | rev
for p in $packages; do
    
    first=$(echo $p | cut -f1 -d" " | head -c 1)
    if [ $first == "d" ]; then
        pack=("${pack[@]}" $(echo $p | rev |cut -d" " -f1 | rev))
    fi
done

____res=""
for (( i=0; i<${#pack[@]}; i++ ))
do
    ____res="$ruta${pack[$i]}/${pack[$i]}.jar:$____res"
done

export MEKA_CLASSPATH="$____res$LIBFOLDER/lib/scikit_ml_learn_data/meka/meka-release-1.9.2/lib/"