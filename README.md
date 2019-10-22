# UBUMLaaS ![admirable-logo](ubumlaas/static/img/onlyA-32x32.svg)
MLaaS platform based on ADMIRABLE and BEST-AI research groups methods.
#### Platform from Spanish "Ministerio de Economía y Competetividad" Project "*Algoritmos de ensembles para problemas de salidas múltiples - nuevos desarrollos y aplicaciones*"

---
## Installation

1. Clone this repository
    ```bash
    $ git clone https://github.com/JoseBarbero/UBUMLaaS.git
    ```
2. Create a conda environment
    ```bash
    $ conda create -n UBUMLaas python=3.6
    ```
3. Activate environment
    ```bash
    $ conda activate UBUMLaaS
    ```
4. Go to UBUMLaaS repository's folder
    ```bash
    $ cd UBUMLaaS
    ```
5. Install requeriments
    ```bash
    $ pip install -r requeriments.txt
    ```
6. Create database
    ```bash
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    ```
    *Opt:* 
    Download a database and put it in ./ubumlaas/
7. Create environments variables
    ```bash
    #!/bin/bash

    export SECRET_KEY=dev
    export EMAIL_AC=<email>
    export EMAIL_PASS=<email-password>
    LIBFOLDER=.
    export WEKA_HOME=$LIBFOLDER/lib/wekafiles/packages/

    ruta="$WEKA_HOME/packages/"
    packages=$(ls -l $ruta)

    pack=()
    IFS=$'\n'
    #rev |cut -d" " -f1 | rev
    for p in $packages; do
        
        first=$(echo $p | cut -f1 -d" " | head -c 1)
        if [ $first == "d" ]; then
            pack=("${pack[@]}" $(echo $p | rev |cut -d" " -f1 | rev))
        fi
    done

    _res=""
    for (( i=0; i<${#pack[@]}; i++ ))
    do
        _res="$ruta${pack[$i]}/${pack[$i]}.jar:$_res"
    done

    export MEKA_CLASSPATH="$_res$LIBFOLDER/lib/scikit_ml_learn_data/meka/meka-release-1.9.2/lib/"
    ```
8. Install Redis-Server
    ```bash
    $ sudo apt install redis-server
    $ sudo service redis-server start
    $ sudo systemctl enable redis-server #If you want to initialize the service in startup
    ```
    *Caution*: Close all workers of RQ before stop redis-server
9.  Execute
    ```bash
    python app.py
    ```

---
<p align="center">
<img align="center" width="20%" src="ubumlaas/static/img/FEDER.svg">
<img align="center" width="20%" src="ubumlaas/static/img/MEC.svg">
<img align="center" width="20%" src="ubumlaas/static/img/JCYL.svg">
<img align="center" width="20%" src="ubumlaas/static/img/JCYL_impulsa.svg">
</p>
        
