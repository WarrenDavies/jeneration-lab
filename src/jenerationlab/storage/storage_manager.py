from pathlib import Path
import datetime
import os

from pydantic import BaseModel

from jenerationutils.data_connections import registry as data_connections_registry
from jenerationlab.schemas.base import BaseSchema

class StorageManager():
    """
    """

    def __init__(self, config):
        self.data_connector = data_connections_registry.get_object(config["experiment"])
        self.base_schema = BaseSchema(**{**config["experiment"], **config["generator"]})
        self.ParamsSchema = self.get_params_schema()
        
        self.images = []
        self.save_timestamp = ""
        self.filenames = []


    def setup_experiment_folders(self, experiment_folder_name):
        self.experiment_folder = Path("outputs/") / Path(experiment_folder_name)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.images_output_folder = Path(self.experiment_folder) / Path("images")
        self.images_output_folder.mkdir(parents=True, exist_ok=True)

        self.text_output_folder = Path(self.experiment_folder) / Path("text")
        self.text_output_folder.mkdir(parents=True, exist_ok=True)


    def get_params_schema(self):
        # This eventually to be emitted from the generator
        # e.g., ParamsSchema = self.parent.generator.get_params_schema()

        class ParamsSchema(BaseModel):
            dtype: str = ""
            seed: int = 0
            height: int = 0
            width: int = 0
            inf_steps: int = 0
            guidance_scale: float = 0
            enable_attention_slicing: bool = True
            scheduler: str = ""
            
        return ParamsSchema

    
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