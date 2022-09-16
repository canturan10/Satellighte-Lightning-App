import logging

import gradio as gr
import satellighte as sat
from lightning.app.components.serve import ServeGradio
from research_app.satellite_demo import SatellighteDemo
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger(__name__)


class ModelDemo(ServeGradio):
    """Serve model with Gradio UI.

    You need to define i. `build_model` and ii. `predict` method and Lightning `ServeGradio` component will
    automatically launch the Gradio interface.
    """

    MODEL_LIST = []
    for model in sat.available_models():
        for version in sat.get_model_versions(model):
            MODEL_LIST.append(f"{model}-{version}")

    inputs = [
        gr.inputs.Image(label="Image"),
        gr.inputs.Dropdown(
            choices=MODEL_LIST,
            default=MODEL_LIST[0],
            label="Model",
        ),
    ]
    outputs = gr.outputs.Label()
    examples = [
        ["resources/eurosat_samples/AnnualCrop.jpg", "efficientnet_b0_eurosat-0"],
        ["resources/eurosat_samples/Forest.jpg", "mobilenetv2_default_eurosat-0"],
        ["resources/eurosat_samples/HerbaceousVegetation.jpg", "efficientnet_b0_eurosat-0"],
        ["resources/eurosat_samples/PermanentCrop.jpg", "mobilenetv2_default_eurosat-0"],
        ["resources/eurosat_samples/River.jpg", "mobilenetv2_default_eurosat-1"],
    ]
    enable_queue = True

    def __init__(self):
        super().__init__(parallel=True)

    def build_model(self) -> SatellighteDemo:
        logger.info("loading model...")
        satellighte = SatellighteDemo()
        logger.info("built model!")
        logger.info(satellighte)
        return satellighte

    def predict(self, query: str, name: str) -> str:
        return self._model.predict(query, name)


# model_demo = ModelDemo()
# model_demo.run()
