import time

from _scripts.azure_utils import check_if_all_servers_are_up
from _scripts.utils import get_current_time_as_string

from _scripts.config import CONFIG

from _scripts.experiments.BaseExperiment import BaseExperimentRunner
from _scripts.experiments.resource import CLIENT, SERVER, CLIENT_IP, SERVER_IP

from multiprocessing import Process

"""

az vm start --name Client1 --resource-group MyResourceGroup
az vm start --name Server1 --resource-group MyResourceGroup
az vm start --name Server2 --resource-group MyResourceGroup

### STOPPING
az vm deallocate --name Client1 --resource-group MyResourceGroup
az vm deallocate --name Server1 --resource-group MyResourceGroup
az vm deallocate --name Server2 --resource-group MyResourceGroup

### Memcached stopping
sudo service memcached stop


###

"""

class Exp2_2:

    def set_configuration(self):

        # Implicit variables (as set by the experiment setup)
        self.number_of_servers = 2
        self.number_of_client_machines = 1

        # Explicit variables (as set as parameters inside the experiment code)
        self.instances_of_memtier_per_machine = 2
        self.threads_per_memtier_instance = 1
        self.virtual_clients_per_thread = [(2 ** x) for x in range(0, 6)]
        # self.virtual_clients_per_thread = [(2 ** x) for x in range(4, 6)]

        # Multi-Get parameters
        self.multiget = False  # So all other parameters disappear

        # Meta experiment configurations
        self.repetitions = 3  # 3 should be fine
        self.time = 60 + 15 # Time in seconds # DEV
        # self.time = 1
        self.population_time = 30
        # self.population_time = 1


class ExperimentBaseline2(BaseExperimentRunner, Exp2_2):

    def __init__(self):
        super(ExperimentBaseline2, self).__init__()
        # Run the initalizers from the parent classes
        self.set_configuration()

        preliminary_name = "ExperimentBaseline2/"
        self.name = "_exp2_1_"

        # Append logdir with some other stuff
        self.local_logdir += preliminary_name
        self.remote_logdir += "logs/"

    def run(self):

        print("Running experiment 2")

        assert check_if_all_servers_are_up(), ("There seems to be a problem that not all servers are up!")

        # Check if servers are up!
        self._test_if_server_is_up(
            [
                CLIENT['Client1'],
                SERVER['Server1'], SERVER['Server2']
            ]
        )

        print("Stopping any memcached instances")
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1'], SERVER['Server2']]
        )
        time.sleep(2)

        print("Setting up..")
        memcached_servers = self.start_memcached_servers(
            memcached_addresses=[
                SERVER['Server1'], SERVER['Server2']
            ],
            port=self.port
        )
        time.sleep(2)


        print("Prepopulating")
        self.prepopulate_memcached_servers([CLIENT['Client1']], SERVER_IP['Server1'], port=self.port, time=self.population_time)
        self.prepopulate_memcached_servers([CLIENT['Client1']], SERVER_IP['Server2'], port=self.port, time=self.population_time)
        time.sleep(self.population_time)

        self._create_log_directories([CLIENT['Client1']], self.remote_logdir)

        # Setting the reads to writes ratio
        for self.writes in ["0", "1"]:
            self.reads = "1" if self.writes == "0" else "0" # Exactly only reads or writes

            for virtual_client_threads in self.virtual_clients_per_thread:

                for i in range(self.repetitions):

                    print("CONFIGURATION VC!: ", virtual_client_threads)

                    start_time = time.time()

                    all_client_processes = []
                    for client_number in ['Client1']:

                        def runner_function():
                            logfile = self.remote_logdir + self.name + "virtualclients_{}__rep_{}_client_{}__writes_{}.txt".format(
                                virtual_client_threads, i, client_number, self.writes)
                            self._create_log_files([CLIENT[client_number]], logfile)

                            print("CONFIGURATION : ", logfile)

                            start_time = time.time()

                            # print("Running right now (first) ...", )
                            print("Running memtier on the server 1!")
                            # TODO: Testing this with one-to-one to check if replicate is the case
                            self.run_memtiered_servers(
                                client_ips=[CLIENT[client_number]],
                                server_ip=SERVER_IP['Server1'],
                                port=self.port,
                                logfile=logfile + "_Server1",
                                time=self.time,
                                write_ratio=self.writes,
                                read_ratio=self.reads,
                                virtual_clients_per_thread=virtual_client_threads,
                                threads=self.threads_per_memtier_instance
                            )
                            print("Running memtier on the server 2!")
                            self.run_memtiered_servers(
                                client_ips=[CLIENT[client_number]],
                                server_ip=SERVER_IP['Server2'],
                                port=self.port,
                                logfile=logfile + "_Server2",
                                time=self.time,
                                write_ratio=self.writes,
                                read_ratio=self.reads,
                                virtual_clients_per_thread=virtual_client_threads,
                                threads=self.threads_per_memtier_instance
                            )
                            print("Running right now (second) ...", time.time() - start_time)

                            print("Done running memtier on the server!")

                        p = Process(target=runner_function)
                        p.start()
                        all_client_processes.append(p)

                    time.sleep(self.time + self.time // 5)  # TODO: Timeout for as long as the experiments run

                    print("Total runtime is: ", time.time() - start_time)

                    # Join all processes again!
                    [p.join() for p in all_client_processes]

                    self.copy_logs_to_local(
                        [CLIENT['Client1']],
                        self.remote_logdir,
                        self.local_logdir
                    )
                    time.sleep(10)


        # kill all memcached services
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1'], SERVER['Server2']]
        )

if __name__ == "__main__":
    experiment2 = ExperimentBaseline2()
    experiment2.run()
