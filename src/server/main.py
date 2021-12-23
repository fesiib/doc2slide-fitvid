from flask import Flask
from flask_cors import CORS
from flask import request

import json
import numpy as np

from parser import get_image_np
from adaptation import adapt_slide

app = Flask(__name__)
CORS(app, origins = ["http://localhost:3000"])

app.config["UPLOAD_EXTENSIONS"] = [".pdf", ".jpg", ".png"]

@app.route("/slide_adaptation/slide", methods=["POST"])
def adapt_slide_route():
    decoded = request.data.decode('utf-8')

    requestJSON = json.loads(decoded)

    url = requestJSON['url']

    adapt_slide(get_image_np(url))

    responseJSON = {
        "status": "success",
    }

    return json.dumps(responseJSON)

def main():
    app.run(host="0.0.0.0", port=7777)

if __name__ == "__main__":
    main()