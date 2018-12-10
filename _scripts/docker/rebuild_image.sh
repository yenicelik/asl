#!/bin/bash

docker build -t aslyedavid:latest .

# The following command should only be run if we spawn servers
docker run -it --name asl2 -d -p 5000:5000 --network="host" aslyedavid

# docker run -it --name asl3 -d -p 5000:5000 --network="host" aslyedavid
# docker exec -it cont_id /bin/bash
