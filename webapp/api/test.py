from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/api/test')
def test():
    return jsonify({
        "status": "OK",
        "python_version": sys.version,
        "message": "Simple Python test is working"
    })
