


class BenchmarkingManager():
    """
    """
    def __init__(self, benchmarking_config):
        self.benchmarking_config = benchmarking_config


    def remove_message_variables(self, variables):
        return [
            variable
            for variable in variables
            if variable.name != "messages"
        ]


    def create_cases(self):
        self.cases = self.benchmarking_config["cases"]
