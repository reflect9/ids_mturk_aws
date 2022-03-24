from flask import Flask, render_template
# from db import add, view    
import datetime 


app = Flask(__name__)

@app.route("/")
def Index():
    data={
        "name":"Tak"
    }
    return render_template("index.html",data=data) 

# @app.route('/add')
# def Add():
#     json_to_add = str(datetime.datetime.now())
#     add(json_to_add)
#     return "Added " + json_to_add

# @app.route('/view')
# def View():
#     records = view()
#     return str([r.json for r in records])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
