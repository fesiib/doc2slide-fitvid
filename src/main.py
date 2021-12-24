from flask import Flask
from flask_cors import CORS
from flask import request

import json
import numpy as np

from adaptation import adapt_example_slide
from process import process_example

app = Flask(__name__)
CORS(app, origins = ["http://localhost:3000"])

app.config["UPLOAD_EXTENSIONS"] = [".pdf", ".jpg", ".png"]

# Generate Requests
@app.route("/example_adaptation/generate_slide_requests", methods=["POST"])
def adapt_example_route():
    decoded = request.data.decode('utf-8')

    requestJSON = json.loads(decoded)

    slide_info = requestJSON["slide_info"]
    example_info = requestJSON["example_info"]

    requests = adapt_example_slide(slide_info, example_info)

    responseJSON = {
        "requests": requests,
        "status": "success",
    }
    return json.dumps(responseJSON)

# Process Example
@app.route("/example_adaptation/process_example", methods=["POST"])
def process_example_route():
    decoded = request.data.decode('utf-8')

    requestJSON = json.loads(decoded)

    url = requestJSON['url']
    example_id = requestJSON['example_id']
    example_deck_id = requestJSON['example_deck_id']

    example_info = process_example(url, example_deck_id, example_id)

    responseJSON = {
        "example_info": example_info,
        "status": "success",
    }
    return json.dumps(responseJSON)

# Process Example Design
@app.route("/example_adaptation/process_example_design", methods=["POST"])
def process_example_design_route():
    decoded = request.data.decode('utf-8')

    requestJSON = json.loads(decoded)

    url = requestJSON['url']
    slide_id = requestJSON['slide_id']
    slide_deck_id = requestJSON['slide_deck_id']

    example_info = process_example(url, slide_deck_id, slide_id)

    responseJSON = {
        "example_info": example_info,
        "status": "success",
    }
    return json.dumps(responseJSON)



def main():
    app.run(host="0.0.0.0", port=7777)

if __name__ == "__main__":
    main()