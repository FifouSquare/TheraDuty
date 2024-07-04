from flask import Flask, request, jsonify

app = Flask(__name__)
data = {"x": 0, "y": 0, "pinch": False}


@app.route("/", methods=["POST"])
def update_data():
    global data
    data = request.get_json()
    return jsonify(data), 200


@app.route("/", methods=["GET"])
def get_data():
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(port=8080)
