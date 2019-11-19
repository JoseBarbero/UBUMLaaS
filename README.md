# UBUMLaaS [![admirable-logo](ubumlaas/static/img/onlyA-32x32.svg)](http://admirable-ubu.es/)


[![Travis (.org)](https://img.shields.io/travis/JoseBarbero/UBUMLaaS/master.svg?label=Travis%20CI&logo=travis-ci&logoColor=white&style=for-the-badge)](https://travis-ci.org/JoseBarbero/UBUMLaaS)
[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/JoseBarbero/UBUMLaaS?logo=code-climate&style=for-the-badge)](https://codeclimate.com/github/JoseBarbero/UBUMLaaS)
[![GitHub repo size](https://img.shields.io/github/repo-size/JoseBarbero/UBUMLaaS?color=yellowgreen&logo=github&style=for-the-badge)](https://github.com/JoseBarbero/UBUMLaaS/archive/master.zip)
[![GitHub](https://img.shields.io/github/license/JoseBarbero/UBUMLaaS?logo=gnu&logoColor=white&style=for-the-badge)](https://github.com/JoseBarbero/UBUMLaaS/blob/master/LICENSE)

Machine Learning as a Service (MLaaS) platform based on [ADMIRABLE](http://admirable-ubu.es/) and [BEST-AI](https://www.ubu.es/best-ai-biologia-educacion-y-salud-con-tecnologias-avanzadas-informaticas-best-ai) research groups methods.

---
This application is described as one of the result of two different projects (with objectives partially overlapping, and being this application in the intersection of the objectives):

1. <a href="http://www.mineco.gob.es/portal/site/mineco/"><img align="right" width="20%" src="ubumlaas/static/img/MEC.svg"></a>
Project "***Algoritmos de ensembles para problemas de salidas múltiples - nuevos desarrollos y aplicaciones***" from "*Ministerio de Economía y Competitividad*" (reference: TIN2015-67534-P)
2. <a href="https://www.jcyl.es/"><img align="right" width="20%" src="ubumlaas/static/img/JCYL.svg"></a>
Project "***Minería de datos para la mejora del mantenimiento y disponibilidad de máquinas de altas presiones***" from *"Consejería de Educación de la Junta de Castilla y León"* (reference: BU085P17)

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
    export FLASK_ENV=development #development or production
    LIBFOLDER=/absolute/path/to/UBUMLaaS
    ```
6. With the conda environment UBUMLaaS, execute the script to export environment variables when activate conda env.
    ```bash
    $ source env_vars_to_conda.sh
    ```
7. Create database
    ```bash
    $ mv data_base.sqlite ubumlaas/data.sqlite
    ```
    *Opt:* 
    Download a database and put it in ./ubumlaas/
8. Install Redis-Server
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
## Update database
1. Execute migrate.py
   ```bash
   $ python migrate.py
   ``` 


---

<a href="https://ec.europa.eu/regional_policy/es/funding/erdf/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/FEDER.svg"></a>
<a href="http://www.mineco.gob.es/portal/site/mineco/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/MEC.svg"></a>
<a href="https://www.jcyl.es/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/JCYL.svg"></a>
<a href="https://www.educa.jcyl.es/universidad/es/fondos-europeos/fondo-europeo-desarrollo-regional-feder/"><img hspace="2%" align="center" width="20%" src="ubumlaas/static/img/JCYL_impulsa.svg"></a>

        
