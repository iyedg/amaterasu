import threading
import uuid
import queue

import cv2
import pafy
from blinker import signal
from loguru import logger
from cute_names import cute_name

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
        sink_queue,
        name=cute_name(),
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
        self.name = name
        self.chunk_size = chunk_size
        DOWNLOADER_STOP_EVT.connect(self.on_kill)

    def run(self):
        DOWNLOADER_STARTED_EVT.send(self)
        video_stream_url = pafy.new(self.youtube_link).getbest().url
        capture = cv2.VideoCapture(video_stream_url)
        while True:
            buffer = []
            if not self.killer_queue.empty():
                if self.killer_queue.get_nowait() == SENTINEL:
                    DOWNLOADER_EO_STREAM_EVT.send(self)
                    break
            if len(buffer) <= self.chunk_size:
                success, frame = capture.read()
                ts = capture.get(cv2.CAP_PROP_POS_MSEC)
                if not success:
                    self.sink_queue.put(SENTINEL)
                    break
                else:
                    self.current_frame += 1
                if (
                    self.current_frame % (self.frame_skip + 1) == 0
                    or self.current_frame == 1
                ):
                    resized_frame = cv2.resize(src=frame, dsize=(480, 320))
                    buffer.append({"frame": resized_frame, "timestamp": ts})
            self.sink_queue.put(buffer)

    def __iter__(self):
        for item in iter(self.sink_queue.get, SENTINEL):
            yield item

    def on_kill(self, sender):
        logger.debug(f"{DOWNLOADER_STOP_EVT} received")
        self.killer_queue.put(SENTINEL)

    @staticmethod
    def active_downloaders():
        active_downloaders = [
            t for t in threading.enumerate() if isinstance(t, DownloaderThread)
        ]
        return active_downloaders
