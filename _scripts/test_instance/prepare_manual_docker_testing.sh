docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

docker network rm aslnetwork

PORT_MW=14432

docker network create aslnetwork

docker run --name='Server1' -it --rm -d --network='aslnetwork' --privileged aslyedavid
docker run --name='Server2' -it --rm -d --network='aslnetwork' --privileged aslyedavid
docker run --name='Server3' -it --rm -d --network='aslnetwork' --privileged aslyedavid

docker run --volume /Users/david/asl-fall18-project/dist/middleware-yedavid.jar:/Users/david/asl-fall18-project/dist/middleware-yedavid.jar --name='MW1' --rm -it -d --network='aslnetwork' --privileged aslyedavid
docker run --volume /Users/david/asl-fall18-project/dist/middleware-yedavid.jar:/Users/david/asl-fall18-project/dist/middleware-yedavid.jar --name='MW2' --rm -it -d --network='aslnetwork' --privileged aslyedavid

docker run --name='Client1' -it --rm -d --network='aslnetwork' --privileged aslyedavid
docker run --name='Client2' -it --rm -d --network='aslnetwork' --privileged aslyedavid
docker run --name='Client3' -it --rm -d --network='aslnetwork' --privileged aslyedavid


#################
# START SERVERS
#################
docker exec Server1 memcached -p 11211 -u root -t 1
docker exec Server2 memcached -p 11211 -u root -t 1
docker exec Server3 memcached -p 11211 -u root -t 1


##############
# PREPOPULATE
##############
docker exec Client1 memtier_benchmark --server=Server1 --port=11211 \
--protocol=memcache_text --clients=1 --threads=1 \
--requests=15000 --ratio=1:0 \
--expiry-range=9999-10000 --key-maximum=10000 \
--data-size=4096 --multi-key-get=2 \
--key-pattern=S:S --hide-histogram

docker exec Client2 memtier_benchmark --server=Server2 --port=11211 \
--protocol=memcache_text --clients=1 --threads=1 \
--requests=15000 --ratio=1:0 \
--expiry-range=9999-10000 --key-maximum=10000 \
--data-size=4096 --multi-key-get=2 \
--key-pattern=S:S --hide-histogram

docker exec Client3 memtier_benchmark --server=Server3 --port=11211 \
--protocol=memcache_text --clients=1 --threads=1 \
--requests=15000 --ratio=1:0 \
--expiry-range=9999-10000 --key-maximum=10000 \
--data-size=4096 --multi-key-get=2 \
--key-pattern=S:S --hide-histogram


##########################
# START MW
##########################
cd /Users/david/asl-fall18-project/. && \
ant && \
docker exec MW1 \
java -jar \
/Users/david/asl-fall18-project/dist/middleware-yedavid.jar \
-l 0.0.0.0 \
-p 14432 \
-t 1 \
-s true \
-m Server1:11211 Server2:11211 Server3:11211


cd /Users/david/asl-fall18-project/. && \
ant && \
docker exec MW2 \
java -jar \
/Users/david/asl-fall18-project/dist/middleware-yedavid.jar \
-l 0.0.0.0 \
-p 14432 \
-t 1 \
-s true \
-m Server1:11211 Server2:11211 Server3:11211

##########################
# START CLIENTS
##########################
docker exec Client1 \
memtier_benchmark -s MW1 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram

docker exec Client1 \
memtier_benchmark -s MW2 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram

docker exec Client2 \
memtier_benchmark -s MW1 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram

docker exec Client2 \
memtier_benchmark -s MW2 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram

docker exec Client3 \
memtier_benchmark -s MW1 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram

docker exec Client3 \
memtier_benchmark -s MW2 -p 14432 \
--protocol=memcache_text --clients=1 --threads=1 \
--test-time=30 --ratio=1:10 \
--expiry-range=9999-10000 --key-maximum=10000 --hide-histogram




#############
# Prepopulate
#############
docker stop Client1
docker stop Client2
docker stop Client3

docker exec MW1 pkill java
docker exec MW2 pkill java

docker exec Server1 pkill memcached
docker exec Server2 pkill memcached
docker exec Server3 pkill memcached
