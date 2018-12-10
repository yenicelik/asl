import time
import datetime
import subprocess
import shlex
import multiprocessing

instances = {
    "client1": "store2y7detktx6mxasshpublicip1.westeurope.cloudapp.azure.com",
    "client2": "store2y7detktx6mxasshpublicip2.westeurope.cloudapp.azure.com",
    "client3": "store2y7detktx6mxasshpublicip3.westeurope.cloudapp.azure.com",

    "middleware1": "store2y7detktx6mxasshpublicip4.westeurope.cloudapp.azure.com",
    "middleware2": "store2y7detktx6mxasshpublicip5.westeurope.cloudapp.azure.com",

    "server1": "store2y7detktx6mxasshpublicip6.westeurope.cloudapp.azure.com",
    "server2": "store2y7detktx6mxasshpublicip7.westeurope.cloudapp.azure.com",
    "server3": "store2y7detktx6mxasshpublicip8.westeurope.cloudapp.azure.com"
}

def console_newline():
    print("################")

def get_current_time_as_string():
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
    return date

def _patch_function_on_new_process_sync(f, args=None):
    p = multiprocessing.Process(
        target=f
    )
    p.daemon = True
    p.start()
    return p

def _patch_function_on_new_process_async(f, args=None):
    return subprocess.check_call(shlex.split('ls -al'))

if __name__ == "__main__":
    a = get_current_time_as_string()
    print(a)