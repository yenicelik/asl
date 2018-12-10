# Install common scripts
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:openjdk-r/ppa
sudo apt-get update
sudo apt-get install -y memcached git unzip ant openjdk-7-jdk
sudo apt-get install -y git unzip
sudo apt-get install -y wget

# Installing the memtier_benchmark
wget https://github.com/RedisLabs/memtier_benchmark/archive/master.zip
unzip master.zip
cd memtier_benchmark-master
sudo apt-get install -y build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev
autoreconf -ivf
./configure
sudo make
sudo make install
sudo apt-get install -y iputils-ping
sudo apt-get install -y dstat

# Stop the memcached service
sudo service memcached stop

# Setup correct permissions
# sudo chmod -R 7777 /home/yedavid/
# sudo chmod -R 700 /home/yedavid/.ssh/
# sudo chmod -R 600 /home/yedavid/.ssh/authorized_keys
