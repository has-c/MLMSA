import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads//'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

path = os.path.dirname(os.path.abspath(__file__))
try:
    os.mkdir("uploads")
except FileExistsError:
    logging.info("Output file already exists")
upload_path = path + "/uploads/"
download_path = path + "/output/"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# home page
@app.route("/")
def home():
    return render_template("welcome.html")
    
    
if __name__ == "__main__":
    app.run(debug=True)