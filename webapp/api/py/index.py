from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/api/py/health')
def health():
    return jsonify({
        "status": "OK",
        "message": "Minimal Flask engine is up",
        "python": sys.version
    })

@app.route('/api/py/test')
def test():
    return jsonify({"test": "success"})

# This handles the root of the function if needed
@app.route('/')
def root():
    return jsonify({"message": "Python engine root"})
