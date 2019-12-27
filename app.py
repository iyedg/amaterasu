import sys
import time

import multiprocessing
import cv2
import dash
import dash_core_components as dcc
import dash_html_components as html
import face_recognition
import joblib
import jupyterlab_dash
import matplotlib.pyplot as plt
import numpy as np
import pafy
from dash.dependencies import Input, Output, State
from pyprojroot import here
from loguru import logger
from src.capture import VideoCaptureThreading
import dash_player as player
from threads import ProducerThread, ConsumerThread, q2, SENTINEL
from src.utils import fig_to_uri
import threading

# def face_distance(x, y):
#     return np.linalg.norm(x - y)


# model = joblib.load(here("../arp_tn_face_recognition/data/models/knn.model"))

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [
        html.Img(id="photo"),
        html.Label(id="prediction_label", children=["Prediction"]),
        html.Label("YouTube URL"),
        dcc.Input(id="url", type="url"),
        html.Button(id="start", children=["Recognize"]),
        html.Label("Detection accuracy threshold (lower is more strict)"),
        dcc.Slider(
            id="threshold",
            min=0,
            max=1,
            step=0.1,
            value=0.6,
            marks={i: f"{i}" for i in np.round(np.arange(0, 1, 0.1), 2)},
        ),
        dcc.Interval(id="ticker", interval=1.2 * 1000),
    ],
    style={"columnCount": 2},
)


@app.callback(Output("photo", "src"), [Input("ticker", "n_intervals")])
def recognize(n_intervals):
    # model = joblib.load(here("data/models/knn.model"))
    next_frame = q2.get()
    while not next_frame is SENTINEL:
        logger.info(f"Procssing incoming frame | {threading.currentThread().getName()}")
        fig = plt.Figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(next_frame)
        encoded_image = fig_to_uri(fig)
        q2.task_done()
        return encoded_image
    return (
        "https://pbs.twimg.com/profile_images/1112915256219758592/6lffJkCG_400x400.png"
    )


if __name__ == "__main__":
    p = ProducerThread(
        name="producer",
        daemon=True,
        # url="https://www.youtube.com/watch?v=qcp7yyYMTc4",
        # url="https://www.youtube.com/watch?v=c_FZbfXq5VM",
        url="https://www.youtube.com/watch?v=1Yr2gtTq5R0",
        # url="https://www.youtube.com/watch?v=668nUCeBHyY",
        # url="https://www.youtube.com/watch?v=oRtyPpuMHso",
        fr=30,
    )
    c = ConsumerThread(name="consumer", daemon=True)

    p.start()
    c.start()
    app.run_server(debug=True, threaded=True)
