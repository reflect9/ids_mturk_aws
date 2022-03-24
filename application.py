from flask import Flask, render_template
import db
# import db
import datetime 

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# EB looks for an 'application' callable by default.
application = Flask(__name__)


@application.route("/")
def Index():
    data={
        "name":"Tak"
    }
    return render_template("index.html",data=data) 


@application.route('/add')
def Add():
    json_to_add = str(datetime.datetime.now())
    db.add(json_to_add)
    return "Added " + json_to_add

@application.route('/view')
def View():
    records = db.view()
    return str([r.json for r in records])

@application.route('/reset')
def Reset():
    db.reset()
    return "DB Reset"


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()


# from flask import Flask, render_template
# # from db import add, view    
# import datetime 


# application = Flask(__name__)

# @application.route("/")
# def Index():
#     data={
#         "name":"Tak"
#     }
#     return render_template("index.html",data=data) 

# # run the application.
# if __name__ == "__main__":
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production application.
#     application.debug = True
#     application.run()
