from flask import Flask, render_template, request, session, send_from_directory
from flask_cors import CORS
import json, uuid, random
import db
import datetime

# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='', static_folder='2022DS_build')
application.secret_key = "super secret key"
CORS(application)

""" fetchTask is a temporary solution for fetching task per participant
    Later we will populat task lists in DB
"""
def fetchTask():
    records = db.myOperation()
    results = []
    for r in records:
        results.append(r.PersonID)

    index = len(set(results)) % 2
    possibleVersions=[0]
    possibleTasks = [[100, 110], [110, 100]]
    # possibleTasks = [[100, 101], [100, 110], [101, 100], [101, 110], [110,100], [110, 101]]
    return [possibleVersions[index//6], possibleTasks[index%2]]
    # return random.sample(possibleTasks,1)[0]

################################################################
###  Web Page endpoints
@application.route("/")
def Index():
    session["IsArchive"] = False
    session["PersonID"] = str(uuid.uuid4())[:8]
    # session["CompletionCode"] = str(uuid.uuid4())[:4]
    session["CompletionCode"] = '4F618013' # given code from Prolific
    session["StoryID"] = 0
    session["IsQuiz"] = 0
    fetched = fetchTask()
    session["DS"] = fetched[0]
    session["Task"] = fetched[1]
    return render_template("index.html")

@application.route("/story")
def Story():
    return send_from_directory(application.static_folder,'index.html')

@application.route("/completion")
def Completion():
    return render_template('completion.html')

@application.route("/archive")
def Archive():
    session["IsArchive"] = True
    session["PersonID"] = str(uuid.uuid4())[:8]
    session["CompletionCode"] = '4F618013' # given code from Prolific
    session["StoryID"] = 0
    session["IsQuiz"] = 0
    session["DS"] = 0
    session["Task"] = [100, 101]
    return render_template("archive.html")
################################################################
###  AJAX endpoints
@application.route('/ajaxGet', methods=["GET"])
def AjaxGet():
    action = request.args.get('action')
    if action == "log": # Adding a new record
        print (request.args.get('json'))
        jsonData = json.loads(request.args.get('json'))
        jsonData["event"] = "log"
        jsonData["DS"] = session["DS"]
        jsonData["Task"] = session["Task"]
        PersonID = session['PersonID']
        if session["IsArchive"] == False:
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
        # print(db);
        if session["StoryID"] == -1:
            if session["IsArchive"] == False:
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
                "DS":session["DS"],
                "nextStory":-1,
                "isQuiz":session["IsQuiz"],
            })
        else:
            storyInfo = session["Task"][session["StoryID"]]
            # session["StoryID"] = session["StoryID"] + 1
            PersonID = session['PersonID']
            if session["IsArchive"] == False:
                db.add({
                    "PersonID":session["PersonID"],
                    "Tasks":session["Task"],
                    "DS":session["DS"],
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
                "DS":session["DS"],
                "nextStory":storyInfo,
                "StoryID":session["StoryID"],
                "isQuiz":session["IsQuiz"]
            })
    elif action == "setQuiz":
        session["IsQuiz"] = session["StoryID"] + 1;
        if session["IsArchive"] == False:
            db.add({
                "PersonID":session["PersonID"],
                "Tasks":session["Task"],
                "DS":session["DS"],
                "CompletionCode":session["CompletionCode"],
                "json": {
                    "event":"setQuiz",
                    "storyIDS":session["StoryID"],
                    "isQuiz":session["IsQuiz"],
                }
            })
        return json.dumps({
            "PersonID": session['PersonID'],
            "task":session["Task"],
            "DS":session["DS"],
            "nextStory": session["Task"][session["StoryID"]],
            "StoryID":session["StoryID"],
            "isQuiz":session["IsQuiz"],
        })

    elif action == "start":
        if session["IsArchive"] == False:
            print (request.args.get('json'))
            session['PersonID'] = json.loads(request.args.get('json'))["ProlificID"]

    elif action == "setMain":
        if session["IsArchive"] == False:
            return json.dumps({
                "PersonID": session['PersonID'],
                "DS":session["DS"],
                "task":session["Task"],
                "Archive":session["IsArchive"]
            })
        else:
            session["DS"] = request.args.get('ds');
            session["Task"] = [request.args.get('condition'), request.args.get('condition')];
            return json.dumps({
                "PersonID": session['PersonID'],
                "DS":session["DS"],
                "task":session["Task"],
                "Archive":session["IsArchive"]
            })
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

@application.route('/assign')
def Assign():
    records = db.myOperation()
    results = []
    for r in records:
        results.append(r.PersonID)

    index = len(set(results)) % 12
    return str(set(results));

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

@application.route('/board')
def Board():
    records = db.myOperation()
    results1 = []
    results2 = []
    results3 = []
    M1 = []
    M2 = []
    M3 = []
    M1_1 = [[], []]
    M1_2 = [[], []]
    M1_3 = [[], []]
    UCS_int = []
    UCS_eas = []
    UCS_per = []
    UCS_tru = []
    UCS_cur = []

    for r in records:
        loadedJson = json.loads(r.json)
        if loadedJson['event'] == 'log':
            if 'M2' in loadedJson:
                results1.append({
                    "ID": r.PersonID,
                    "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
                    "Json": loadedJson
                })
                M1.append(loadedJson["M1-1"])
                M2.append(loadedJson["M2"])
                M3.append(loadedJson["M3"])

                if hasattr(loadedJson, 'type'):
                    M1_1[0 if loadedJson["type"] == 100 else 1].append(loadedJson["M1-1"])
                    M1_2[0 if loadedJson["type"] == 100 else 1].append(loadedJson["M1-2"])
                # M1_3[0 if loadedJson["type"] == 100 else 1].append(loadedJson["M1-3"])

            elif 'UCS' in loadedJson:
                # print(loadedJson)
                results2.append({
                    "ID": r.PersonID,
                    "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
                    "Json": loadedJson
                })
                for k,v in loadedJson["UCS"].items():
                    if 'interest' in k:
                        UCS_int.append({
                            "DS":loadedJson["DS"],
                            "FirstTask":loadedJson["Task"][0],
                            "DS_Task":str(loadedJson["DS"])+"_"+str(loadedJson["Task"][0])+"/"+str(loadedJson["Task"][1]),
                            "score": v["col1"],
                            "comment": v[""],
                            "ID": r.PersonID,
                        })
                    elif 'easier' in k or 'easy' in k:
                        UCS_eas.append({
                            "DS":loadedJson["DS"],
                            "FirstTask":loadedJson["Task"][0],
                            "DS_Task":str(loadedJson["DS"])+"_"+str(loadedJson["Task"][0])+"/"+str(loadedJson["Task"][1]),
                            "score": v["col1"],
                            "comment": v[""],
                            "ID": r.PersonID,
                        })
                    elif 'persuasive' in k:
                        UCS_per.append({
                            "DS":loadedJson["DS"],
                            "FirstTask":loadedJson["Task"][0],
                            "DS_Task":str(loadedJson["DS"])+"_"+str(loadedJson["Task"][0])+"/"+str(loadedJson["Task"][1]),
                            "score": v["col1"],
                            "comment": v[""],
                            "ID": r.PersonID,
                        })
                    elif 'trustworthy' in k:
                        UCS_tru.append({
                            "DS":loadedJson["DS"],
                            "FirstTask":loadedJson["Task"][0],
                            "DS_Task":str(loadedJson["DS"])+"_"+str(loadedJson["Task"][0])+"/"+str(loadedJson["Task"][1]),
                            "score": v["col1"],
                            "comment": v[""],
                            "ID": r.PersonID,
                        })
                    elif 'curious' in k:
                        UCS_cur.append({
                            "DS":loadedJson["DS"],
                            "FirstTask":loadedJson["Task"][0],
                            "DS_Task":str(loadedJson["DS"])+"_"+str(loadedJson["Task"][0])+"/"+str(loadedJson["Task"][1]),
                            "score": v["col1"],
                            "comment": v[""],
                            "ID": r.PersonID,
                        })
            else:
                results3.append({
                    "ID": r.PersonID,
                    "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
                    "Json": loadedJson
                })

    results1.sort(key=lambda x: x["Json"]["M3"])
    UCS_int.sort(key=lambda x: (int(x["FirstTask"]), int(x["score"]), int(x["DS"])))
    UCS_eas.sort(key=lambda x: (int(x["FirstTask"]), int(x["score"]), int(x["DS"])))
    UCS_per.sort(key=lambda x: (int(x["FirstTask"]), int(x["score"]), int(x["DS"])))
    UCS_tru.sort(key=lambda x: (int(x["FirstTask"]), int(x["score"]), int(x["DS"])))
    UCS_cur.sort(key=lambda x: (int(x["FirstTask"]), int(x["score"]), int(x["DS"])))
    print(len(UCS_tru))


    graph_layout = {}
#
    return render_template('board.html',
        data1 = results1,
        data2 = results2,
        data3 = results3,
        UCS_int = UCS_int,
        UCS_eas = UCS_eas,
        UCS_per = UCS_per,
        UCS_tru = UCS_tru,
        UCS_cur = UCS_cur,
        )

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
