from flask import Flask, render_template, request, session, send_from_directory
from flask_cors import CORS
import json, uuid, random
import db
# import db
import datetime


# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='', static_folder='2022DS_build')
application.secret_key = "super secret key"
CORS(application)

""" fetchTask is a temporary solution for fetching task per participant
    Later we will populat task lists in DB
"""
def fetchTask():
    # Below is two possible tasks for a participant (will be replaced with pre-populated DB)
    # possibleTasks = [[1000], [1001], [1010], [1011], [1100], [1101], [1110]]
    possibleTasks = [[1000, 1110], [1110, 1000]]
    # 1000:Static_Non1, 1001:Animated_Non, 1010:Immersive_Non, 1011:Static_Non2, 1100: Static_Imm, 1101: Animated_Imm, 1110: Immersive_Imm
    return random.sample(possibleTasks,1)[0]

################################################################
###  Web Page endpoints
@application.route("/")
def Index():
    session["PersonID"] = str(uuid.uuid4())[:8]
    # session["CompletionCode"] = str(uuid.uuid4())[:4]
    session["CompletionCode"] = '4F618013' # given code from Prolific
    session["StoryID"] = 0
    session["IsQuiz"] = 0
    session["Task"] = fetchTask()
    return render_template("index.html")

@application.route("/story")
def Story():
    return send_from_directory(application.static_folder,'index.html')

@application.route("/completion")
def Completion():
    return render_template('completion.html')
################################################################
###  AJAX endpoints
@application.route('/ajaxGet', methods=["GET"])
def AjaxGet():
    action = request.args.get('action')
    if action == "log": # Adding a new record
        print (request.args.get('json'))
        jsonData = json.loads(request.args.get('json'))
        jsonData["event"] = "log"
        PersonID = session['PersonID']
        db.add({
            "PersonID":PersonID,
            "CompletionCode":session["CompletionCode"],
            "json": jsonData
        })

        if session["StoryID"] < len(session["Task"]) - 1:
            session["StoryID"] = session["StoryID"] + 1
        else:
            session["StoryID"] = -1
        session["IsQuiz"] = 0;
        print("StoryID:", session["StoryID"])
        return "done"
    elif action == "getSessionVar": # Getting the current session's variable
        response = { }
        ks = request.args.get("keys").split(",")
        for k in ks:
            print(k)
            print(session[k])
            if k in session:
                response[k] = session[k]
            else:
                response[k] = "There is no session variable for " + k
        return json.dumps(response)
    elif action == "fetchNextStory": # ReactJS is getting information of the next story
        if session["StoryID"] == -1:
            db.add({
                "PersonID":session["PersonID"],
                "CompletionCode":session["CompletionCode"],
                "json": {
                    "event":"completed"
                }
            })
            return json.dumps({
                "PersonID":session["PersonID"],
                "CompletionCode":session["CompletionCode"],
                "nextStory":-1,
                "isQuiz":session["IsQuiz"]
            })
        else:
            storyInfo = session["Task"][session["StoryID"]]
            # session["StoryID"] = session["StoryID"] + 1
            PersonID = session['PersonID']
            db.add({
                "PersonID":session["PersonID"],
                "CompletionCode":session["CompletionCode"],
                "json": {
                    "event":"fetchStory",
                    "storyIDS":session["StoryID"],
                    "storyInfo":storyInfo
                }
            })
            return json.dumps({
                "PersonID": PersonID,
                "task":session["Task"],
                "nextStory":storyInfo,  # either 100,101,110 (type of the current story)
                "StoryID":session["StoryID"],
                "isQuiz":session["IsQuiz"]
            })
    elif action == "setQuiz":
        session["IsQuiz"] = session["StoryID"] + 1;
        return json.dumps({
            "PersonID": session['PersonID'],
            "task":session["Task"],
            "nextStory": session["Task"][session["StoryID"]],  # either 100,101,110 (type of the current story)
            "StoryID":session["StoryID"],
            "isQuiz":session["IsQuiz"]
        })
    elif action == "start":
        print (request.args.get('json'))
        session['PersonID'] = json.loads(request.args.get('json'))["ProlificID"]
    else:
        return "?"

################################################################
### DB testing endpoints
@application.route('/add')
def Add(data):
    db.add(data)
    return "Added " + data

@application.route('/view')
def View():
    records = db.view()
    results = []
    for r in records:
        results.append([r.PersonID, r.CompletionCode, r.Timestamp, r.json])
        print (r.json)
    return str(results)

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
