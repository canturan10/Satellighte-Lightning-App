"""This module implements the demo for Satellighte library.
"""
import logging
from rich.logging import RichHandler
import satellighte as sat
from PIL import Image

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger(__name__)


class SatellighteDemo:
    def __init__(self):
        self.model = {}
        for model in sat.available_models():
            for version in sat.get_model_versions(model):
                self.model[f"{model}-{version}"] = sat.Classifier.from_pretrained(
                    model,
                    version,
                )
                self.model[f"{model}-{version}"].eval()
                print(f"Loaded {model}-{version}")

    def predict(self, image: Image.Image, name: str) -> str:
        res = self.model[name].predict(image)[0]
        return res
