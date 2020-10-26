from flask import Flask
app = Flask(__name__)

@app.route('/')
def welcome():
    return 'Tool for Binding Site Prediction'