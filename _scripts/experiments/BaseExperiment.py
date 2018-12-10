import time

from _scripts.azure_utils import check_if_all_servers_are_up, pipe_command_into_ssh, pipe_command_locally
from _scripts.commands import test_if_there_is_output, setup_memcached, \
    memtier_get_requests, create_logfile, \
    create_logdir, create_local_logdir, remove_logdir, copy_logs_to_local, \
    check_if_logdir_exists, stop_memcached, stop_middleware, setup_middleware, \
    memtier_prepropulate
from _scripts.config import CONFIG
from _scripts.utils import _patch_function_on_new_process_sync

class BaseExperimentRunner:
    """
        This base runner should include common logic like
            - logging
    """

    def _test_if_server_is_up(self, server_ips):
        """
            Checks if the individual instances are echo-ing something
        :param server_ips:
        :return:
        """
        for sip in server_ips:
            pipe_command_into_ssh(sip, test_if_there_is_output(), sync=True)

    # Stupid logic which doesn't run otherwise!
    def run_memtiered_servers(self, client_ips, server_ip, port, logfile, time, write_ratio, read_ratio, virtual_clients_per_thread, threads):
        print("Starting memtiered servers")
        for cip in client_ips:
            print("Starting ... ")
            memtier_process = pipe_command_into_ssh(cip, bashcommand=memtier_get_requests(
                memcached_ip=server_ip,
                port=port,
                test_time=time,
                logfile=logfile,
                write_ratio=write_ratio,
                read_ratio=read_ratio,
                virtual_clients_per_thread=virtual_clients_per_thread,
                threads=threads
            ), sync=True)
            print("Ending ... ")
        print("Boomm... ")

    def prepopulate_memcached_servers(self, client_ips, server_ip, port, time):
        print("Starting pre-population memtier servers")
        for cip in client_ips:
            print("Starting ... ")
            memtier_process = pipe_command_into_ssh(cip, bashcommand=memtier_prepropulate(
                memcached_ip=server_ip,
                port=port,
                logfile="./tmp.log",
                threads=2,
                virtual_clients_per_thread=2
            ), sync=True)
            print("Ending ... ")
        print("Boomm... ")

    def start_middleware_servers(self, middleware_addresses, middleware_localips, listening_port, server_strings, middleware_threads, sharding):
        print("Starting middleware...")
        out = []
        for maddress, mlocalips in zip(middleware_addresses, middleware_localips):
            print("Running middleware on the server!")
            memcached_process = _patch_function_on_new_process_sync(
                lambda: pipe_command_into_ssh(maddress, bashcommand=setup_middleware(
                    current_ip=mlocalips,
                    listening_port=listening_port,
                    server_strings=server_strings,
                    middleware_threads=middleware_threads,
                    sharding=sharding
                ), sync=True)
            )
            print("Started running memcached on the server!")
            out.append(memcached_process)
        return out

    def start_memcached_servers(self, memcached_addresses, port):
        print("More shit...")
        out = []
        for maddress in memcached_addresses:
            print("Running memcached on the server!")
            memcached_process = _patch_function_on_new_process_sync(
                lambda: pipe_command_into_ssh(maddress, bashcommand=setup_memcached(
                    port=port
                ), sync=True)
            )
            print("Started running memcached on the server!")
            out.append(memcached_process)
        return out

    def stop_middleware_servers(self, middleware_addresses):
        print("Stopping middleware...")
        out = []
        for maddress in middleware_addresses:
            print("Stopping middleware on the server!")
            memcached_process = _patch_function_on_new_process_sync(
                lambda: pipe_command_into_ssh(maddress, bashcommand=stop_middleware(), sync=True)
            )
            print("Started running memcached on the server!")
            out.append(memcached_process)
        return out

    def stop_memcached_servers(self, memcached_addresses):
        print("More shit... Stopping memcached...")
        out = []
        for maddress in memcached_addresses:
            print("Stopping memcached on the server!")
            memcached_process = _patch_function_on_new_process_sync(
                lambda: pipe_command_into_ssh(maddress, bashcommand=stop_memcached(), sync=True)
            )
            print("Started running memcached on the server!")
            out.append(memcached_process)
        return out

    def copy_logs_to_local(self, ips, remote_logdir, local_logdir, logfile=True):
        """
            Copies all the logs from the remote machine to the local machine
        :param ips:
        :param remote_logdir:
        :param local_logdir:
        :return:
        """
        for ip in ips:
            pipe_command_locally(
                copy_logs_to_local(ip, remote_logdir, local_logdir, logfile),
                sync=True
            )

    def _create_log_directories(self, ips, logdir):
        print("Creating local directoreis for logdirs")

        for ip in ips:
            pipe_command_locally(create_local_logdir(self.local_logdir), sync=True)

            # Create remote log directories
            try:
                q = pipe_command_into_ssh(ip, remove_logdir(logdir), sync=True)
                print(q)
            except Exception as e:
                print(e)
            try:
                q = pipe_command_into_ssh(ip, create_logdir(logdir), sync=True)
                print(q)
            except Exception as e:
                print(e)

                # Check if directory exists by printing the ls
            print("Printing directory")
            q = pipe_command_into_ssh(ip, check_if_logdir_exists(logdir), sync=True)
            print(q)

    def _create_log_files(self, ips, logfile):
        for ip in ips:
            q = pipe_command_into_ssh(ip, create_logfile(logfile), sync=True)
            print(q)

    def __init__(self):
        self.local_logdir = "/Users/david/asl-fall18-project/data/raw/"
        self.remote_logdir = "/home/azureuser/"
        self.port = CONFIG['PORT']
        self.middleware_port = CONFIG['MIDDLEWARE_PORT']


    # def run_experiment(self):
    #     raise NotImplementedError
    #
    # def run(self):
    #     # First create logdirs
    #     self._create_log_directories()
    #
    #     self.run_experiment()
    #
    #     # Pull logs from the servers
    #     pipe_command_locally(
    #         copy_logs_to_local(client_ip, self.remote_logdir, self.local_logdir),
    #         sync=True
    #     )


# class AllExperimentsRunner:
#
#
#     def select_clients_and_servers(self):
#         pass
#
#     def _get_client(self):
#         out = CLIENT[self.client_selector]
#         self.client_selector += 1
#         assert self.client_selector < 2, ("Something went wrong!")
#         return out
#
#     def _get_middleware(self):
#         out = MIDDLEWARE[self.middleware_selector]
#         self.middleware_selector
#
#     def _reset_client_selectors(self):
#
#         self.client_selector = 0
#         self.middleware_selector = 0
#         self.server_selector = 0


if __name__ == "__main__":
    print("Starting the main thingy")

    # experiments_runner = AllExperimentsRunner()
