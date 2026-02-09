DEFAULT_CONFIG = {
    "cases": [
        {"case_id": None}
    ]
}


class BenchmarkingManager():
    """
    """
    def __init__(self, benchmarking_config = DEFAULT_CONFIG):
        self.benchmarking_config = benchmarking_config


    def remove_message_variables(self, variables):
        return [
            variable
            for variable in variables
            if variable.name != "messages"
        ]


    def create_cases(self):
        self.cases = self.benchmarking_config["cases"]
        if "benchmark_system_prompt" in self.benchmarking_config:
            for case in self.cases:
                case["messages"] = [self.benchmarking_config["benchmark_system_prompt"]] + case["messages"]
