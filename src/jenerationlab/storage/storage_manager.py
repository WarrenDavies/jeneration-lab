from pathlib import Path
import datetime
import os
import sys

from jenerationutils.data_connections import registry as data_connections_registry


class StorageManager():
    """
    """

    def __init__(self, core_config, experiment_config):
        self.data_connection = data_connections_registry.get_object(core_config)
        self.artifacts = []
        self.save_timestamp = ""
        self.filenames = []
        

    def setup_experiment_folders(self, experiment_folder_name):
        self.experiment_folder_name = experiment_folder_name

        self.experiment_folder = Path("outputs/") / Path(experiment_folder_name)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.output_folder = Path(self.experiment_folder) / Path("artifacts")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    
    def save(self, artifacts = None):
        """
        Saves generated artifacts to the configured directory.

        Images are saved with a timestamped filename.
        """
        if not artifacts:
            artifacts = self.artifacts

        save_timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        batch_filenames = []
        for i, artifact in enumerate(artifacts):
            generation_no = str((len(self.filenames) + 1)).zfill(4)
            file_name = f"{generation_no}_{save_timestamp}_no{i + 1}.jpg"
            batch_filenames.append(file_name)
            self.filenames.append(file_name)
            print("saving ", file_name)
            save_path = os.path.join(self.output_folder, file_name)
            artifact.save(save_path)

        return batch_filenames

    
    def create_data_store(self, headers):
        data_connection.create_new_data_source(headers)