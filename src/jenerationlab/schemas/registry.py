REGISTRY = {}

def register(name):
    """
    A decorator factory used to register a subclass.

    The decorated class is stored in the global REGISTRY dictionary
    under the provided `name`.

    Args:
        name (str): The string key used to reference the class
                    in the config.

    Returns:
        Callable: A decorator function that takes a class and registers it.
    """
    def decorator(cls):
        REGISTRY[name] = cls
        return cls
    return decorator


def get_schema_class(name):
    """
    Retrieves and instantiates the correct class based on the
    configuration dictionary.

    It looks up the class in REGISTRY using the key found in
    `name`.

    Args:
        name (str): a key corresponding to a registered class name.

    Returns:
        BaseClass: An instantiated object of the registered class.

    Raises:
        KeyError: If the `name` is not found in the REGISTRY.
    """
    SchemaClass = REGISTRY[name]

    return SchemaClass