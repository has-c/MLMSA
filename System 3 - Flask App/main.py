import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

path = os.path.dirname(os.path.abspath(__file__))
try:
    os.mkdir("uploads")
except FileExistsError:
    pass

upload_path = path + "/uploads/"
download_path = path + "/output/"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# home page
@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        # grab filename
        filename = request.files["file"].filename

        if filename == "":
            # nothing is uploaded
            flash("empty upload")
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
        

        # download

    return render_template("home.html", filename=filename_secure)
    
    
#download code 
@app.route("/download/<filename>", methods=["GET", "POST"])
def download(filename):
    if filename != "":
        return send_file(download_path + filename + ".docx", as_attachment=True)
    else:
        return render_template("home.html")


@app.route("/download/", methods=["GET", "POST"])
def download_blank():
    return render_template("home.html")
    
    
if __name__ == "__main__":
    app.run(debug=True)