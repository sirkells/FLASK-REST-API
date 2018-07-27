from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient






app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.mathdb
userNum = db['userNum']
userNum.insert_one({"num_of_users": 0})

class Visit(Resource):
    def get(self):
        prev_num = userNum.find({})[0]["num_of_users"]
        new_num = prev_num + 1
        userNum.update({}, {"$set": {"num_of_users": new_num}})
        return str("Hello user " + str(new_num))



#check if the data poted is correct
def checkPostedData(postedData, functionName):
    if (functionName == 'Add' or functionName == 'Subtract' or functionName == 'Multiply'):
        if 'x' not in postedData or 'y' not in postedData:
            return 301
        #isinstance is used to check if a value is of a given datatype
        elif not isinstance(postedData['x'], str) and not isinstance(postedData['y'], str):
            return 200
        else:
            return 303
    
    if (functionName == 'Divide'):
        if 'x' not in postedData or 'y' not in postedData:
            return 301
        elif not isinstance(postedData['x'], str) and not isinstance(postedData['y'], str):
            return 200
        elif postedData['y']==0:
            return 302
        elif isinstance(postedData['y'], str) or isinstance(postedData['x'], str):
            return 303
        else:
            return 303

error301 = {
                'Message': 'An error occured: one or more value not given',
                'Status Code': 301
            }
error302 = {
                'Message': 'An error occured: one or more value is zero',
                'Status Code': 302
            }
error303 = {
                'Message': 'An error occured: one or more value is invalid',
                'Status Code': 303
            }

 #if Add was requested using the POST mtd it would come here
class Add(Resource):
    def post(self):
       
    #step1: get posted data
        postedData = request.get_json()
    
     #step2 check if data posted is correct
        status_code = checkPostedData(postedData, 'Add')
        if (status_code == 301):
            return jsonify(error301)
        
        if (status_code == 303):
            return jsonify(error303)
    #step3: if posted data is correct perform this
        x = postedData['x']
        y = postedData['y']
        ret = x + y
        retJson = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retJson)

#if Add was requested using the POST mtd it would come here
class Subtract(Resource):
    def post(self):
        #step1: get posted data
        postedData = request.get_json()
    
     #step2 check if data posted is correct
        status_code = checkPostedData(postedData, 'Subtract')
        if (status_code == 301):
            return jsonify(error301)
        
        if (status_code == 303):
            return jsonify(error303)
    #step3: if posted data is correct perform this
        x = postedData['x']
        y = postedData['y']
        ret = x - y
        retJson = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retJson)
class Multipy(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, 'Multiply')
        if (status_code == 301):
            return jsonify(error301)
        if (status_code == 302):
            return jsonify(error302)
        if (status_code == 303):
            return jsonify(error303)
    #step3: if posted data is correct perform this
        x = postedData['x']
        y = postedData['y']
        
        ret = x * y
        retJson = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retJson)

class Divide(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, 'Divide')
        if (status_code == 301):
            return jsonify(error301)
        if (status_code == 302):
            return jsonify(error302)
        
        if (status_code == 303):
            return jsonify(error303)
    #step3: if posted data is correct perform this
        x = postedData['x']
        y = postedData['y']
        if y == 0:
            return jsonify(error302)

        res = x / y
        #round() rounds up to 2d.p
        ret = round(res, 2)
        retJson = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retJson)


#Add resources to api
api.add_resource(Add, '/add')
api.add_resource(Subtract, '/sub')
api.add_resource(Multipy, '/mult')
api.add_resource(Divide, '/div')
api.add_resource(Visit, '/hello')


@app.route('/')
def home():
    return 'Hello World'







if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")