# UBUMLaaS [![admirable-logo](ubumlaas/static/img/onlyA-32x32.svg)](http://admirable-ubu.es/)

<div align="center">
    <img alt="Codacy grade" src="https://img.shields.io/codacy/grade/5380c6229bc5421ba4832902f9e359fa?logo=codacy">
    <img alt="SonarCloud Build Status" src="https://sonarcloud.io/api/project_badges/measure?project=dpr1005_UBUMLaaS&metric=alert_status">
    <img alt="SonarCloud Mantainability" src="https://sonarcloud.io/api/project_badges/measure?project=dpr1005_UBUMLaaS&metric=sqale_rating">
    <img alt="SonarCloud Vulneravilities" src="https://sonarcloud.io/api/project_badges/measure?project=dpr1005_UBUMLaaS&metric=vulnerabilities">
    <br/>
    <a href="https://github.com/dpr1005/UBUMLaaS/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/dpr1005/UBUMLaaS"></a>
<a href="https://github.com/dpr1005/UBUMLaaS/network/members"><img alt="GitHub forks" src="https://img.shields.io/github/forks/dpr1005/UBUMLaaS"></a>
<a href="https://github.com/dpr1005/UBUMLaaS/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/dpr1005/UBUMLaaS"></a>
<img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/dpr1005/UBUMLaaS">
  <a href="https://github.com/dpr1005/UBUMLaaS/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/dpr1005/UBUMLaaS"></a>
    <br/>
    <img alt="Non Comment Lines Of Code" src="https://sonarcloud.io/api/project_badges/measure?project=dpr1005_UBUMLaaS&metric=ncloc">
    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/dpr1005/UBUMLaaS?color=purple&logo=github">
</div>
    
---
<div align="justify">
This application is the continuation of <a href="https://github.com/JoseBarbero/UBUMLaaS">UBUMLaaS</a> developed by the ADMIRABLE research group of the University of Burgos.

This new version provides support for Semi-Supervised Learning algorithms and new instance selection filters.

It also has a renewed and modernized interface. With a whole new administration section of the application itself, with statistics for users and general system statistics.

Machine Learning as a Service (MLaaS) platform based on [ADMIRABLE](http://admirable-ubu.es/) and [BEST-AI](https://www.ubu.es/best-ai-biologia-educacion-y-salud-con-tecnologias-avanzadas-informaticas-best-ai) research groups methods.
</div>
<br>

---
## Installation (Linux)

1. Clone this repository
    ```bash
    $ git clone https://github.com/dpr1005/UBUMLaaS.git
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
    export EMAIL_URL=<email-url>
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
    ./run.sh
    ```
    Remember to give the required permissions in case they are needed.
## Update database
1. Execute migrate.py
   ```bash
   $ python migrate.py
   ``` 


---

> GitHub [@dpr1005](https://github.com/dpr1005) &nbsp;&middot;&nbsp;
> Twitter [@callmednx](https://twitter.com/callmednx) &nbsp;&middot;&nbsp;
> LinkedIn [Daniel Puente Ramírez](https://www.linkedin.com/in/danielpuenteramirez/)

        
