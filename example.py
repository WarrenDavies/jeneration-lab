import yaml

from jenerationlab.core.experiment import Experiment
from jenerationlab.core.runner import Runner
from jenerationlab.storage.storage_manager import StorageManager
from jenerationlab.metrics.metrics_manager import MetricsManager
from jenerationlab.benchmarking.benchmarking_manager import BenchmarkingManager
from jenerationlab.rater.rater import Rater

with open("configs/experiment_demo_llm.yaml", 'r') as stream:
    experiment_config = yaml.safe_load(stream)

with open("configs/core_config.yaml", 'r') as stream:
    core_config = yaml.safe_load(stream)

experiment = Experiment(experiment_config)
storage_manager = StorageManager(core_config, experiment_config)

runner = Runner(core_config, experiment_config, experiment, storage_manager)
runner.run()

with open(str(runner.experiment_config_path), 'r') as stream:
    experiment_config = yaml.safe_load(stream)

metrics_manager = MetricsManager(core_config, experiment_config, storage_manager)
metrics_manager.calculate_metrics()

rating_manager = Rater(core_config, experiment_config, storage_manager)
requested_ratings = experiment_config["ratings"].keys()
for rating_name in requested_ratings:
    queue = rating_manager.get_queue(rating_name)
    for artifact_id in queue:
        question = rating_manager.get_question(rating_name)
        print(artifact_id)
        print(question)
        rating_value = input("> ")
        rating_manager.rate_artifact(artifact_id, rating_name, rating_value)
