from loguru import logger
import json
import logging

import face_recognition
import joblib
import numpy as np
from flask import Flask, Response, request, stream_with_context
from flask.logging import default_handler
from pyprojroot import here


model_path = here("../arp_tn_face_recognition/data/models/knn.model")
model = joblib.load(model_path)

app = Flask(__name__)


@app.route("/recognize", methods=["POST"])
def recognize():
    posted_data = request.get_json(force=True)
    frame = np.array(posted_data.get("frame"), dtype=np.uint8)[:, :, ::-1]
    fls = face_recognition.face_locations(frame)
    logger.debug(f"{len(fls)} faces detected")
    if len(fls) > 0:
        fes = face_recognition.face_encodings(frame, fls)
        prediction = model.predict(fes)
        logger.info(prediction)
        return json.dumps({"prediction": prediction.tolist()})
    return json.dumps({"prediction": None})


if __name__ == "__main__":
    app.run(debug=True)
