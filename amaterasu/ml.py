import face_recognition
import numpy as np
import joblib
from loguru import logger
from pyprojroot import here
from PIL import Image, ImageDraw

model = joblib.load(here("models/knn.model"))


def draw_locations(image_array, locations):
    image = Image.fromarray(image_array)
    for location in locations:
        draw = ImageDraw.Draw(image)
        t, r, b, l = location
        draw.rectangle([r, t, l, b], outline="red")
    return image


def predict(frame, threshold=0.6):
    face_locations = face_recognition.face_locations(frame)
    if len(face_locations) == 0:
        logger.error("No faces detected")
        return
    if len(face_locations) > 1:
        logger.warning("Multiple faces detected, using the first face")

    face_encoding = face_recognition.face_encodings(frame, face_locations)
    model_prediction = model.predict(face_encoding)
    prediction_distance_to_neighbors = model.kneighbors(face_encoding)
    average_distance = np.mean(prediction_distance_to_neighbors[0])
    if average_distance <= threshold:
        return model_prediction
    else:
        # return model.predict_proba(face_encoding)
        return "Unrecognized"
    logger.debug(model_prediction)
    logger.debug(prediction_distance_to_neighbors)
