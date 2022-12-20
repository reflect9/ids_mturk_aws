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

    index = len(set(results)) % 38
    possibleVersions=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    possibleTasks = [[100, 101], [101, 100], [100, 101], [101, 100], [100, 101], [100, 110], [110, 100], [101, 110], [110, 101], [101, 110], [110, 101], [100, 101], [101, 100], [100, 110], [101, 110], [110, 101], [101, 110], [110, 101], [101, 110], [110, 101], [101, 110], [110, 101], [101, 110], [100, 101], [101, 100], [100, 101], [101, 100], [100, 110], [110, 100], [100, 110], [110, 100], [100, 110], [110, 100], [101, 110], [110, 101], [101, 110], [110, 101], [101, 110]]
    # possibleTasks = [[100, 101], [100, 110], [101, 100], [101, 110], [110,100], [110, 101]]
    return [possibleVersions[index//1], possibleTasks[index%38]]
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
    # return render_template("end.html")

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

# get loadedJson as input
screener_answers = [
    'a',
    'q',
    # 'The 3D article was more interesting to look at but it was harder to navigate it on my own.',
    # 'Visually this has much more impact and gets away from the tried and test 2D bar charts that people are familiar with and probably a little bored with. Version A is just more modern and uses technology better. ',
    'The animations of B made it more interesting visually to watch. However, I would overall say there wasn\'t much difference between them.',
    'A was more interesting because as an autistic person, the broken-apart nature of the text makes it easier for me to follow along, as opposed to large blocks of text.',
    'I think they were both interesting but B caught my attention more. ', 'The new animation style makes it look more immersive and interesting.'
]

screener_ids = [
    "62c41fe598ab94de4d4f021e",
    "6023f94d1951e70ae21770ec",
    "5f6067975552dc000aa21f2a",
    "62e17900c4ff2316a7297ce6",
    "62db2644ab0a3a353c0dcb54",
    "615eca41d537883c96fc9eec",
    "5ff75af9",
    "5eea1be10e95520beb9fa654",
    "ff9c5800",
    "aab69097",
    "7d4d8032",
    "62a3b97d41ae082b602e815b",
    "5eda5ad7cee6c16590433514",
    "5f1c72e25a26d503c77bfdc9",
    "62a7c4d5266dfb89bf94fec8",
    "56e03d86a3b147000ac61c4c",
    "609140cea1442672dd2141d7",
    "6321d750bbac904272fcff34",
    "21e657ae",
    "f41d8579",
    "c9515f1c",
    # "5ddd631f063ebd000dbe0687",
    # "5f16f559325a640008bb9a07",
    # "5c66d6a50d7f5f00014b8ab0",
    # "6097f813d541b6142fae8e7f",
    # "60a4a56df1a5ad7deb4b7e69",
    # "5d1c9d39ff67e3000140ca87",
    # "5d730a3cf37bfe0001ff031a",
    # "56de005e6893b5000ce95d71",
    # "c0994ac0",
    # "286b04fc",
    # "628f7669ee68aabf3930123b",
    # "ea660b87",
    # "5ce475232210eb00018706b3",
    # "5c9f61562707e10001a01066",
    # "5eb9ea35347cb51296f0c223",
    # "5f27f6a0e13d4e05d048335f",
    # "627e1a670e22288b334ebf9d",
    # "edb9f5eb",
    # "5eca55ce7b00b50119c64518",
    # "5f8cbc5c355ea745e6cef2ca",
    # "5c4592d7f608210001a4b0a8",
    # "43f546ca",
    # "616d5c54f2953f6447f27402",
    # "5ec00f62cf12be40ea6fe344",
    # "eaea35ef",
    # "e0374dca",
    # "578917da4d107800016db836",
    # "6107acc592df914a921e2b41",
    # "62a447d91e71bfacd2e8c006",
    # "5ecd36302b4d3c05d4cc1ba2",
    # "b248785e",
    # "5cc53cf3291607001757c712",
    # "5ac033fa68b65b00018d2c1a",
    # "a427e7a8",
    # "629b3b3c89d490460eacbfbc",
    # "6287745dd285a8be832879dc",
    # "58d0632c2fc72000011f8c57",
    # "5f1c74f81af38d514e2a50bb",
    # "f42b1c37",
    # "62b1ed7447191a42db49a77f",
    # "5c3dfadfef1d0d0001b2870e"
]

def filter(loadedJson, ID):
    if loadedJson["UCS"]['Which version was<br/> <b>more interesting</b>?'][""] in screener_answers:
        return False
    if ID in screener_ids:
        return False

    return True

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
    results = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for r in records:
        loadedJson = json.loads(r.json)
        if r.Timestamp.month >= 11 and loadedJson['event'] == 'log' and 'UCS' in loadedJson:
            if filter(loadedJson, r.PersonID):
                print(f'{r.PersonID} : {loadedJson["DS"]} - {loadedJson["Task"]}')
                results[loadedJson["DS"]][int(str(loadedJson["Task"][0]), 2) + int(str(loadedJson["Task"][1]), 2) - 9] += 1
    #     if r.json.event == 'completed':
    #         results.append(r.PersonID)
    #
    # index = len(set(results)) % 12
    # print(results)
    return str(results);

# @application.route('/reset')
# def Reset():
#     db.reset()
#     return "DB Reset"
#
# @application.route('/drop')
# def Drop():
#     db.dropTable()
#     return "DB Table Dropped"

# don't want to let any other users to delete the database!

# @application.route('/create')
# def Create():
#     db.createTable()
#     return "DB Table Created"

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
        if r.Timestamp.month >= 11 and loadedJson['event'] == 'log':
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
                print(loadedJson["UCS"])
                if filter(loadedJson, r.PersonID):
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
