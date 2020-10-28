import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

path = os.path.dirname(os.path.abspath(__file__))
try:
    os.mkdir("uploads")
except FileExistsError:
    pass

upload_path = path + "/uploads/"
download_path = path + "/outputs/"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# home page
@app.route("/")
def home():
    analysis_complete = False
    return render_template("home.html",analysis_complete=analysis_complete)
    
@app.route("/upload", methods=["GET", "POST"])
def upload():
    analysis_complete = False

    if request.method == "POST":
        # grab filename
        unbound_filename = request.files["unbound_file"].filename
        bound_filename = request.files["bound_file"].filename
        compound_file = request.files["compound_file"].filename

        if unbound_filename == "" or bound_filename == "" or compound_file == "":
            # nothing is uploaded
            flash("Please upload all required files")
            return render_template("home.html", analysis_complete=analysis_complete)

        # some file is entered
        # check it is the valid file type
        allowed_files_mask = allowed_file(unbound_filename) and allowed_file(bound_filename) and allowed_file(compound_file)
        if not allowed_files_mask:
            flash("Wrong File Type. Please only upload xlsx files. ")
            return render_template("home.html", analysis_complete=analysis_complete)

        # file is submitted and file type is correct so now grab the file
        # to do - permission error when trying to save file to uploads folder
        download_uploaded_file(bound_filename, request, "bound_file")
        download_uploaded_file(unbound_filename, request, "unbound_file")
        download_uploaded_file(compound_file, request, "unbound_file")

        # run external python module
        

        # download
        analysis_complete = True

    return render_template("home.html", analysis_complete=analysis_complete)

def download_uploaded_file(filename, request, file_id):
    filename_secure = secure_filename(filename)
    request.files[file_id].save(os.path.join(upload_path, filename_secure))
    

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename): 
    # Appending app path to upload folder path within app root folder
    outputs = os.path.join(path, download_path)
    # Returning file from appended path
    return send_from_directory(directory=outputs, filename=filename)
    
    
if __name__ == "__main__":
    app.run(debug=True)