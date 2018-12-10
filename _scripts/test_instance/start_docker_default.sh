#!/bin/bash
bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh

clear
# "docker exec " + container + " " + bashcommand

PORT=13433

# Server setup (Memcached)
SERVER_ID=`docker run -it -d --network='host' --privileged aslyedavid`
echo "server id is: $SERVER_ID"

# Starting the memtier server
echo "starting memcached..."
docker exec $SERVER_ID memcached -u root -t 1 -p $PORT &
MEMTIER_PID=$!
echo "id of the memtier server: $MEMTIER_PID"


# Client setup
CLIENT_ID=`docker run -it -d --network='host' --privileged aslyedavid`
echo "client id is: $SERVER_ID"

# Starting the memtier server
echo "starting memcached..."

docker exec $CLIENT_ID \
memtier_benchmark -s localhost -p $PORT \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=3 --ratio=1:1 \
--expiry-range=9999-10000 --key-maximum=1000 \

kill $MEMTIER_PID

bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh
