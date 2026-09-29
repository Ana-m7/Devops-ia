import os, socket
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from a container built without Docker!"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/whoami")
def whoami():
    return jsonify(hostname=socket.gethostname(), uid=os.getuid())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
