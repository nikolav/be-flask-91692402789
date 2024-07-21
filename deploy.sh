#!/bin/bash

if [ -e "./wserver.sh" ]; then
  chmod 755 ./wserver.sh
fi

docker compose up -d --build api


# docker exec -it api python script.py
