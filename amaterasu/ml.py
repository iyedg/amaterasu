import face_recognition
import numpy as np
import joblib
from loguru import logger
from pyprojroot import here

model = joblib.load(here("../arp_tn_face_recognition/data/models/knn.model"))


def predict(frame, threshold=0.6):
    face_locations = face_recognition.face_locations(frame)
    if len(face_locations) == 0:
        logger.error("No faces detected")
        return
    if len(face_locations) > 1:
        logger.warning("Multiple faces detected, using the first face")
    try:
        face_encoding = face_recognition.face_encodings(frame, face_locations)
        if len(face_encoding) > 1:
            face_encoding = face_encoding[0]
        model_prediction = model.predict(face_encoding)
        prediction_distance_to_neighbors = model.kneighbors(face_encoding)
        average_distance = np.mean(prediction_distance_to_neighbors[0])
        if average_distance <= threshold:
            return model_prediction
        else:
            # return model.predict_proba(face_encoding)
            return "Unrecognized"
    except Exception as e:
        logger.error(e)
        return "ERROR"
    logger.debug(model_prediction)
    logger.debug(prediction_distance_to_neighbors)
