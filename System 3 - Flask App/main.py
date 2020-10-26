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
    
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        # grab filename
        filename = request.files["file"].filename
        fcln = request.form["fcln"]
        cnss = request.form["cnss"]

        if filename == "":
            # nothing is uploaded
            flash("empty upload")
            return render_template("home.html")
        if fcln == "" or cnss == "":
            flash("please fill in all text")
            return render_template("home.html")

        # some file is entered
        # check it is the valid file type
        if not (allowed_file(filename)):
            flash("wrong file type")
            return render_template("home.html")

        # file is submitted and file type is correct so now grab the file
        # to do - permission error when trying to save file to uploads folder
        filename_secure = secure_filename(filename)
        request.files["file"].save(os.path.join(upload_path, filename_secure))

        # run external python module
        tax_charter.create_Tax_Charter(filename_secure, fcln, cnss)

        # download
    return render_template("home.html", filename=filename_secure)
    
    
if __name__ == "__main__":
    app.run(debug=True)