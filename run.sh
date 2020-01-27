#!/bin/bash
sudo docker run -d --env-file=deploy.env -p 10044:10044 --restart=unless-stopped --name conn_monitor -it raccoon_conn_monitor:latest