REGISTRY = {}

def register_model(name):
    """
    """
    def decorator(cls):
        REGISTRY[name] = cls
        return cls
    return decorator


def get_model_class(config):
    ModelClass = REGISTRY[config["model"]]
    image_generator = ModelClass(config)

    return image_generator


def get_object(config):
    """
    Retrieves and instantiates the correct class based on the config 
    dictionary.

    It looks up the class in REGISTRY using `config["dtype"]`

    Args:
        config (dict): The configuration dictionary, which must contain a
                       key named `config["dtype"]` corresponding to a registered 
                       class name.

    Returns:
        An instantiated object of the registered class.

    Raises:
        KeyError: If the value of `config["dtype"]` is not found 
                  in the REGISTRY.
    """
    Class_ = REGISTRY[config["dtype"]]
    object_ = Class_(config)

    return object_