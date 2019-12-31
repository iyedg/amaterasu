import cProfile
import io
import pstats
import queue
import threading
import time

import numpy as np
import streamlit as st
from loguru import logger

from threaded_io import (
    DOWNLOADER_STARTED_EVT,
    DOWNLOADER_STOP_EVT,
    SENTINEL,
    DownloaderThread,
)

# TODO: use a queue per downloader instance and delete on kill
DOWNLOAD_QUEUE_SIZE = 300

st.sidebar.title("Amaterasu")
status = st.sidebar.empty()
frame_display = st.empty()
youtube_link = st.sidebar.text_input(
    "YouTube Link", "https://www.youtube.com/watch?v=ns6BqrV9Ppk&t=10s"
)
every = st.sidebar.slider("Process a frame out of every", 0, 50, 15)
queue_size = st.sidebar.progress(0)
queue_size_txt = st.sidebar.empty()
active_threads_count = st.sidebar.empty()
active_threads = st.sidebar.empty()
response_display = st.sidebar.empty()
kill_button = st.sidebar.button("Kill")


def update_status(sender):
    status.info("Subscribe")


DOWNLOADER_STARTED_EVT.connect(update_status)


pr = cProfile.Profile()
pr.enable()

sink = queue.Queue(DOWNLOAD_QUEUE_SIZE)
downloader = DownloaderThread(
    youtube_link, sink_queue=sink, frame_skip=every, chunk_size=120
)
downloader.start()

for chunk in iter(sink.get, SENTINEL):
    if kill_button:
        DOWNLOADER_STOP_EVT.send(__name__)
        break
    for frame_info in chunk:
        frame, ts = frame_info.values()
        timestamp = time.strftime("%H:%M:%S", time.gmtime(ts / 1000))
        frame_display.image(
            np.array(frame, dtype=np.uint8), channels="BGR", caption=timestamp
        )
        queue_size.progress(sink.qsize() / DOWNLOAD_QUEUE_SIZE)
        queue_size_txt.markdown(
            f"Sink queue has {downloader.chunk_size * sink.qsize()}"
            f" unprocessed frames"
        )
        active_threads_count.markdown(
            f"{len(downloader.active_downloaders())} active downloaders"
        )
        active_threads.markdown(
            "\n".join([f"* {t.getName()}" for t in downloader.active_downloaders()])
        )

queue_size.progress(sink.qsize() / DOWNLOAD_QUEUE_SIZE)
queue_size_txt.markdown(
    f"Sink queue has {downloader.chunk_size * sink.qsize()}" f" unprocessed frames"
)
active_threads_count.markdown(
    f"{len(downloader.active_downloaders())} active downloaders"
)
active_threads.markdown(
    "\n".join([f"* {t.getName()}" for t in downloader.active_downloaders()])
)
logger.debug(f"{threading.enumerate()}")

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats()
logger.debug(s.getvalue())
