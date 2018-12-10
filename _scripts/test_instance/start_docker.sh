#!/bin/bash
bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh

clear
set -e

# Globals
PORT_MW=14432

# Setup docker containers
SERVER_ID1=`docker run -it -d --network='host' --privileged aslyedavid`
SERVER_ID2=`docker run -it -d --network='host' --privileged aslyedavid`
MW_ID=`docker run -it -d --network='host' -v /Users/david/asl-fall18-project/dist/middleware-yedavid.jar:/Users/david/asl-fall18-project/dist/middleware-yedavid.jar --privileged aslyedavid`
CLIENT_ID=`docker run -it -d --network='host' --privileged aslyedavid`

# Start memtier server
docker exec $SERVER_ID1 memcached -p 11211 -u root -t 1 &
MC_PID1=$!
echo "Started memcached server: $MC_PID1"
sleep 1

# Start memtier server
docker exec $SERVER_ID2 memcached -p 11212 -u root -t 1 &
MC_PID2=$!
echo "Started memcached server: $MC_PID2"
sleep 1

# Start the client
docker exec $CLIENT_ID \
memtier_benchmark --server=localhost --port=11211 \
--protocol=memcache_text --clients=1 --threads=1 \
--requests=15000 --ratio=1:0 \
--expiry-range=9999-10000 --key-maximum=10000 \
--data-size=4096 --multi-key-get=2 \
--key-pattern=S:S
MW_PID=$!
echo "Started the client: $CLIENT_PID"

#docker exec $CLIENT_ID \
#memtier_benchmark --server=localhost --port=11212 \
#--protocol=memcache_text --clients=1 --threads=1 \
#--test-time=5 --ratio=1:0 \
#--expiry-range=9999-10000 --key-maximum=1000 \
#--data-size=4096 --multi-key-get=2
#MW_PID=$!
#echo "Started the client: $CLIENT_PID"


# Build the middleware
cd /Users/david/asl-fall18-project/.
ant
# Start the middleware
docker exec $MW_ID \
java -jar \
/Users/david/asl-fall18-project/dist/middleware-yedavid.jar \
-l localhost \
-p $PORT_MW \
-m localhost:11211 \
-t 1 \
-s false &
MW_PID=$!
echo "Started middleware: $MW_PID"
sleep 1

# Start the client
# Causing the problem

docker exec $CLIENT_ID \
memtier_benchmark -s localhost -p $PORT_MW \
--protocol=memcache_text --clients=1 --threads=2 \
--test-time=10 --ratio=1:1 \
--data-size=4096 --expiry-range=9999-10000 --key-maximum=10000 \
--hide-histogram &
CLIENT_PID=$!
echo "Started the client: $CLIENT_PID$"

docker exec $CLIENT_ID \
memtier_benchmark --server=localhost --port=$PORT_MW \
--protocol=memcache_text --clients=32 --threads=2 \
--test-time=10 --ratio=1:1 \
--expiry-range=9999-10000 --key-maximum=10000 \
--data-size=4096 --multi-key-get=10 --hide-histogram
MW_PID=$!
echo "Started the client: $CLIENT_PID"

sleep 10

kill $SERVER_PID1
kill $SERVER_PID2
kill $MW_PID
kill $CLIENT_PID

bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh