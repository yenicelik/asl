import time

from _scripts.azure_utils import check_if_all_servers_are_up, upload_jar
from _scripts.utils import get_current_time_as_string

from _scripts.config import CONFIG

from _scripts.experiments.BaseExperiment import BaseExperimentRunner
from _scripts.experiments.resource import CLIENT, SERVER, CLIENT_IP, SERVER_IP, MIDDLEWARE, MIDDLEWARE_IP

from multiprocessing import Process

# Starting and stopping all VM's
"""

az vm start --name Client1 --resource-group MyResourceGroup
az vm start --name Client2 --resource-group MyResourceGroup
az vm start --name Client3 --resource-group MyResourceGroup
az vm start --name Middleware1 --resource-group MyResourceGroup
az vm start --name Middleware2 --resource-group MyResourceGroup
az vm start --name Server1 --resource-group MyResourceGroup
az vm start --name Server2 --resource-group MyResourceGroup
az vm start --name Server3 --resource-group MyResourceGroup

### STOPPING
az vm deallocate --name Client1 --resource-group MyResourceGroup
az vm deallocate --name Client2 --resource-group MyResourceGroup
az vm deallocate --name Client3 --resource-group MyResourceGroup
az vm deallocate --name Middleware1 --resource-group MyResourceGroup
az vm deallocate --name Middleware2 --resource-group MyResourceGroup
az vm deallocate --name Server1 --resource-group MyResourceGroup
az vm deallocate --name Server2 --resource-group MyResourceGroup
az vm deallocate --name Server3 --resource-group MyResourceGroup

### Memcached stopping
sudo service memcached stop

### Stopping the middleware
sudo pkill java


###
PREPOPULATION WRITES APPR. 74796 ops,    3712 (avg:    3739) ops/sec, 14.65MB/sec (avg: 14.75MB/sec), keys into it.

"""

"""
    Baseline with two Middlewares
"""


class Exp5_1:
    """
        Configuration for this specific Experiments:
        We have experiments:
            - Write only
    """

    def __init__(self):
        print("Sharded and non-sharded!")
        self.set_configuration()

    def set_configuration(self):
        self.number_of_servers = 3
        self.number_of_client_machines = 3
        self.instances_of_memtier_per_machine = 2
        self.threads_per_memtier_instance = 1
        # self.virtual_clients_per_thread = [(2 ** x) for x in range(0, 6)]
        self.virtual_clients_per_thread = 2

        # Middleware parameters
        self.number_of_middlewares = 2
        self.worker_threads_per_middleware = 64

        # Setting the reads to writes ratio
        self.writes = "1"
        self.reads = ["1", "3", "6", "9"]

        # Multi-Get parameters
        self.multiget = True  # So all other parameters disappear
        self.sharding = [False, True]

        # Meta experiment configurations
        self.repetitions = 3  # 3 should be fine
        self.time = 60 + 15 # Time in seconds
        # self.time = 10
        self.population_time = 20
        # self.population_time = 1


class ExperimentSharding(BaseExperimentRunner, Exp5_1):

    def __init__(self):
        super(ExperimentSharding, self).__init__()
        # Run the initalizers from the parent classes
        self.set_configuration()

        preliminary_name = "ExperimentSharding/"
        self.name = "_Exp51"

        # Append logdir with some other stuff
        self.local_logdir += preliminary_name
        self.remote_logdir += 'logs/'

    def run(self):

        print("Running experiment 1")

        assert check_if_all_servers_are_up(), ("There seems to be a problem that not all servers are up!")

        self._test_if_server_is_up(
            [
                CLIENT['Client1'], CLIENT['Client2'], CLIENT['Client3'],
                MIDDLEWARE['Middleware1'], MIDDLEWARE['Middleware2'],
                SERVER['Server1'], SERVER['Server2'], SERVER['Server3']
            ]
        )

        # TODO: Compile, and upload the java jar to the middleware!
        print("Compile and upload middleware to VM...")
        upload_jar([MIDDLEWARE['Middleware1']], compile=True)
        upload_jar([MIDDLEWARE['Middleware2']], compile=True)

        print("Stopping any memcached instances")
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1'], SERVER['Server2'], SERVER['Server3']]
        )
        time.sleep(2)

        print("Setting up memcached..")
        self.start_memcached_servers(
            memcached_addresses=[SERVER['Server1'], SERVER['Server2'], SERVER['Server3']],
            port=self.port
        )
        time.sleep(5)

        server_strings = SERVER_IP['Server1'] + ":" + str(self.port) + " " + \
                         SERVER_IP['Server2'] + ":" + str(self.port) + " " + \
                         SERVER_IP['Server3'] + ":" + str(self.port)
        print("Server strings are: (USED BY MIDDLEWARE LATER)", server_strings)

        print("Prepopulating")
        self.prepopulate_memcached_servers([CLIENT['Client1']], SERVER_IP['Server1'], port=self.port, time=self.population_time)
        self.prepopulate_memcached_servers([CLIENT['Client2']], SERVER_IP['Server2'], port=self.port, time=self.population_time)
        self.prepopulate_memcached_servers([CLIENT['Client3']], SERVER_IP['Server3'], port=self.port, time=self.population_time)
        time.sleep(self.population_time)

        self._create_log_directories(
            [CLIENT['Client1'], CLIENT['Client2'], CLIENT['Client3']],
            self.remote_logdir
        )

        # Iterate through keysizes
        for keysize in self.reads:
            print("Keysize is: ", keysize)

            for sharding in self.sharding:
                print("Sharding: ", sharding)

                assert type(self.worker_threads_per_middleware) == int, ("NO", self.worker_threads_per_middleware)
                assert type(self.virtual_clients_per_thread) == int, ("NO 2", self.virtual_clients_per_thread)

                for i in range(self.repetitions):

                    # FORK JOIN for all individual clients

                    print("CONFIGURATION VC!: ", self.virtual_clients_per_thread)

                    print("Stopping any middleware instances")
                    self.stop_middleware_servers(
                        middleware_addresses=[MIDDLEWARE['Middleware1']]
                    )
                    self.stop_middleware_servers(
                        middleware_addresses=[MIDDLEWARE['Middleware2']]
                    )
                    time.sleep(5)

                    # Generating the server strings:
                    print("Setting up the middleware...")
                    self.start_middleware_servers(
                        middleware_addresses=[MIDDLEWARE['Middleware1'], MIDDLEWARE['Middleware2']],
                        middleware_localips=[MIDDLEWARE_IP['Middleware1'], MIDDLEWARE_IP['Middleware2']],
                        listening_port=self.middleware_port,
                        server_strings=server_strings,
                        middleware_threads=self.worker_threads_per_middleware,
                        sharding=sharding
                    )
                    time.sleep(10)

                    self._create_log_directories(
                        [MIDDLEWARE['Middleware1']],
                        self.remote_logdir
                    )
                    self._create_log_directories(
                        [MIDDLEWARE['Middleware2']],
                        self.remote_logdir
                    )
                    time.sleep(4)

                    start_time = time.time()

                    all_client_processes = []

                    for client_number in ['Client1', 'Client2', 'Client3']:

                        def runner_function():
                            logfile = self.remote_logdir + self.name + "_" + "multikeysize_{}_middleware1__rep_{}_client_{}_sharding_{}_middlewarethreads_{}.txt".format(
                                keysize, i, client_number, sharding, self.worker_threads_per_middleware)
                            self._create_log_files([CLIENT[client_number]], logfile)
                            print("CONFIGURATION : ", logfile)

                            print("Running memtier on the server 1!")
                            self.run_memtiered_servers(
                                client_ips=[CLIENT[client_number]],
                                server_ip=MIDDLEWARE_IP['Middleware1'],
                                port=self.middleware_port,
                                logfile=logfile,
                                time=self.time,
                                write_ratio=self.writes,
                                read_ratio=keysize,
                                virtual_clients_per_thread=self.virtual_clients_per_thread,
                                threads=self.threads_per_memtier_instance
                            )

                            logfile = self.remote_logdir + "_" + self.name + "_" + "multikeysize_{}_middleware2__rep_{}_client_{}_sharding_{}_middlewarethreads_{}.txt".format(
                                keysize, i, client_number, sharding, self.worker_threads_per_middleware)
                            self._create_log_files([CLIENT[client_number]], logfile)
                            print("CONFIGURATION : ", logfile)

                            print("Running memtier on the server 2!")
                            self.run_memtiered_servers(
                                client_ips=[CLIENT[client_number]],
                                server_ip=MIDDLEWARE_IP['Middleware2'],
                                port=self.middleware_port,
                                logfile=logfile,
                                time=self.time,
                                write_ratio=self.writes,
                                read_ratio=keysize,
                                virtual_clients_per_thread=self.virtual_clients_per_thread,
                                threads=self.threads_per_memtier_instance
                            )
                            print("Done running memtier on the server!")

                        p = Process(target=runner_function)
                        p.start()
                        all_client_processes.append(p)
                        time.sleep(1)

                    time.sleep(self.time + self.time // 3)

                    # Join all processes again!
                    print("Starting to copy... Took so many seconds", time.time() - start_time)

                    self.copy_logs_to_local(
                        [
                            MIDDLEWARE['Middleware1']
                        ],
                        self.remote_logdir,
                        self.local_logdir + "Middleware1_multikeygetsize_{}_rep_{}__sharding_{}__middlewareworkerthreads_{}/".format(
                            keysize, i, sharding, self.worker_threads_per_middleware)
                    )
                    self.copy_logs_to_local(
                        [
                            MIDDLEWARE['Middleware2']
                        ],
                        self.remote_logdir,
                        self.local_logdir + "Middleware2_multikeygetsize_{}_rep_{}__sharding_{}_middlewareworkerthreads_{}/".format(
                            keysize, i, sharding, self.worker_threads_per_middleware)
                    )
                    time.sleep(10)

                    # Join all processes again!
                    [p.join(self.time // 3) for p in all_client_processes]

                    print("Starting to copy... Took so many seconds", time.time() - start_time)

                    self.copy_logs_to_local(
                        [
                            CLIENT['Client1'],
                            CLIENT['Client2'],
                            CLIENT['Client3']
                        ],
                        self.remote_logdir,
                        self.local_logdir
                    )

                    time.sleep(30)

        # kill all memcached services
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1']]
        )


if __name__ == "__main__":
    experiment1 = ExperimentSharding()
    experiment1.run()
