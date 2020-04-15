from flask import Flask,request,jsonify
from flask_restful import Resource,Api
from flask_pymongo import pymongo
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)
"""1.Registration of user
   2. Each user have 6 token
   3. store a sentence on database for 1 token
   4. retrieve his stored sentence from database for 1 token
"""
app.config['MONGO_URI']="mongodb://localhost:27017/Sentence"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["Sentence"]
users=mydb["feedSentence"]

def UserExist(username):
	if users.find({"Username":username}).count()==0:
		return False
	else:
		return True

class Register(Resource):
	def post(self):
		#get posted data by the user
		postedData = request.get_json()
		#get data
		username = postedData["username"]
		password = postedData["password"]
		if UserExist(username):
			retJson={
				"status":301,
				"msg":"Invalid username"
			}
			return jsonify(retJson)
		hashed_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

		#store username into database
		users.insert({
			"Username":username,
			"Password":hashed_pw,
			"Tokens":6
			}) 
		retJson = {
		"status":200,
		"msg": "you successfully signed up"
		}
		return jsonify(retJson)
def verifyPW(username,password):
	hashed_pw=users.find({
		"Username":username
		})[0]["Password"]
	if bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw:
		return True
	else:
		return False
def countTokens(username):
	tokens=users.find({
		"Username":username
		})[0]["Tokens"]
	return tokens

class Store(Resource):
	def post(self):
		#get posted data by the user
		postedData = request.get_json()
		#read data 
		username = postedData["Username"]
		password = postedData["Password"]
		sentence = postedData["Sentence"]
		#verify username pass match
		correct_pw=verifyPW(username,password)
		if not correct_pw:
			retJson={
			    "status": 302
			}
			return jsonify(retJson)

		#verify user has enough tokens
		num_tokens = countTokens(username)
		if num_tokens<=0:
			retJson={
			"status":301,
			"msg":"you have less tokens to store sentence"
			}
			return jsonify(retJson)
		#store the sentence
		users.update({
			"Username":username
			},{
			"$set":{
			"Sentence":sentence,
			"Tokens":num_tokens-1
			}}
			)
		retJson={
			"status":200,
			"msg":"sentence saved successfully"
			}
		return jsonify(retJson)

class Get(Resource):
	def post(self):
		postedData=request.get_json()
		username = postedData["Username"]
		password = postedData["Password"]
		correct_pw=verifyPW(username,password)
		if not correct_pw:
			retJson={
			"status": 302
			}
			return jsonify(retJson)
		
		num_tokens = countTokens(username)
		if num_tokens<=0:
			retJson={
			"status":301,
			"msg":"you have less tokens to store sentence"
			}
			return jsonify(retJson)
		
		sentence=users.find({
			"Username":username
		})[0]["Sentence"]
		retJson={
			"Status":200,
			"sentence":sentence
		}
		return jsonify(retJson)




api.add_resource(Register,'/register')
api.add_resource(Store,'/store')
api.add_resource(Get,'/get')


if __name__ == '__main__':
	app.run(debug=True)






