from pathlib import Path

from jenerationutils.data_connections import registry as data_connections_registry
from jenerationlab.schemas.base import BaseSchema

class StorageManager():
    """
    """

    def __init__(self, parent, config):
        self.parent = parent
        self.data_connector = data_connections_registry.get_object(config["experiment"])
        self.base_schema = BaseSchema(**{**config["experiment"], **config["generator"]})
        self.setup_experiment_folders()


    def setup_experiment_folders(self):
        self.experiment_folder = Path("outputs/") / Path(self.parent.start_timestamp_str)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.images_output_folder = Path(self.experiment_folder) / Path("images")
        self.images_output_folder.mkdir(parents=True, exist_ok=True)

        self.text_output_folder = Path(self.experiment_folder) / Path("text")
        self.text_output_folder.mkdir(parents=True, exist_ok=True)