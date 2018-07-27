from flask import Flask, jsonify, request, json
from pymongo import MongoClient
from flask_restful import Api, Resource
import bcrypt


app = Flask(__name__)
api = Api(app)

#for docker env use this
client = MongoClient("mongodb://db:27017")
#for normal local env use this
#client = MongoClient('127.0.0.1', 27017), db = client["BankAPI"]

db = client.BankAPI
users = db["Users"]

def UserExist(username):
    #return false if user doesnt exist
    if users.find({"Username":username}).count() == 0:
        return False
    #return true if it does
    else:
        return True

#func for json status code and msg
def getStatusMsg(status, message):
    retJson = {
        "status": status,
        "message": message
    }
    return retJson

#function to verify pwd match with user
def verifyPw(username, password):
    #gets the pwd of the corresponding username and save it as hashed_pw
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]
    #hashes the given pwd by the user and compares it with the saved hashed pwd. ret true if equal
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False
#verify logindetails: returns  true is theres an error status message and False with NOne status msg
def verifyLoginDetails(username, password):
    if not UserExist(username):
        return getStatusMsg(301, "Username doesnt exist"), True
    correct_pw = verifyPw(username, password)
    if not correct_pw:
        return getStatusMsg(302, "Incorrect password" ), True

    return None, False
#check user balance
def balance(username):
    amount = users.find({"Username": username})[0]["Balance"]
    return amount

#check user debt
def debt(username):
    debt = users.find({"Username": username})[0]["Debt"]
    return debt

#Ubdate balance
def updateBalance(username, balance):
    users.update({"Username": username}, {"$set": {"Balance": balance }})
#update debt
def updateDebt(username, balance):
    users.update({"Username": username}, {"$set": {"Debt": balance }})
#Resources
class Register(Resource):
    def post(self):
        #get data from user
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        #check if user exist
        if UserExist(username):
            return jsonify(getStatusMsg(301, "username already taken"))
            #if user doesnt exist, hash password
        hashedpw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #insert user in db
        users.insert({
            "Username": username,
            "Password": hashedpw,
            "Balance": 0,
            "Debt": 0
        })
        return jsonify(getStatusMsg(200, "account succesfully created"))

class Add(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]
        #verify logindetails
        retJson, error = verifyLoginDetails(username, password)
        if error:
            return jsonify(retJson)
        #check if amount is valid
        if amount<=0:
            return jsonify(getStatusMsg(304, "amount must be >0 "))
        #get user account balance
        cash = balance(username)
        #subtract bank charge
        amount-=1
        #add bankcharge to bank balance, remember to create account for bank with username=BANK
        bank_cash = balance("BANK")
        updateBalance("BANK", bank_cash+1)
        #add amount to user balance
        updateBalance(username, cash+amount)

        return jsonify(getStatusMsg(200, "Amount added succesfully to account"))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]
        recipient_username = postedData["recipient"]

        retJson, error = verifyLoginDetails(username, password)
        if error:
            return jsonify(retJson)
        if amount<=0:
            return jsonify(getStatusMsg(304, "amount must be >0 "))
        #check if userbalance is greater than transfer amount
        if amount < balance(username):
            return jsonify(getStatusMsg(305, "insufficient account balance"))

        user_balance = balance(username)
        recipient_balance = balance(recipient_username)
        #check if user has sufficient balance
        if user_balance <=0:
            return jsonify(getStatusMsg(305, "insufficient account balance"))
        #chek if reciepient exist
        if not UserExist(recipient_username):
            return jsonify(getStatusMsg(306, "user doesnt exist"))
        #bank charge
        recipient_balance-=1
        bank_cash = balance("BANK")

        updateBalance("BANK", bank_cash+1)
        updateBalance(username, user_balance-amount)
        updateBalance(recipient_username, recipient_balance+amount)

        return jsonify(getStatusMsg(200, "Amount Sent succesfully"))

class CheckBalance(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        retJson, error = verifyLoginDetails(username, password)
        if error:
            return jsonify(retJson)
        #the value 0 means that mongodb should exclude password and _id when showing the user
        retJson = users.find({"Username": username}, {"Password": 0, "_id": 0})[0]
        return jsonify(retJson)

class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        retJson, error = verifyLoginDetails(username, password)
        if error:
            return jsonify(retJson)
        if amount<=0:
            return jsonify(getStatusMsg(304, "amount must be >0 "))
        old_balance = balance(username)
        old_debt = debt(username)


        old_balance-=1
        bank_cash = balance("BANK")

        updateBalance("BANK", bank_cash+1)
        updateBalance(username, old_balance+amount)
        updateDebt(username, old_debt+amount)
        return jsonify(getStatusMsg(200, "Loan succesfully added"))

class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        amount = postedData["amount"]

        retJson, error = verifyLoginDetails(username, password)
        if error:
            return jsonify(retJson)
        if amount<=0:
            return jsonify(getStatusMsg(304, "amount must be >0 "))
        old_balance = balance(username)
        if old_balance < amount:
            return jsonify(getStatusMsg(200, "Insufficient account balance"))

        old_debt = debt(username)
        updateBalance(username, old_balance-amount)
        updateDebt(username, old_debt-amount)
        return jsonify(getStatusMsg(200, "Loan payment succesfully added"))


api.add_resource(Register, '/register')
api.add_resource(Add, '/add')
api.add_resource(Transfer, '/transfer')
api.add_resource(CheckBalance, '/checkbal')
api.add_resource(TakeLoan, '/takeloan')
api.add_resource(PayLoan, '/payloan')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
