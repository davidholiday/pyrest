from flask import Flask, json
app = Flask(__name__)

@app.route("/healthcheck")
def ping():
    return json.jsonify(status="OK")
