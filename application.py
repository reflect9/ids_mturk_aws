from flask import Flask, render_template
# from db import add, view    
import datetime 


application = Flask(__name__)

@application.route("/")
def Index():
    data={
        "name":"Tak"
    }
    return render_template("index.html",data=data) 

# @application.route('/add')
# def Add():
#     json_to_add = str(datetime.datetime.now())
#     add(json_to_add)
#     return "Added " + json_to_add

# @application.route('/view')
# def View():
#     records = view()
#     return str([r.json for r in records])

# run the application.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    application.debug = True
    application.run()
