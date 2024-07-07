from better_profanity import profanity
import cv2
from PIL import Image
import opennsfw2 as n2
from io import BytesIO
import numpy as np


def profanity_censor(text):
    return profanity.censor(text)

 

#Check and Blur Image 
def is_nsfw(image_array):

    img_pil = Image.fromarray(image_array)
    buffer = BytesIO()
    img_pil.save(buffer, format='JPEG')
    buffer.seek(0)

    predictions = n2.predict_images([buffer])
    print("Predictions:", predictions)
    
    if isinstance(predictions, (list, np.ndarray)):
        if isinstance(predictions[0], (list, np.ndarray)):
            score = predictions[0][0]
        else:
            score = predictions[0]
    elif isinstance(predictions, float):
        score = predictions
    else:
        raise TypeError("Unsupported prediction format")
    return score > 0.5

def blur_image(image_array):
    ksize = (101, 101) 
    sigmaX = 0
    return cv2.GaussianBlur(image_array, ksize, sigmaX)