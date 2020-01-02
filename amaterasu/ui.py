from pyinstrument import Profiler
import face_recognition
import queue
import time

import numpy as np
import streamlit as st
from loguru import logger

from amaterasu.threaded_io import (
    DOWNLOADER_STARTED_EVT,
    DOWNLOADER_STOP_EVT,
    DownloaderThread,
)
from amaterasu.ml import predict, draw_locations


def update_status(sender):
    logger.debug("Subs")


DOWNLOAD_QUEUE_SIZE = 300


# TODO: quality chooser
# TODO: user initiated processing


def main():
    DOWNLOADER_STOP_EVT.send(__name__)
    DOWNLOADER_STARTED_EVT.connect(update_status)
    sink = queue.Queue(DOWNLOAD_QUEUE_SIZE)

    frame_display = st.empty()
    youtube_link = st.sidebar.text_input(
        "YouTube Link", "https://www.youtube.com/watch?v=c_FZbfXq5VM&t=66s"
    )
    every = st.sidebar.slider("Process a frame out of every", 0, 50, 10)
    queue_size = st.sidebar.progress(0)
    queue_size_txt = st.sidebar.empty()
    active_threads_count = st.sidebar.empty()
    active_threads = st.sidebar.empty()
    kill_button = st.sidebar.button("Kill")
    downloader = DownloaderThread(
        youtube_link, sink_queue=sink, frame_skip=every, chunk_size=1000
    )
    downloader.start()

    for chunk in downloader:
        if kill_button:
            DOWNLOADER_STOP_EVT.send(__name__)
            break
        for frame_info in chunk:
            frame, ts = frame_info.values()
            timestamp = time.strftime("%H:%M:%S", time.gmtime(ts / 1000))
            prediction = predict(frame)
            frame_display.image(
                draw_locations(
                    np.array(frame, dtype=np.uint8),
                    face_recognition.face_locations(
                        frame
                    ),  # TODO: used twice, DRY this
                ),
                channels="BGR",
                caption=f"{timestamp} | recognized {prediction}",
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


profiler = Profiler()
profiler.start()
main()
profiler.stop()
print(profiler.output_text(unicode=True, color=True))
