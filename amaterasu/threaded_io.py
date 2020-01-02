import queue
import threading
import time

import cv2
import pafy
from blinker import signal
from loguru import logger

from amaterasu.cute_names import cute_name

SENTINEL = object()

DOWNLOADER_STARTED_EVT = signal("DOWNLOADER_STARTED_EVT")
DOWNLOADER_EO_STREAM_EVT = signal("DOWNLOADER_EO_STREAM_EVT")
DOWNLOADER_STOP_EVT = signal("DOWNLOADER_STOP_EVT")


READER_EMPTY_DOWNLOADER_QUEUE_EVT = signal("READER_EMPTY_DOWNLOADER_QUEUE_EVT")
READER_STARTED_EVT = signal("READER_STARTED_EVT")
READER_RECEIVED_FRAME_EVT = signal("READER_RECEIVED_FRAME_EVT")


class DownloaderThread(threading.Thread):
    def __init__(
        self,
        youtube_link,
        sink_queue,  # TODO: crate own sink
        name=None,
        frame_skip=0,
        daemon=True,
        chunk_size=120,
    ):
        super().__init__()
        self.youtube_link = youtube_link
        self.current_frame = 0
        self.frame_skip = frame_skip
        self.sink_queue = sink_queue
        self.killer_queue = queue.Queue(1)
        self.daemon = daemon
        self.chunk_size = chunk_size
        if name is None:
            name = cute_name()
        self.name = name
        DOWNLOADER_STOP_EVT.send(self)
        time.sleep(1)
        DOWNLOADER_STOP_EVT.connect(self.on_kill)

    def run(self):
        DOWNLOADER_STARTED_EVT.send(self)
        logger.debug(f"{self.name} is Downloading {self.youtube_link}")
        video_stream_url = pafy.new(self.youtube_link).getbest().url
        logger.debug(f"{self.name} started capturing video")
        capture = cv2.VideoCapture(video_stream_url)
        while True:
            buffer = []
            if not self.killer_queue.empty():
                if self.killer_queue.get_nowait() == SENTINEL:
                    self.sink_queue.put(SENTINEL)
                    DOWNLOADER_EO_STREAM_EVT.send(self)
                    break
            if len(buffer) <= self.chunk_size:
                success, frame = capture.read()
                ts = capture.get(cv2.CAP_PROP_POS_MSEC)
                if not success:
                    self.sink_queue.put(SENTINEL)
                    DOWNLOADER_EO_STREAM_EVT.send(self)
                    break
                else:
                    self.current_frame += 1
                if (
                    self.current_frame % (self.frame_skip + 1) == 0
                    or self.current_frame == 1
                ):
                    logger.debug(f"{self.name} successfully received frame")
                    resized_frame = cv2.resize(src=frame, dsize=(640, 480))
                    buffer.append({"frame": resized_frame, "timestamp": ts})
            self.sink_queue.put(buffer)
        self.sink_queue.put(SENTINEL)
        logger.warning(f"{self.name} has finished")
        DOWNLOADER_EO_STREAM_EVT.send(self)

    def __iter__(self):
        for item in iter(self.sink_queue.get, SENTINEL):
            yield item

    def on_kill(self, sender):
        if isinstance(sender, DownloaderThread):
            if sender.name != self.name:
                logger.warning(f"{self.name} killed by {sender.name}")
                self.killer_queue.put(SENTINEL)
        else:
            logger.warning(f"{self.name} killed by {sender}")
            self.killer_queue.put(SENTINEL)

    @staticmethod
    def active_downloaders():
        active_downloaders = [
            t for t in threading.enumerate() if isinstance(t, DownloaderThread)
        ]
        return active_downloaders
