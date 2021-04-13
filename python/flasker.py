from flask import Flask, request
import subnetcalc

app = Flask(__name__)

@app.route('/', methods=['POST'])
def wrapper():
    return subnetcalc.on_event(request)