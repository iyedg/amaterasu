import pafy
from loguru import logger
import cv2
import time
from datetime import datetime
import threading
import queue


def stream(url, q):
    # video = pafy.new(url, basic=False)
    # stream = video.getbest()
    # cap = cv2.VideoCapture(stream.url)
    # current_frame = 0
    while True:
        break
        ret, frame = cap.read()
        if not ret:
            logger.debug("No return, breaking the loop")
            break
        current_frame += 1
        if current_frame % 1 == 0 or current_frame == 1:
            logger.debug(f"Putting frame {current_frame} into queue")
            q.put(frame)
            logger.debug(f"Queue size is {q.qsize()}\nSleeping")
    for i in range(10):
        logger.debug(f"{i}th iteration")
        q.put(i)
        time.sleep(1)


if __name__ == "__main__":
    q = queue.Queue()
    t = threading.Thread(
        target=stream, args=("https://www.youtube.com/watch?v=-KWyh78xVII", q)
    )
    t.start()
    t.join()
    while not q.empty():
        q.get()
        logger.debug(f"Got frame, Queue size is {q.qsize()}")
    logger.debug("Queue empty")
