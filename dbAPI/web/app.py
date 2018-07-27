from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt







app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.SentenceDB
users = db.Users

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True
class Register(Resource):
    def post(self):
        #step1 get posted data from user
        postedData = request.get_json()

        #get the data
        username = postedData['username']
        password = postedData['password']
        if UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Username already exists"
            }
            return jsonify(retJson)

        hashedpw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({ "Username": username, "Password": hashedpw, "Sentence": "", "Token": 5 })

        retJson = {
            "status": 200,
            "message": "You succesfully signed up"

        }
        return jsonify(retJson)




        #store username and pwd into db


def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Token"]
    return tokens

class Store(Resource):
    def post(self):
        #step1 get posteddata
        postedData = request.get_json()
        #step2 read posted data
        username = postedData['username']
        password = postedData['password']
        sentence = postedData['sentence']
        #step3 check if pasword match
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302,
                "message": "invalid username/pwd"
            }
            return jsonify(retJson)


    #step4 verify user has enough tokens
        num_tokens= countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301,
                "Error": "Sentence not saved due to insufficient tokens, buy more tokens"
            }
            return jsonify(retJson)

    #step5 store the sentence, take one token away and return 200 ok
        users.update({
            "Username": username },
        {
                "$set":{
                    "Sentence": sentence,
                    "Token": num_tokens - 1
            }
        })

        retJson = {
                "status": 200,
                "message": "Sentence saved succesfully"
            }
        return jsonify(retJson)

class Get(Resource):
    def post(self):
        #step1 get posteddata
        postedData = request.get_json()
        #step2 read posted data
        username = postedData['username']
        password = postedData['password']
        #step3 check if pasword match
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

    #step4 verify user has enough tokens
        num_tokens= countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)
        sentence = users.find({"Username": username})[0]["Sentence"]
        #Make the user pay for get sentence
        users.update({
            "Username": username },
        {
                "$set":{
                    "Token": num_tokens - 1
            }
        })
        retJson = {
                "status": 200,
                "sentence": sentence
            }
        return jsonify(retJson)




api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')











if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
