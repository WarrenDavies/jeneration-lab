from abc import ABC


class Variable(ABC):
    """
    """
    def __init__(self, config):
        """
        """
        self.dtype = config["dtype"]

    def values(self):
        """
        """
        raise NotImplementedError
        