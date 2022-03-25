from flask import Flask, render_template, request, session, send_from_directory
from flask_cors import CORS
import json, uuid
import db
# import db
import datetime 


# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='', static_folder='2022DS_build')
application.secret_key = "super secret key"
CORS(application)

################################################################
###  Web Page endpoints
@application.route("/")
def Index():
    if 'PersonID' not in session:
        session["PersonID"] = str(uuid.uuid4())[:8]
    data={
        "name":"Tak"
    }
    return render_template("index.html",data=data) 

@application.route("/story")
def Story():
    return send_from_directory(application.static_folder,'index.html')
    # return render_template("story.html") 

################################################################
###  AJAX endpoints
@application.route('/ajaxGet', methods=["GET"])
def AjaxGet():
    action = request.args.get('action')
    if action == "add": # Adding a new record
        PersonID = session['PersonID']
        jsonData = json.loads(request.args.get('JSON'))
        db.add({
            "PersonID":PersonID,
            "json": jsonData
        })
    return "done"
################################################################
### DB testing endpoints
@application.route('/add')
def Add(data):
    db.add(data)
    return "Added " + data

@application.route('/view')
def View():
    records = db.view()
    return str([r for r in records])

@application.route('/reset')
def Reset():
    db.reset()
    return "DB Reset"

@application.route('/drop')
def Drop():
    db.dropTable()
    return "DB Table Dropped"

@application.route('/create')
def Create():
    db.createTable()
    return "DB Table Created"

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()