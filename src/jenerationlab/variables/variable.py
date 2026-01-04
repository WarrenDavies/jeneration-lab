from abc import ABC


class Variable(ABC):
    """
    """
    def __init__(self, config):
        """
        """
        self.dtype = config["dtype"]
        self.min = config["min"]
        self.max = config["max"]

    def values(self):
        """
        """
        raise NotImplementedError
        