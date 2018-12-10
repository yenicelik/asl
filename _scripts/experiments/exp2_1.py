import time

from _scripts.azure_utils import check_if_all_servers_are_up
from _scripts.utils import get_current_time_as_string

from _scripts.config import CONFIG

from _scripts.experiments.BaseExperiment import BaseExperimentRunner
from _scripts.experiments.resource import CLIENT, SERVER, CLIENT_IP, SERVER_IP

from multiprocessing import Process

# Starting and stopping all VM's
"""

az vm start --name Client1 --resource-group MyResourceGroup
az vm start --name Client2 --resource-group MyResourceGroup
az vm start --name Client3 --resource-group MyResourceGroup
az vm start --name Server1 --resource-group MyResourceGroup

### STOPPING
az vm deallocate --name Client1 --resource-group MyResourceGroup
az vm deallocate --name Client2 --resource-group MyResourceGroup
az vm deallocate --name Client3 --resource-group MyResourceGroup
az vm deallocate --name Server1 --resource-group MyResourceGroup

### Memcached stopping
sudo service memcached stop


###
PREPOPULATION WRITES APPR. 74796 ops,    3712 (avg:    3739) ops/sec, 14.65MB/sec (avg: 14.75MB/sec), keys into it.

"""

class Exp2_1:
    """
        Configuration for this specific Experiments.
        We have two experiments:
            - Read only
            - Write only
    """

    def __init__(self):
        print("Baseline without Middleware 1!")
        self.set_configuration()

    def set_configuration(self):

        # Implicit variables (as set by the experiment setup)
        self.number_of_servers = 1
        self.number_of_client_machines = 3

        # Explicity variables (as set as parameters inside the experiment code)
        self.instances_of_memtier_per_machine = 1
        self.threads_per_memtier_instance = 2
        # self.virtual_clients_per_thread = [(2**x) for x in range(0, 6)]
        self.virtual_clients_per_thread = [(2 ** x) for x in range(0, 6)]  # DEV

        # Setting the reads to writes ratio
        self.writes = "0"
        self.reads = "1" if self.writes == "0" else "0" # Exactly only reads or writes

        # Multi-Get parameters
        self.multiget = False  # So all other parameters disappear

        # Meta experiment configurations
        self.repetitions = 3  # 3 should be fine
        self.time = 60 + 15 # Time in seconds # DEV
        # self.time = 1
        self.population_time = 20
        # self.population_time = 1



class ExperimentBaseline1(BaseExperimentRunner, Exp2_1):

    def __init__(self):
        super(ExperimentBaseline1, self).__init__()
        # Run the initalizers from the parent classes
        self.set_configuration()

        preliminary_name = "ExperimentBaseline1/"

        # Append logdir with some other stuff
        self.local_logdir += preliminary_name
        self.remote_logdir += "logs/"

    def run(self):

        print("Running experiment 1")

        assert check_if_all_servers_are_up(), ("There seems to be a problem that not all servers are up!")

        self._test_if_server_is_up([CLIENT['Client1'], CLIENT['Client2'], CLIENT['Client3'], SERVER['Server1']])

        print("Stopping any memcached instances")
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1']]
        )
        time.sleep(2)

        print("Setting up..")
        memcached_servers = self.start_memcached_servers(
            memcached_addresses=[SERVER['Server1']],
            port=self.port
        )
        time.sleep(2)

        print("Prepopulating")
        self.prepopulate_memcached_servers([CLIENT['Client1']], SERVER_IP['Server1'], port=self.port, time=self.population_time)
        time.sleep(self.population_time)

        self._create_log_directories([CLIENT['Client1'], CLIENT['Client2'], CLIENT['Client3']], self.remote_logdir)

        for virtual_client_threads in self.virtual_clients_per_thread:

            for i in range(self.repetitions):

                # FORK JOIN for all individual clients

                print("CONFIGURATION VC!: ", virtual_client_threads)

                all_client_processes = []
                for client_number in ['Client1', 'Client2', 'Client3']:


                    def runner_function():

                        logfile = self.remote_logdir + "virtualclients_{}__rep_{}_client_{}_writes_{}.txt".format(virtual_client_threads, i, client_number, self.writes)
                        self._create_log_files([CLIENT[client_number]], logfile)

                        print("CONFIGURATION : ", logfile)

                        print("Running memtier on the server!")
                        self.run_memtiered_servers(
                            client_ips=[CLIENT[client_number]],
                            server_ip=SERVER_IP['Server1'],
                            port=self.port,
                            logfile=logfile,
                            time=self.time,
                            write_ratio=self.writes,
                            read_ratio=self.reads,
                            virtual_clients_per_thread=virtual_client_threads,
                            threads=self.threads_per_memtier_instance
                        )
                        print("Done running memtier on the server!")

                    p = Process(target=runner_function)
                    p.start()
                    all_client_processes.append(p)

                time.sleep(self.time)  # TODO: Timeout for as long as the experiments run

                # Join all processes again!
                [p.join() for p in all_client_processes]


        self.copy_logs_to_local(
            [CLIENT['Client1'], CLIENT['Client2'], CLIENT['Client3']],
            self.remote_logdir,
            self.local_logdir
        )
        time.sleep(20)

        # kill all memcached services
        self.stop_memcached_servers(
            memcached_addresses=[SERVER['Server1']]
        )

if __name__ == "__main__":
    experiment1 = ExperimentBaseline1()
    experiment1.run()
