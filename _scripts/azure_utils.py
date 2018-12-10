import os
import subprocess
import shlex
import multiprocessing

server_dns = [
    "store2y7detktx6mxasshpublicip1.westeurope.cloudapp.azure.com", # Client1
    "store2y7detktx6mxasshpublicip2.westeurope.cloudapp.azure.com", # Client2
    "store2y7detktx6mxasshpublicip3.westeurope.cloudapp.azure.com", # Client3
    "store2y7detktx6mxasshpublicip4.westeurope.cloudapp.azure.com", # MW1
    "store2y7detktx6mxasshpublicip5.westeurope.cloudapp.azure.com", # MW2
    "store2y7detktx6mxasshpublicip6.westeurope.cloudapp.azure.com", # Server1
    "store2y7detktx6mxasshpublicip7.westeurope.cloudapp.azure.com", # Server2
    "store2y7detktx6mxasshpublicip8.westeurope.cloudapp.azure.com", # Server3

]

def pipe_command_locally(bashcommand, sync):
    print("Executing local command: ", bashcommand)

    if sync:
        result = subprocess.run(shlex.split(bashcommand))
    else:
        os.system(bashcommand)

    return result

def pipe_command_into_ssh(ip, bashcommand, sync):
    assert isinstance(ip, str)

    q = 'ssh azureuser@{} "{}"'.format(ip, bashcommand)
    print("Running command: ", q)

    if sync:
        result = subprocess.call(q, shell=True)
    else:
        os.system(q)

    return result

def check_if_all_servers_are_up():

    for ips in server_dns:
        print("Up!")

    return True


def download_logs(
        container_id,
        server_path,
        local_path,
        name_identifier):
    os.system(
        "docker cp " + str(container_id) + ":" + str(server_path) + name_identifier
        + " " + local_path + name_identifier
    )

    return True

def upload_jar(external_ips, compile=False):
    """
        Compiles the java code to a jar file.
        Then uploads this jar file to the online home directory.
    :param external_ip:
    :return:
    """
    # Build the middleware
    if compile:
        c1 = "cd /Users/david/asl-fall18-project/. && ant clean && ant "
        print("Running ", c1)
        os.system(c1)

    for ip in external_ips:
        c2 = "rsync /Users/david/asl-fall18-project/dist/middleware-yedavid.jar azureuser@{}:/home/azureuser/ --progress".format(ip)
        print("Running ", c2)
        os.system(c2)

if __name__ == "__main__":
    print("Testing if compile and upload works...")
    upload_jar(["store2y7detktx6mxasshpublicip4.westeurope.cloudapp.azure.com"], compile=True)