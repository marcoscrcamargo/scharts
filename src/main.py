from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import plotly.express as px
import pandas as pd
import os

CHARTS = {
    "scatter": {"f": px.scatter, "required": {"x", "y"}, "optional": {"size", "color", "title"}},
    "line": {"f": px.line, "required": {"x", "y"}, "optional": {"color", "title"}},
    "bar": {"f": px.bar, "required": {"x", "y"}, "optional": {"color", "title"}},
}


def get_kwargs(body, charts):
    chart_name = body.get("chart")
    chart = charts.get(chart_name)

    try:
        kwargs = {"data_frame": pd.DataFrame(body["data"])}
    except KeyError as e:
        raise Exception(f"Missing {e}")

    for req in chart["required"]:
        try:
            kwargs[req] = body[req]
        except KeyError as e:
            raise Exception(f"Missing {e}")

    for opt in chart["optional"]:
        if opt in body:
            kwargs[opt] = body[opt]
    return kwargs, chart


def export_chart(kwargs, chart, fname):
    fig = chart["f"](**kwargs)
    fig.write_image(fname)


app = FastAPI()


class Chart(BaseModel):
    data: dict
    chart: str
    image_name: str
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None


@app.post("/charts")
def gen_chart(body: Chart):
    os.makedirs("images", exist_ok=True)
    fname = f"images/{body.image_name}.png"
    kwargs, chart = get_kwargs(vars(body), CHARTS)
    export_chart(kwargs, chart, fname)
    return {"image": fname}
