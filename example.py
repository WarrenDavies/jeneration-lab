import yaml

from jenerationlab.core.experiment import Experiment
from jenerationlab.core.runner import Runner
from jenerationlab.storage.storage_manager import StorageManager
from jenerationlab.rater.rater import Rater

with open("configs/experiment_demo.yaml", 'r') as stream:
    experiment_config = yaml.safe_load(stream)

with open("configs/core_config.yaml", 'r') as stream:
    core_config = yaml.safe_load(stream)

experiment = Experiment(experiment_config)
storage_manager = StorageManager(core_config, experiment_config)
runner = Runner(core_config, experiment_config, experiment, storage_manager)
runner.run()

with open(str(runner.experiment_config_path), 'r') as stream:
    rater_config = yaml.safe_load(stream)
rating_manager = Rater(core_config, rater_config, storage_manager)

queue = rating_manager.get_queue("rating")

# here is where you would loop through the tasks, but we'll just do one for the demo
rating = True
artifact_id = queue[0]

rating_manager.rate_artifact(artifact_id, "rating", rating)


