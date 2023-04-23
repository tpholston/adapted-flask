from flask import Flask, jsonify
application = Flask(__name__)

@application.route("/")
def hello_world():
    return jsonify({"message": "Hello, World!"})