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
        self.images = []
        self.save_timestamp = ""
        self.filenames = []
        # print(self.data_connection)
        # sys.exit()
        

    def setup_experiment_folders(self, experiment_folder_name):
        self.experiment_folder_name = experiment_folder_name

        self.experiment_folder = Path("outputs/") / Path(experiment_folder_name)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.images_output_folder = Path(self.experiment_folder) / Path("images")
        self.images_output_folder.mkdir(parents=True, exist_ok=True)

        self.text_output_folder = Path(self.experiment_folder) / Path("text")
        self.text_output_folder.mkdir(parents=True, exist_ok=True)

    
    def save(self):
        """
        Saves generated artifacts to the configured directory.

        Images are saved with a timestamped filename.
        """
        save_timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        for i, image in enumerate(self.images):
            generation_no = str((len(self.filenames) + 1)).zfill(4)
            file_name = f"{generation_no}_{save_timestamp}_no{i + 1}.jpg"
            self.filenames.append(file_name)
            print("saving ", file_name)
            save_path = os.path.join(self.images_output_folder, file_name)
            image.save(save_path)

    
    def create_data_store(self, headers):
        data_connection.create_new_data_source(headers)