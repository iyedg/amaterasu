import cv2
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pafy
from flask import Flask, Response
from pyprojroot import here

from src.utils import fig_to_uri
from src.base_camera import BaseCamera
import os


class Camera(BaseCamera):
    video_source = 0

    def __init__(self, video_source):
        self.set_video_source(pafy.new(video_source).getbest().url)
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError("Could not start camera.")

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode(".jpg", img)[1].tobytes()


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


server = Flask(__name__)
app = dash.Dash(__name__, server=server)


@server.route("/video_feed")
def video_feed():
    return Response(
        # gen(Camera("https://www.youtube.com/watch?v=HdDCR8CfQ9g")),
        gen(Camera(str(here("data/raw/hamilton.mp4")))),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


app.layout = html.Div([html.H1("Webcam Test"), html.Img(src="/video_feed")])

if __name__ == "__main__":
    app.run_server(debug=True)
