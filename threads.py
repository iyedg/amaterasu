import threading
from loguru import logger
import queue
import pafy
import cv2
import time
import numpy as np


BUF_SIZE = 10
SENTINEL = object()
q = queue.Queue(BUF_SIZE)
q2 = queue.Queue(BUF_SIZE)


class ProducerThread(threading.Thread):
    def __init__(
        self, url, fr=24, target=None, name=None, *args, **kwargs,
    ):
        super().__init__()
        self.target = target
        self.name = name
        self.video = pafy.new(url).getbest().url
        self.cap = cv2.VideoCapture(self.video)
        self.current_frame = 0
        self.produced_frames = 0
        self.fr = fr

    def run(self):
        while True:
            # success = self.cap.grab()
            success, frame = self.cap.read()
            if not success:
                q.put(SENTINEL)
                break
            else:
                self.current_frame += 1
            if not self.current_frame % self.fr == 0 or self.current_frame == 1:
                continue
            # frame = self.cap.retrieve()
            if not q.full():
                q.put(frame)
                logger.debug(
                    f"Putting frame {self.current_frame} : {q.qsize()} items in queue | {threading.currentThread().getName()}"
                )
                self.produced_frames += 1
        logger.error(f"Done producing {self.produced_frames} frames")


class ConsumerThread(threading.Thread):
    def __init__(
        self, target=None, name=None, *args, **kwargs,
    ):
        super().__init__()
        self.target = target
        self.name = name

    def run(self):
        flag = True
        while True:
            if not q.empty():
                item = q.get()
                if item is SENTINEL:
                    logger.error(
                        f"Nothing to read | {threading.currentThread().getName()}"
                    )
                    q.task_done()
                    q2.put(SENTINEL)
                    break

                logger.info(
                    f"Getting item : {q.qsize()} items in queue | {threading.currentThread().getName()}"
                )
                rgb_frame = item[:, :, ::-1]
                q2.put(rgb_frame)
                q.task_done()

