"""
    This file includes all the commands that will be executed via ssh or docker exec later.
    Maybe this file should discrimate running the docker container vs. ssh'ing into the servers
"""
import os
from _scripts.config import CONFIG

# COPY LOGS TO LOCAL DIRECTORY
def copy_logs_to_local(ip, remote_logdir, local_logdir, logfile):

    q = "rsync -r azureuser@{}".format(ip)
    q += ":{} ".format(remote_logdir)
    q += "{} --progress".format(local_logdir)

    print("Copying using the following command: ", q)
    return q

def check_if_logdir_exists(logdir):
    print("Checking if logdir exists...")
    return "cd {} && ls -la".format(logdir)

# MISC
def remove_logdir(logdir):
    print("Removing logdir...")
    return "rm -rf {}".format(logdir)

def create_local_logdir(logdir):
    q = "mkdir -p {}".format(logdir)
    return q

def create_logdir(logdir):
    print("Creating logfile directory")
    print("Directory is: ", logdir)
    q = "mkdir -p {}".format(logdir) # && sudo chmod 777 -R {}
    return q

def create_logfile(logfile):
    print("Creating the logfile directory")
    q = "touch {} && echo '' >> {}".format(logfile, logfile)
    return q

def print_file_contents(file):
    print("Printing file contents!")
    q = "cat {}".format(file)
    return q

# BASIC TESTS
def test_if_there_is_output():
    return "echo Working"

# MEMTIER SPECIFIC
def memtier_get_requests(
        memcached_ip,
        port,
        virtual_clients_per_thread,
        logfile,
        threads,
        test_time,
        write_ratio,
        read_ratio):

    ratio = write_ratio + ":" + read_ratio

    q = "memtier_benchmark -s {} -p {} ".format(memcached_ip, port)
    q += "--protocol=memcache_text --clients={} --threads={} ".format(virtual_clients_per_thread, threads)
    q += "--test-time={} --ratio={} --data-size=4096 ".format(test_time, ratio)
    q += "--expiry-range=9999-10000 --key-maximum=10000 "
    q += "--json-out-file={}".format(logfile)
    return q

def memtier_prepropulate(
        memcached_ip,
        port,
        virtual_clients_per_thread,
        logfile,
        threads):

    q = "memtier_benchmark -s {} -p {} ".format(memcached_ip, port)
    q += "--protocol=memcache_text --clients={} --threads={} ".format(virtual_clients_per_thread, threads)
    q += "--requests=15000 --ratio=1:0 --data-size=4096 "
    q += "--expiry-range=9999-10000 --key-maximum=10000 --key-pattern=S:S "
    q += "--json-out-file={}".format(logfile)
    return q

# MEMCACHED SPECIFIC
def setup_middleware(current_ip, listening_port, server_strings, middleware_threads, sharding):
    """
        TODO: Figure out what command to run here!
    :server_string : has to be a space separated items, of tuples that are colon separated,
        of IP and port
    :return:
    """
    q = "java -jar /home/azureuser/middleware-yedavid.jar "
    q += "-l {} ".format(current_ip)
    q += "-p {} ".format(listening_port)
    q += "-m {} ".format(server_strings) #  Allow this to include multiple servers!
    q += "-t {} ".format(middleware_threads)
    q += "-s {} ".format(sharding)

    return q


def setup_memcached(port):
    return "memcached -u root -t 1 -p {} ".format(port)

def stop_memcached():
    return "pkill memcached"

def stop_middleware():
    return "pkill java"

if __name__ == "__main__":
    print("Some commands")
    copy_logs_to_local(23, "/Users/david/asl-fall18-project/_scripts/asd.txt", "/Users/david/asl-fall18-project/")