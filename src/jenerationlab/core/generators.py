from imagejenerator.models import registry as image_model_registry
from textjenerator.models import registry as text_model_registry

generator_registries = {
    "text": text_model_registry,
    "image": image_model_registry,
}
