# UBUMLaaS ![admirable-logo](ubumlaas/static/img/onlyA-32x32.svg)


[![Travis (.org)](https://img.shields.io/travis/JoseBarbero/UBUMLaaS?label=Travis%20CI&logo=travis-ci&logoColor=white&style=for-the-badge)](https://travis-ci.org/JoseBarbero/UBUMLaaS)
[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/JoseBarbero/UBUMLaaS?logo=code-climate&style=for-the-badge)](https://codeclimate.com/github/JoseBarbero/UBUMLaaS)
[![GitHub repo size](https://img.shields.io/github/repo-size/JoseBarbero/UBUMLaaS?color=yellowgreen&logo=github&style=for-the-badge)](https://github.com/JoseBarbero/UBUMLaaS/archive/master.zip)
[![GitHub](https://img.shields.io/github/license/JoseBarbero/UBUMLaaS?logo=gnu&logoColor=white&style=for-the-badge)](https://github.com/JoseBarbero/UBUMLaaS/blob/master/LICENSE)

MLaaS platform based on ADMIRABLE and BEST-AI research groups methods.
#### Platform from Spanish "Ministerio de Economía y Competitividad" Project "*Algoritmos de ensembles para problemas de salidas múltiples - nuevos desarrollos y aplicaciones*"

---
## Installation (Linux)

1. Clone this repository
    ```bash
    $ git clone https://github.com/JoseBarbero/UBUMLaaS.git
    ```
2. Go to UBUMLaaS repository's folder
    ```bash
    $ cd UBUMLaaS
    ```
3. Create a conda environment
    ```bash
    $ conda env create -f UBUMLaaS_env.yml
    ```
4. Activate environment
    ```bash
    $ conda activate UBUMLaaS
    ```
5. Modify **env_variables.sh** with properly values
    ```bash 
    export SECRET_KEY=<app secret key>
    export EMAIL_AC=<email>
    export EMAIL_PASS=<email-password>
    LIBFOLDER=/absolute/path/to/UBUMLaaS
    ```
6. With the conda environment UBUMLaaS, execute the script to export environment variables when activate conda env.
    ```bash
    $ bash env_vars_to_conda.sh
    ```
7. Deactivate and activate conda environment to take effect.
    ```bash
    $ conda deactivate
    $ conda activate UBUMLaaS
    ```
8. Create database
    ```bash
    $ mv data_base.sqlite ubumlaas/data.sqlite
    ```
    *Opt:* 
    Download a database and put it in ./ubumlaas/
9. Install Redis-Server
    ```bash
    $ sudo apt install redis-server
    $ sudo service redis-server start
    $ sudo systemctl enable redis-server #If you want to initialize the service in startup
    ```
    *Caution*: Close all workers of RQ before stop redis-server

## Execution
1. Inside the UBUMLaaS repository's folder, activate conda environment if not activated.
    ```bash
    $ conda activate UBUMLaaS
    ```
2.  Execute to run the server
    ```bash
    python app.py
    ```

---

<a href="https://ec.europa.eu/regional_policy/es/funding/erdf/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/FEDER.svg"></a>
<a href="http://www.mineco.gob.es/portal/site/mineco/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/MEC.svg"></a>
<a href="https://www.jcyl.es/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/JCYL.svg"></a>
<a href="https://www.educa.jcyl.es/universidad/es/fondos-europeos/fondo-europeo-desarrollo-regional-feder/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/JCYL_impulsa.svg"></a>

        
