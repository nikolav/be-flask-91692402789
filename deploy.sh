#!/bin/bash

WSERVER="./wserver.sh"

#  exe server script
if [ -e "$WSERVER" ]; then
  chmod 755 $WSERVER
fi

docker compose up -d --build api


# docker exec -it api python script.py
