#!/bin/bash

sudo service redis-server stop
sudo apt-get purge --auto-remove -y redis-server
sudo apt-get install -y redis-server
sudo service redis-server start
rq info