from flask import Flask, render_template, request
import json
import db
# import db
import datetime 

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# EB looks for an 'application' callable by default.
application = Flask(__name__)

################################################################
###  Web Page endpoints
@application.route("/")
def Index():
    data={
        "name":"Tak"
    }
    return render_template("index.html",data=data) 

################################################################
###  AJAX endpoints
@application.route('/ajaxGet', methods=["GET"])
def AjaxGet():
    action = request.args.get('action')
    if action == "add": # Adding a new record
        PersonID = request.args.get('PersonID')
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