from flask import Flask, render_template, request, session, send_from_directory
from flask_cors import CORS
import json, uuid, random
import db
# import db
import datetime
# import plotly, plotly.graph_objs as go


# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='', static_folder='2022DS_build')
application.secret_key = "super secret key"
CORS(application)

""" fetchTask is a temporary solution for fetching task per participant
    Later we will populat task lists in DB
"""
def fetchTask():
    # Below is two possible tasks for a participant (will be replaced with pre-populated DB)
    records = db.myOperation()
    results = []
    for r in records:
        results.append(r.PersonID)

    index = len(set(results)) % 12
    possibleVersions=[0, 1]
    possibleTasks = [[100, 101], [100, 110], [101, 100], [101, 110], [110,100], [110, 101]]
    return [possibleVersions[index//6], possibleTasks[index%6]]
    # return random.sample(possibleTasks,1)[0]

################################################################
###  Web Page endpoints
@application.route("/")
def Index():
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
                "nextStory":storyInfo,  # either 100,101,110 (type of the current story)
                "StoryID":session["StoryID"],
                "isQuiz":session["IsQuiz"]
            })
    elif action == "setQuiz":
        session["IsQuiz"] = session["StoryID"] + 1;
        return json.dumps({
            "PersonID": session['PersonID'],
            "task":session["Task"],
            "DS":session["DS"],
            "nextStory": session["Task"][session["StoryID"]],  # either 100,101,110 (type of the current story)
            "StoryID":session["StoryID"],
            "isQuiz":session["IsQuiz"],
        })
    elif action == "start":
        print (request.args.get('json'))
        session['PersonID'] = json.loads(request.args.get('json'))["ProlificID"]
    elif action == "setMain":
        return json.dumps({
            "PersonID": session['PersonID'],
            "DS":session["DS"],
            "task":session["Task"],
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
    return str(index);

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

# @application.route('/board')
# def Board():
#     records = db.myOperation()
#     results1 = []
#     results2 = []
#     results3 = []
#     M1 = []
#     M2 = []
#     M3 = []
#     M1_1 = [[], []]
#     M1_2 = [[], []]
#     M1_3 = [[], []]
#     UCS_int = []
#     UCS_eas = []
#     UCS_per = []
#     UCS_tru = []
#
#     for r in records:
#         loadedJson = json.loads(r.json)
#         if r.Timestamp.month == 5 and r.Timestamp.day > 24 and len(r.PersonID) == 24 and loadedJson['event'] == 'log':
#             if 'scroll' in loadedJson:
#                 loadedJson["scroll"] = []
#             if 'M2' in loadedJson:
#                 results1.append({
#                     "ID": r.PersonID,
#                     "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
#                     "Json": loadedJson
#                 })
#                 M1.append(loadedJson["M1-1"])
#                 M2.append(loadedJson["M2"])
#                 M3.append(loadedJson["M3"])
#
#                 M1_1[0 if loadedJson["type"] == 1000 else 1].append(loadedJson["M1-1"])
#                 M1_2[0 if loadedJson["type"] == 1000 else 1].append(loadedJson["M1-2"])
#                 M1_3[0 if loadedJson["type"] == 1000 else 1].append(loadedJson["M1-3"])
#
#             elif 'UCS' in loadedJson:
#                 results2.append({
#                     "ID": r.PersonID,
#                     "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
#                     "Json": loadedJson
#                 })
#                 for k,v in loadedJson["UCS"].items():
#                     if 'interest' in k:
#                         UCS_int.append({
#                             "score": v["col1"] if loadedJson["type"] == 1000 else -v["col1"],
#                             "comment": v["comment"]
#                         })
#                     elif 'easier' in k or 'easy' in k:
#                         UCS_eas.append({
#                             "score": v["col1"] if loadedJson["type"] == 1000 else -v["col1"],
#                             "comment": v["comment"]
#                         })
#                     elif 'persuasive' in k:
#                         UCS_per.append({
#                             "score": v["col1"] if loadedJson["type"] == 1000 else -v["col1"],
#                             "comment": v["comment"]
#                         })
#                     elif 'trustworthy' in k:
#                         UCS_tru.append({
#                             "score": v["col1"] if loadedJson["type"] == 1000 else -v["col1"],
#                             "comment": v["comment"]
#                         })
#             else:
#                 results3.append({
#                     "ID": r.PersonID,
#                     "Timestamp": [r.Timestamp.month, r.Timestamp.day, r.Timestamp.hour],
#                     "Json": loadedJson
#                 })
#
#     print(len(results1))
#     # print(len(results2))
#     # print(len(results3))
#     # print(len(UCS_int))
#     # print(len(UCS_eas))
#     # print(len(UCS_per))
#     # print(len(UCS_tru))
#     print(M1_1)
#     # print(M2)
#     # print(M3)
#
#
#     data_M1 = go.Figure(data=[go.Pie(labels=['2-3','5-6','8-9','11-12'], values=[sum(x == y for x in M1) for y in ['February - March', 'May - June', 'August - September', 'November - December']])])
#     graphJSON_M1 = json.dumps(data_M1, cls=plotly.utils.PlotlyJSONEncoder)
#     data_M2 = go.Figure(data=[go.Pie(labels=['True','False'], values=[sum(x == y for x in M2) for y in ['True', 'False']])])
#     graphJSON_M2 = json.dumps(data_M2, cls=plotly.utils.PlotlyJSONEncoder)
#     data_M3 = go.Figure(data=[go.Pie(labels=['1','2','3','4'], values=[sum(x == y for x in M3) for y in ['1', '2', '3', '4']])])
#     graphJSON_M3 = json.dumps(data_M3, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_M111 = [go.Bar(x=['2-3','5-6','8-9','11-12'],y=[sum(x == y for x in M1_1[0]) for y in ['February - March', 'May - June', 'August - September', 'November - December']])]
#     graphJSON_M111 = json.dumps(data_M111, cls=plotly.utils.PlotlyJSONEncoder)
#     data_M112 = [go.Bar(x=['2-3','5-6','8-9','11-12'],y=[sum(x == y for x in M1_1[1]) for y in ['February - March', 'May - June', 'August - September', 'November - December']])]
#     graphJSON_M112 = json.dumps(data_M112, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_M121 = [go.Bar(x=[1, 2, 3, 4, 5, 6, 7],y=[sum(int(x[0]) == y for x in M1_2[0]) for y in range(1, 8)])]
#     graphJSON_M121 = json.dumps(data_M121, cls=plotly.utils.PlotlyJSONEncoder)
#     data_M122 = [go.Bar(x=[1, 2, 3, 4, 5, 6, 7],y=[sum(int(x[0]) == y for x in M1_2[1]) for y in range(1, 8)])]
#     graphJSON_M122 = json.dumps(data_M122, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_M131 = [go.Bar(x=[1, 2, 3, 4, 5, 6, 7],y=[sum(int(x[0]) == y for x in M1_3[0]) for y in range(1, 8)])]
#     graphJSON_M131 = json.dumps(data_M131, cls=plotly.utils.PlotlyJSONEncoder)
#     data_M132 = [go.Bar(x=[1, 2, 3, 4, 5, 6, 7],y=[sum(int(x[0]) == y for x in M1_3[1]) for y in range(1, 8)])]
#     graphJSON_M132 = json.dumps(data_M132, cls=plotly.utils.PlotlyJSONEncoder)
#
#     UCS_int.sort(key=lambda x: int(x["score"]))
#     UCS_eas.sort(key=lambda x: int(x["score"]))
#     UCS_per.sort(key=lambda x: int(x["score"]))
#     UCS_tru.sort(key=lambda x: int(x["score"]))
#
#     data_int = [go.Bar(x=[-3, -2, -1, 0, 1, 2, 3],y=[sum(x["score"] == y for x in UCS_int) for y in range(-3, 4)])]
#     graphJSON_int = json.dumps(data_int, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_eas = [go.Bar(x=[-3, -2, -1, 0, 1, 2, 3],y=[sum(x["score"] == y for x in UCS_eas) for y in range(-3, 4)])]
#     graphJSON_eas = json.dumps(data_eas, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_per = [go.Bar(x=[-3, -2, -1, 0, 1, 2, 3],y=[sum(x["score"] == y for x in UCS_per) for y in range(-3, 4)])]
#     graphJSON_per = json.dumps(data_per, cls=plotly.utils.PlotlyJSONEncoder)
#
#     data_tru = [go.Bar(x=[-3, -2, -1, 0, 1, 2, 3],y=[sum(x["score"] == y for x in UCS_tru) for y in range(-3, 4)])]
#     graphJSON_tru = json.dumps(data_tru, cls=plotly.utils.PlotlyJSONEncoder)
#
#     graph_layout = {}
#
#     return render_template('board.html',
#         data1 = results1,
#         data2 = results2,
#         data3 = results3,
#         UCS_int = UCS_int, graph_int = graphJSON_int,
#         UCS_eas = UCS_eas, graph_eas = graphJSON_eas,
#         UCS_per = UCS_per, graph_per = graphJSON_per,
#         UCS_tru = UCS_tru, graph_tru = graphJSON_tru,
#         graph_layout = graph_layout,
#         graph_M1 = graphJSON_M1, graph_M2 = graphJSON_M2, graph_M3 = graphJSON_M3,
#         graph_M111 = graphJSON_M111, graph_M112 = graphJSON_M112,
#         graph_M121 = graphJSON_M121, graph_M122 = graphJSON_M122,
#         graph_M131 = graphJSON_M131, graph_M132 = graphJSON_M132,
#         )

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
