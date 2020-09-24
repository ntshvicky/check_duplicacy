# import the necessary packages
from skimage.metrics import structural_similarity
import matplotlib.pyplot as plt
import numpy as np
import cv2

from flask import Flask,jsonify,request

app = Flask(__name__)


def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err


def compare_images(imageA, imageB):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    score, diff = structural_similarity(imageA, imageB, multichannel=True,full=True)
    return score, diff, m


@app.route('/check_duplicacy',methods=['POST'])
def check_duplicacy():
    image1 = None
    image2 = None
    if 'image1' in request.files:
        image1 = request.files['image1']
    
    if 'image2' in request.files:
        image2 = request.files['image2']

    if image1 and image2:
        try:
            imageA = cv2.imdecode(np.fromstring(image1.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            imageB = cv2.imdecode(np.fromstring(image2.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            score, diff, m = compare_images(imageA, imageB)
            message = "Not similar"
            if score == 1.0 and m == 0:
                message = "Similar"

            resp = jsonify({"status": "success", "mean_square_error": "%.2f"% (m), "score": "%.2f"% (score), "message": message})
            resp.status_code = 401
            return resp
        except:
            resp = jsonify({'status': 'failed', 'message': 'Not similar'})
            resp.status_code = 401
            return resp
    else:
        resp = jsonify({'status': 'failed', 'message': 'Both images is mandatory for find similarity'})
        resp.status_code = 401
        return resp

if __name__ == '__main__':
    app.run(debug=True, port=5000)