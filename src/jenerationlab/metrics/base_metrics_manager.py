from pathlib import Path
import uuid
import datetime

from jenerationlab.metrics import registry as metrics_registry
from jenerationutils.jenerationrecord import registry as recorder_registry
from jenerationlab.schemas.measurements import MeasurementSchema


class BaseMetricsManager():
    """
    """
    def __init__(self, core_config, experiment_config, storage_manager):
        self.config = core_config
        self.experiment_config = experiment_config
        self.ARTIFACT_GETTERS = {
            "image": self.get_image_artifact,
            "text": self.get_text_artifact
        }
        self.get_artifact = self.ARTIFACT_GETTERS[
            self.experiment_config["experiment"]["generation_format"]
        ]
        self.storage_manager = storage_manager
        self.artifact_folder = self.experiment_config["experiment"]["artifact_folder"]
        self.df_all_measurements = self.import_data_to_df("measurements")
        self.df_artifacts = self.import_data_to_df("artifacts")
        self.GenerationRecordClass = recorder_registry.get_class(
            core_config["data_connections"]["measurements"]["output_data_type"]
        )
        self.producer = "auto"


    def import_data_to_df(self, data_source):
        conn = self.storage_manager.data_connections[data_source]
        df = conn.to_pandas()
        
        return df


    def filter_to_experiment(self, df, experiment_id):
        experiment_mask = df["experiment_id"] == experiment_id
        df = df[experiment_mask]
        return df


    def filter_to_rows_with_measurement(self, df, measurement_name):
        measurement_name_mask = df["measurement_name"] == measurement_name
        df = df[measurement_name_mask]
        return df


    def get_queue(self, metric_name):
        queue = self._get_queue_impl(metric_name)
        return queue


    def _get_queue_impl(self, metric_name):
        """
        Logic to get uncompleted metrics within a given experiment.
        """
        df_artifacts = self.filter_to_experiment(
            self.df_artifacts,
            self.experiment_config["experiment"]["experiment_id"]
        )
        df_measurements = self.filter_to_experiment(
            self.df_all_measurements,
            self.experiment_config["experiment"]["experiment_id"]
        )
        df_artifacts_with_metric = self.filter_to_rows_with_measurement(
            df_measurements,
            metric_name,
        )

        all_artifacts = df_artifacts["artifact_id"].tolist()
        artifacts_with_metrics = df_artifacts_with_metric["artifact_id"].tolist()
        queue = list(set(all_artifacts) - set(artifacts_with_metrics))
        
        return queue


    def get_metrics_calculators(self):
        metric_calculators = {}

        for metric_calculator in self.experiment_config["metrics"]:
            metric_calculators[metric_calculator] = (
                metrics_registry.get_object(metric_calculator)
            )

        return metric_calculators


    def get_file_path(self, artifact_id):
        artifact_mask = self.df_artifacts["artifact_id"] == artifact_id
        df_artifact = self.df_artifacts[artifact_mask]
        file_name = df_artifact["filename"].iat[0]
        return file_name


    def get_text_artifact(self, artifact_id):

        file_name = self.get_file_path(artifact_id)
        file_path = Path(self.artifact_folder) / file_name
        file_path = str(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            text_artifact = file.read()
        return text_artifact


    def get_image_artifact(self, artifact_id):
        pass


    @staticmethod
    def get_rating_type_key(rating):
        TYPE_MAP = {
            int: "value_int",
            float: "value_float",
            str: "value_str",
            bool: "value_bool",
        }

        value_type = TYPE_MAP.get(type(rating))
        if not value_type:
            raise ValueError(f"Unsupported rating type: {type(rating)}")

        return value_type


    def build_measurement_record(self, artifact_id, rating_name, rating):

        rating_type_key = self.get_rating_type_key(rating)

        values = {
            "value_int": None,
            "value_float": None,
            "value_str": None,
            "value_bool": None
        }
        values[rating_type_key] = rating

        measurement_record = {
            "measurement_id": uuid.uuid4().hex[:8],
            "artifact_id": artifact_id,
            "experiment_id": self.experiment_config["experiment"]["experiment_id"],
            "timestamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "producer": self.producer,
            "measurement_name": rating_name,
            **values
        }

        return measurement_record


    def save_metric(self, measurement_record):
        data_row = measurement_record.create_data_row()
        self.storage_manager.data_connections["measurements"].append_data(
            data_row
        )

