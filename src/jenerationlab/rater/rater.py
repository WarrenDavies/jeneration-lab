import uuid
import datetime

from jenerationutils.jenerationrecord import registry as recorder_registry

from jenerationlab.schemas.measurements import MeasurementSchema
from jenerationlab.metrics.base_metrics_manager import BaseMetricsManager


class InvalidRatingError(Exception):
    pass


class Rater(BaseMetricsManager):
    """
    """
    def __init__(self, core_config, experiment_config, storage_manager):
        super().__init__(core_config, experiment_config, storage_manager)
        self.producer = "human"


    def get_queue(self, rating_name):
        queue = self._get_queue_impl(rating_name)
        queue.sort()
        print(queue)
        return queue


    def is_valid_rating(self, rating_name):
        return rating_name in self.experiment_config["ratings"].keys()


    def get_question(self, rating_name):
        return self.experiment_config["ratings"][rating_name]["question"]


    def rate_artifact(self, artifact_id, rating_name, rating):
        if not self.is_valid_rating(rating_name):
            valid_ratings = list(self.experiment_config["ratings"].keys())
            raise InvalidRatingError(
                f"Invalid rating '{rating_name}' for experiment "
                f"{self.experiment_config["experiment"]['experiment_id']}. "
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
        self.save_metric(measurement_record)
