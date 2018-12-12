from _scripts.experiments.exp3_1 import ExperimentBaseline1
from _scripts.experiments.exp3_2 import ExperimentBaselineMW2
from _scripts.experiments.exp4_1 import ExperimentThroughputWrite
from _scripts.experiments.exp5_1 import ExperimentSharding
from _scripts.experiments.exp6_1 import Experiment2KOneMiddleware

if __name__ == "__main__":
    # Baseline with one middleware
    print("#### BASELINE 1")
    experiment1 = ExperimentBaseline1()
    experiment1.run()

    # Baseline with two middlewares
    print("#### BASELINE 2")
    experiment2 = ExperimentBaselineMW2()
    experiment2.run()

    # Throughput Writes
    print("#### THROUGHPUT WRITES")
    experiment3 = ExperimentThroughputWrite()
    experiment3.run()

    # Sharding
    print("#### SHARDING")
    experiment4 = ExperimentSharding()
    experiment4.run()

    # 2K
    print("#### 2K EXP")
    experiment5 = Experiment2KOneMiddleware()
    experiment5.run()
