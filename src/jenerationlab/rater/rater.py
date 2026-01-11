import uuid
import datetime

from jenerationutils.jenerationrecord import registry as recorder_registry

from jenerationlab.schemas.measurements import MeasurementSchema


class InvalidRatingError(Exception):
    pass


class Rater():
    """
    """
    def __init__(self, core_config, rater_config, storage_manager):
        self.config = rater_config
        self.storage_manager = storage_manager
        self.df_all_measurements = self.import_data_to_df("measurements")
        self.df_artifacts = self.import_data_to_df("experiments")
        self.GenerationRecordClass = recorder_registry.get_class(
            core_config["data_connections"]["measurements"]["output_data_type"]
        )


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


    def get_queue(self, rating_name):
        """
        Logic to get uncompleted ratings within a given experiment.
        """
        df_artifacts = self.filter_to_experiment(
            self.df_artifacts,
            self.config["experiment"]["experiment_id"]
        )
        df_measurements = self.filter_to_experiment(
            self.df_all_measurements,
            self.config["experiment"]["experiment_id"]
        )
        df_artifacts_with_rating = self.filter_to_rows_with_measurement(
            df_measurements,
            rating_name,
        )

        all_artifacts = df_artifacts["filename"].tolist()
        artifacts_with_ratings = df_artifacts_with_rating["artifact_id"].tolist()
        tasks = list(set(all_artifacts) - set(artifacts_with_ratings))
        tasks.sort()

        return tasks


    def get_rating_type_key(self, rating):
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
            "experiment_id": self.config["experiment"]["experiment_id"],
            "timestamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "producer": "human",
            "measurement_name": rating_name,
            **values
        }

        return measurement_record

       
    def save_rating(self, measurement_record):
        data_row = measurement_record.create_data_row()
        self.storage_manager.data_connections["measurements"].append_data(
            data_row
        )


    def is_valid_rating(self, rating_name):
        return rating_name in self.config["ratings"].keys()

    def rate_artifact(self, artifact_id, rating_name, rating):
        if not self.is_valid_rating(rating_name):
            valid_ratings = list(self.config["ratings"].keys())
            raise InvalidRatingError(
                f"Invalid rating '{rating_name}' for experiment "
                f"{self.config["experiment"]['experiment_id']}. "
                f"Valid ratings are: {valid_ratings}"
            )

        measurement_record = self.build_measurement_record(
            artifact_id, 
            rating_name,
            rating
        )
        measurement_record = self.GenerationRecordClass(
            schema=MeasurementSchema,
            generation_metadata = measurement_record
        )
        self.save_rating(measurement_record)
