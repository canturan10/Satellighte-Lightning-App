import logging
import os
from typing import Dict, List, Optional

import lightning as L
from lightning.app.frontend.web import StaticWebFrontend
from poster import Poster
from rich import print
from rich.logging import RichHandler


from research_app.components.model_demo import ModelDemo
from research_app.utils import clone_repo, notebook_to_html

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger(__name__)


class StaticNotebookViewer(L.LightningFlow):
    def __init__(self, notebook_path: str):
        super().__init__()
        self.serve_dir = notebook_to_html(notebook_path)

    def configure_layout(self):
        return StaticWebFrontend(serve_dir=self.serve_dir)


class ResearchApp(L.LightningFlow):
    """Share your paper "bundled" with the arxiv link, poster, live jupyter notebook, interactive demo to try the model
    and more!

    poster_dir: folder path of markdown file. The markdown will be converted into a poster and launched as static
        html.
    blog: [Optional] Link to a blog post for your research
    github: [Optional] Clone GitHub repo to a temporary directory.
    training_log_url: [Optional] Link for experiment manager like wandb or tensorboard
    notebook_path: [Optional] View a Jupyter Notebook as static html tab
    launch_jupyter_lab: Launch a full-fledged Jupyter Lab instance. Note that sharing Jupyter publicly is not
        recommended and exposes security vulnerability to the cloud. Defaults to False.
    launch_gradio: Launch Gradio demo. Defaults to False. You should update the
        `research_app/components/model_demo.py` file to your use case.
    tab_order: You can optionally reorder the tab layout by providing a list of tab name.
    """

    def __init__(
        self,
        poster_dir: str,
        blog: Optional[str] = None,
        github: Optional[str] = None,
        launch_gradio: bool = False,
        tab_order: Optional[List[str]] = None,
    ) -> None:

        super().__init__()
        self.poster_dir = os.path.abspath(poster_dir)
        self.blog = blog
        self.model_demo = None
        self.poster = Poster(resource_dir=self.poster_dir)
        self.tab_order = tab_order

        if github:
            clone_repo(github)

        if launch_gradio:
            self.model_demo = ModelDemo()

    def run(self) -> None:
        if os.environ.get("TESTING_LAI"):
            print("⚡ Lightning Research App! ⚡")
        self.poster.run()

        if self.model_demo:
            self.model_demo.run()

    def configure_layout(self) -> List[Dict[str, str]]:
        tabs = []

        tabs.append({"name": "Poster", "content": self.poster.url + "/poster.html"})

        if self.blog:
            tabs.append({"name": "Blog", "content": self.blog})

        if self.model_demo:
            tabs.append({"name": "Model Demo", "content": self.model_demo.url})

        return self._order_tabs(tabs)

    def _order_tabs(self, tabs: List[dict]):
        """Reorder the tab layout."""
        if self.tab_order is None:
            return tabs
        order_int: Dict[str, int] = {e.lower(): i for i, e in enumerate(self.tab_order)}
        try:
            return sorted(tabs, key=lambda x: order_int[x["name"].lower()])
        except KeyError as e:
            logger.error(
                f"One of the key '{e.args[0]}' that you passed as `tab_order` argument is missing or incorrect. "
                f"Please check {tabs}"
            )


if __name__ == "__main__":
    poster_dir = "resources/poster"
    blog = "https://canturan10.github.io/satellighte/"
    github = "https://github.com/canturan10/satellighte"
    tabs = ["Poster", "Blog", "Model Demo"]

    app = L.LightningApp(
        ResearchApp(
            poster_dir=poster_dir,
            blog=blog,
            launch_gradio=True,
            tab_order=tabs,
        ),
    )
