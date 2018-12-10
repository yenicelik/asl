##!/bin/bash
#bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh
#

#
## Setup docker containers
#echo "Setting up containers..."
#SERVER_ID1=`docker run --name='Server1' -it -d --network='aslnetwork' --privileged aslyedavid`
#SERVER_ID2=`docker run --name='Server2' -it -d --network='aslnetwork' --privileged aslyedavid`
#MW_ID=`docker run --name='Middleware1' -it -d --network='aslnetwork' -v /Users/david/asl-fall18-project/dist/middleware-yedavid.jar:/Users/david/asl-fall18-project/dist/middleware-yedavid.jar --privileged aslyedavid`
#CLIENT_ID=`docker run --name='Client1' -it -d --network='aslnetwork' --privileged aslyedavid`
#
## Start memcached server
#docker exec $SERVER_ID1 memcached -p 11211 -u root -t 1 &
#MC_PID1=$!
#docker exec $SERVER_ID2 memcached -p 11212 -u root -t 1 &
#MC_PID2=$!
#echo "Started memcached server: $MC_PID1, $MC_PID2"
#sleep 1
#
##docker exec $CLIENT_ID \
##memtier_benchmark --server=Server1 --port=11211 \
##--protocol=memcache_text --clients=1 --threads=1 \
##--test-time=3 --ratio=0:1 \
##--expiry-range=9999-10000 --key-maximum=1000 --hide-histogram
##CLIENT_PID=$!
##echo "Started the client: $CLIENT_PID"
##
##docker exec $CLIENT_ID \
##memtier_benchmark --server=Server2 --port=11211 \
##--protocol=memcache_text --clients=1 --threads=1 \
##--test-time=1 --ratio=0:1 \
##--expiry-range=9999-10000 --key-maximum=1000 --hide-histogram
##CLIENT_PID=$!
##echo "Populated the servers!"
#
#
#
## Build the middleware
#cd /Users/david/asl-fall18-project/.
#ant
## Start the middleware
#docker exec $MW_ID \
#java -jar \
#/Users/david/asl-fall18-project/dist/middleware-yedavid.jar \
#-l localhost \
#-p $PORT_MW \
#-m Server1:11211 Server2:11212 \
#-t 1 \
#-s false &
#sleep 1
#
#MW_PID=$!
#echo "Started middleware: $MW_PID"
#sleep 1
#
#
#
#
#
## When ratio=1:9, it crashes (nullpointer exception)
## Start the client
#docker exec $CLIENT_ID \
#memtier_benchmark --server=localhost --port=$PORT_MW \
#--protocol=memcache_text --clients=1 --threads=1 \
#--test-time=1 --ratio=0:1 \
#--expiry-range=9999-10000 --key-maximum=1000 \
#--data-size=4096
#
##docker exec $CLIENT_ID \
##memtier_benchmark --server=localhost --port=$PORT_MW \
##--protocol=memcache_text --clients=1 --threads=1 \
##--test-time=1 --ratio=0:1 \
##--expiry-range=9999-10000 --key-maximum=1000 --hide-histogram \
##--data-size=10 --multi-key-get=10
#
##--multi-key-get=1
#
#CLIENT_PID=$!
#
#echo "Started the client: $CLIENT_PID"
#
#kill $MC_PID1
#kill $MC_PID2
#kill $MW_PID
#kill $CLIENT_PID
#
#bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh
#
#docker network rm aslnetwork


#!/bin/bash
bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh

clear
set -e

# Globals
PORT_MW=13432

# Create the docker network
docker network create aslnetwork

# Setup docker containers
SERVER_ID1=`docker run --name='Server1' -it -d --network='aslnetwork' --privileged aslyedavid`
#SERVER_ID2=`docker run --name='Server2' -it -d --network='aslnetwork' --privileged aslyedavid`
MW_ID=`docker run --name='Middleware1' -it -d --network='aslnetwork' -v /Users/david/asl-fall18-project/dist/middleware-yedavid.jar:/Users/david/asl-fall18-project/dist/middleware-yedavid.jar --privileged aslyedavid`
CLIENT_ID=`docker run --name='Client1' -it -d --network='aslnetwork' --privileged aslyedavid`

# Start memtier server
docker exec $SERVER_ID1 memcached -p 11211 -u root -t 1 &
MC_PID=$!
echo "Started memcached server: $MC_PID"
sleep 1

# Build the middleware
cd /Users/david/asl-fall18-project/.
ant
# Start the middleware
docker exec $MW_ID \
java -jar \
/Users/david/asl-fall18-project/dist/middleware-yedavid.jar \
-l $SERVER_ID1 \
-p $PORT_MW \
-m $SERVER_ID1:11211 \
-t 1 \
-s false &
MW_PID=$!
echo "Started middleware: $MW_PID"
sleep 1

# Start the client
docker exec $CLIENT_ID \
memtier_benchmark --server=$MW_ID --port=$PORT_MW \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=1 --ratio=0:1 \
--expiry-range=9999-10000 --key-maximum=1000 \
--data-size=4096
MW_PID=$!
echo "Started the client: $CLIENT_PID"

kill $SERVER_PID
kill $MW_PID
kill $CLIENT_PID

bash /Users/david/asl-fall18-project/_scripts/test_instance/stop_docker.sh