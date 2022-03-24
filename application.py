from flask import Flask
import datetime 

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    11:35
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

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

# # @application.route('/add')
# # def Add():
# #     json_to_add = str(datetime.datetime.now())
# #     add(json_to_add)
# #     return "Added " + json_to_add

# # @application.route('/view')
# # def View():
# #     records = view()
# #     return str([r.json for r in records])

# # run the application.
# if __name__ == "__main__":
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production application.
#     application.debug = True
#     application.run()
