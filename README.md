# IDS Mturk experiment
For the Immersive Data Storytelling project, this repository contains source code of a web application that runs on AWS Elastic Beanstalk. 

# Usage
## How to run locally
1. Clone or download this repository
> `git clone git@github.com:reflect9/ids_mturk_aws.git`
2. Install required libraries
> `pip install -r requirements.txt`
3. Set Flask environments
> `export FLASK_APP=application.py`

> `export FLASK_ENV=development`
4. Run Flask locally
> `flask run`
<pre>
Serving Flask app 'application.py' (lazy loading) 
Environment: development 
Debug mode: on 
Running on http://127.0.0.1:5000/ (Press CTRL+C to quit) 
Restarting with stat
Debugger is active!
Debugger PIN: 127-277-866
</pre>
5. Open the local page on browser (http://127.0.0.1:5000/)

## How to deploy on AWS EB
1. Install AWS EB CLI (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
2. Make sure EB CLI runs on your terminal
<pre>
takyeonlee@TAKui-MacBookPro ids_mturk % eb
usage: eb (sub-commands ...) [options ...] {arguments ...}
...
</pre>
3. Make sure all updates are staged on local git

BAD EXAMPLE (modified files are not staged yet)
<pre>
takyeonlee@TAKui-MacBookPro ids_mturk % git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   README.md
	modified:   __pycache__/application.cpython-310.pyc
	modified:   __pycache__/db.cpython-310.pyc
	modified:   requirements.txt

no changes added to commit (use "git add" and/or "git commit -a")
</pre>

GOOD EXAMPLE (modified files are staged; not committed yet though)
<pre>
takyeonlee@TAKui-MacBookPro ids_mturk % git add .
takyeonlee@TAKui-MacBookPro ids_mturk % git status
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   README.md
	modified:   __pycache__/application.cpython-310.pyc
	modified:   __pycache__/db.cpython-310.pyc
	modified:   requirements.txt
</pre>

4. Deploy on EB 

If you want to deploy currently staged files without changing the repository
> `eb deploy --staged`

If you want to deploy the latest commit
> `eb deploy`



# ETC 

RDS loggin 
"mysql -h ids-mturk.ctb0mvbckgia.ap-northeast-2.rds.amazonaws.com -P 3306 -u ael -p"


- To kill local servers using 5000
kill -9 $(lsof -t -i:"5000")