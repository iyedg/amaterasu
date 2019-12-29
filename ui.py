import json

import cv2
import pafy
import requests
import streamlit as st
from loguru import logger

st.title("Amaterasu")

youtube_link = st.sidebar.text_input(
    "YouTube Link", "https://www.youtube.com/watch?v=ns6BqrV9Ppk&t=10s"
)

video_stream_url = pafy.new(youtube_link).getbest().url

cap = cv2.VideoCapture(video_stream_url)

frame_display = st.empty()
response_display = st.sidebar.empty()

current_frame = 0
while True:
    # Reading the first 2000 frames
    ret, frame = cap.read()
    if ret:
        current_frame += 1
        if current_frame % 60 == 0 or current_frame == 1:
            response = requests.post(
                "http://localhost:5000/recognize", json={"frame": frame.tolist()}
            )
            response_display.json(json.loads(response.content))
            frame_display.image(frame, channels="BGR", use_column_width=True)
        else:
            continue
    else:
        break
