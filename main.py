import pyrebase
import json
import os
from werkzeug import secure_filename
from flask import *
import datetime
from time import gmtime, strftime
import hashlib
import webbrowser
config = {
  	
  "apiKey" : "AIzaSyCLlwtDViQPRFWCYrm4OXVUoXx5oC12e2U",
	"authDomain" : "test-38881.firebaseapp.com",
	"databaseURL" : "https://test-38881.firebaseio.com",
	"storageBucket" : "test-38881.appspot.com",
	"messagingSenderId" : "136023743018",
	"serviceAccount": "auth.json"
}


def generatetimestamp():
	return strftime("%Y-%m-%d %H:%M:%S", gmtime())

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("rajasthantest@gmail.com", "8602229193")
db = firebase.database()
# print(auth.get_account_info(user['idToken']))
app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploaded/'
app.secret_key = 'moriarty'

@app.route('/', methods=['POST','GET'])
def index():
	return render_template("index.html")

@app.route('/register',methods=['POST','GET'])
def signup():
	users = db.child("users").get()
	users=(users.val())
	if request.method=="POST":
		email=request.form.get("email",'')
		password=request.form.get("password",'')
		name=request.form.get("name",'')
		uid=request.form.get("id",'')
		name=request.form.get("name",'')
		aadhar=request.form.get("aadhar",'')
		address=request.form.get("address",'')
		role=request.form.get("role",'')
		city=request.form.get("city",'')
		district=request.form.get("district",'')
		dob=request.form.get("dob",'')
		mobile=request.form.get("mobile",'')
		docdept=request.form.get("docdept",'')
		docdegree=request.form.get("docdegree",'')
		docdept=request.form.get("mobile",'')
		hospital=request.form.get("hospital",'')
		schedule=request.form.get("schedule",'')
		offdept=request.form.get("offdept",'')
		offpost=request.form.get("offpost",'')
		offdegree=request.form.get("offdegree",'')
		users = db.child("users").get()
		users=(users.val())
		registered=1
		for i in users:
			if i["id"]==uid:
				flash("Username Already Exists")
				registered=0
		if registered:
			d={}
			d["id"]=uid
			d["password"]=password
			d["name"]=name
			d["email"]=email
			d["aadhar"]=aadhar
			d["address"]=address
			d["city"]=city
			d["dob"]=dob
			d["role"]=role
			d["name"]=name
			d["mobile"]=mobile
			d["camps"]=[]
			d["appointments"]=[]
			d["roledetails"]={}
			if role=="doctor":
				d["roledetails"]["docdept"]=docdept
				d["roledetails"]["docdegree"]=docdegree
				d["roledetails"]["hospital"]=hospital
				d["roledetails"]["schedule"]=schedule
			if role=="official":
				d["roledetails"]["office"]=office
				d["roledetails"]["offdegree"]=offdegree
				d["roledetails"]["offdept"]=offdept
				d["roledetails"]["offpost"]=offpost
			users.append(d)
			n={}
			n["users"]=users
			db.update(n)
			flash("Registered")
	return render_template("signup.html")

@app.route('/logout')
def logout():
	session.clear()
	redirect(url_for('index'))

@app.route('/login',methods=['POST','GET'])
def login():
	if "user" in session:
		return render_template("profile.html")
	if request.method=="POST":
		uid=request.form.get("id",'')
		password=request.form.get("password",'')
		users = db.child("users").get()
		users=(users.val())
		for user in users:
			if user["id"]==uid and user["password"]==password:
				session["user"]=user
				return render_template("profile.html")
		flash("Invalid Credentials")
	return render_template("login.html")


@app.route('/news',methods=['POST','GET'])
def news():
	news = db.child("news").get()
	news=(news.val())
	return render_template("news.html",news=news)

@app.route('/addnews',methods=['POST','GET'])
def addnews():
	news = db.child("news").get()
	news=(news.val())
	if request.method == 'POST':
		title=request.form.get("title",'')
		content=request.form.get("content",'')
		timestamp=generatetimestamp()
		newnode={}
		newnode["title"]=title
		newnode["content"]=content
		newnode["author"]=session["user"]["name"]
		newnode["timestamp"]=timestamp
		# [
		# 	{
		# 		"title": "new title",
		# 		"content": "id2",
		# 		"img": "image",
		# 		"author":"bla",
		# 		"timestamp":"2017-03-18 16:39:58.260378"
		# 	}
		# ]
		uniq=session["user"]["name"]+timestamp
		f = request.files['file']
		newsid=(hashlib.md5(uniq.encode('utf-8')).hexdigest())
		nameoffile=(f.filename)
		ext=nameoffile.split('.')
		ext=ext[len(ext)-1]
		f.filename=newsid+"."+ext
		f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
		storage = firebase.storage()
		storage.child("images/"+newsid+".jpg").put("uploaded/"+newsid+".jpg")
		urlimage=storage.child("images/"+newsid+".jpg").get_url(token=auth.get_account_info(user['idToken']))
		urlimage=urlimage.split("&token")
		newnode["img"]=urlimage[0]
		print(newnode["img"])
		news.append(newnode)
		newsupdated={}
		newsupdated["news"]=news
		db.update(newsupdated)
		return('News Updated')
	return render_template("purana.html")

@app.route('/chat',methods=['GET','POST'])
def create_chat():
	uid=session["user"]["id"]
	token='emitra'+uid
	chatupdated={}
	chatupdated["chat"]=[]
	new={}
	new["duid"]=uid
	new["status"]="available"
	new["token"]=token
	print(token)
	chatupdated["chat"].append(new)
	db.update(chatupdated)
	webbrowser.open('http://appr.tc/r/'+token)
	return('0')

@app.route('/show_online_docs',methods=['GET','POST'])
def show_online_doctors():
	chats = db.child("chat").get()
	chats=(chats.val())
	available=[]
	for x in chats:
		if x['status']=='available':
			available.append(x)
	return render_template('show_docs.html',available=available)

@app.route('/show_online_docs',methods=['GET','POST'])
def join_chat():
	uid=request.form.get("duid",'')
	chats = db.child("chat").get()
	chats=(chats.val())
	for c in range(len(chats)):
		if uid==chats[c]["duid"]:
			token=chats[c]["token"]
			chats[c]["status"]="engaged"
	chatupdated={}
	chatupdated["chat"]=chats
	db.update(chatupdated)
	return urllib.urlopen('http://webr.tc/r/'+token)

@app.route('/notification',methods=['POST','GET'])
def notify():
	return render_template("indexnotification.html")

@app.route('/newappointment',methods=['POST','GET'])
def newappointment():
	if request.method=="POST":
		doctorid=request.form.get("doctorid",'')
		slot=request.form.get("slot",'')
		userid=session["user"]["id"]
		users = db.child("users").get()
		users=(users.val())
		registered=1
		for i in users:
			if i["id"]==email:
				flash("Email Already Exists")
				registered=0
		if registered:
			d={}
			d["id"]=email
			d["password"]=password
			d["name"]=name
			users.append(d)
			n={}
			n["users"]=users
			db.update(n)
			flash("Registered")
	return render_template("register.html")

@app.route('/blood',methods=['POST','GET'])
def blood():
	a={}
	a["bloodgroup"]=request.args['bloodgroup']
	a["uid"]=request.args['id']
	a["city"]=request.args['city']
	a["mobile"]=request.args['mobile']
	a["address"]=request.args['address']
	l=0
	users = db.child("users").get()
	users=(users.val())
	for user in users:
		if user["bloodgroup"]==a["bloodgroup"] and a["district"]==user["district"]:
			l+=1
	if l:
		data_message = {
			"Blood Required" : a["bloodgroup"],
			"body" : "Urgent Required",
		}
		result = push_service.notify_multiple_devices(registration_ids=registration_ids, data_message=data_message)

	return(l)

@app.route('/bloodapi',methods=['POST','GET'])
def bloodapi():
	a={}
	a["bloodgroup"]=request.args['bloodgroup']
	a["uid"]=request.args['id']
	a["city"]=request.args['city']
	a["mobile"]=request.args['mobile']
	a["address"]=request.args['address']
	users = db.child("users").get()
	users=(users.val())
	response={}
	c=0
	b=[]
	for user in users:
		if user["bloodgroup"]==a["bloodgroup"] and a["city"]==user["city"]:
			c+=1
			b.append(
				{
					"name":user["name"],
					"mobile":user["mobile"]
				}
			)
	
	if c:
		registration_ids = ["ewEDOBTYu-w:APA91bG-Gc9SZPT7YY82jubMJ-WYWfpfSe3JXc1T9oSuWQpwoIe1DZjrveXnOcagCdM3Px0iWVqSBqSvM1qWvBQy3bw9U3Ad8897qu3ZHSRVkwX_29oBxbhjTlmqoyrlIcRpHC8t9JgE"]
		message_title = "Sanskar"
		message_body = "Chutiya hai"
		result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body, message_icon="facebook.png")

	return jsonify(b)

@app.route('/question',methods=['POST','GET'])
def question():
	questions = db.child("questions").get()
	questions=(questions.val())
	queupdated={}
	if request.method=="POST":
		newque={}
		newque["id"]=generateid()
		newque["title"]=request.form.get("title",'')
		newque["body"]=request.form.get("body",'')
		newque["solved"]=0
		newque["timestamp"]=generatetimestamp()
		newque["private"]=request.form.get("private",'')
		newque["author"]=session["user"]["name"]
		newque["upvotes"]=[]
		questions.append(newque)
	queupdated["questions"]=questions
	db.update(queupdated)	
	for i in comments:
		content.append(i["content"])
	return render_template("index.html",contents=content)

@app.route('/answer',methods=['POST','GET'])
def answer():
	questions = db.child("questions").get()
	questions=(questions.val())
	questionid=str(request.args.get('que'))
	if request.method=="POST":
		answer=request.form.get("answer",'')
		for que in range(len(questions)):
			if questions[que]["id"]==questionid:
				answers=questions[que]["answers"]
				questions[que]["answers"].append(answer)
				break
		queupdated={}
		queupdated["questions"]=questions
		db.update(queupdated)
	content=[]
	for que in questions:
		if questionid==que["id"]:
			answers=que["answers"]
			break
	return render_template("answer.html",answers=answers)

if __name__ == '__main__':
    app.run( debug=True )