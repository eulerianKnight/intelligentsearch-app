#!/bin/bash

# If DOCKER_MACHINE_IP is not set, you need to set it manually before running docker-compose up
export DOCKER_GATEWAY_HOST=172.17.0.1

echo "**********************************************************************"
echo "**********************************************************************"
echo "Browse to http://${DOCKER_GATEWAY_HOST}:9200/info to check Elastic status"
echo "**********************************************************************"
echo "**********************************************************************"


docker compose up -d