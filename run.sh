#!/bin/bash
sudo docker run -d --env-file=deploy.env --restart=unless-stopped --name conn_monitor -it raccoon_conn_monitor:latest