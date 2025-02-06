import azure.functions as func
from flask import request, Flask,jsonify
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from bson import json_util
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_bcrypt import Bcrypt
import jwt
import datetime
uri = "mongodb+srv://se1212312121:se1212312121@cluster0.kjvosuu.mongodb.net/"

client = MongoClient(uri)

app = Flask(__name__)
keyforlogin = "1212312121"
bcrypt = Bcrypt(app)
db = client["vivart"]
customer = db["customer"]
post = db["post"]

clientId = "1007059418552-8qgb0riokmg3t0t993ecjodnglvm0bj2.apps.googleusercontent.com"

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the WSGI handler.
    """
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

@app.route("/", methods=["GET"])
def test():
    return("lfkpowkoefk")

@app.route("/signup/email/google", methods=["POST"])
def signup_google():
    data = request.get_json()
    token = data.get("credential")
    if token :
        decoded_data = id_token.verify_oauth2_token(token, requests.Request(), clientId)
        find = customer.find_one({"email": decoded_data["email"]})
        if not find :
            return jsonify(decoded_data), 200
    elif "email" in data:
        find = customer.find_one({"email": data["email"]})
        if not find :
            return jsonify({"email" : data["email"]}), 200
    return {"message" : "fail"}, 400

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    find = customer.find_one({"username": data["username"]})
    if not find :
        if "password" in data :
            data["password"]=bcrypt.generate_password_hash(data["password"]).decode('utf-8')
        customer.insert_one(data)
        payload = {
        "username": data['username'],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)  
        }
        token = jwt.encode(payload, keyforlogin, algorithm="HS256")
        return jsonify(token), 200
    return {"message" : "fail"}, 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    token = data.get("credential")
    if token :
        decoded_data = id_token.verify_oauth2_token(token, requests.Request(), clientId)
        find = customer.find_one({"email": decoded_data["email"]})
        if find :
            payload = {
            "username": find['username'],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)  
            }
            token = jwt.encode(payload, keyforlogin, algorithm="HS256")
            return jsonify(token), 201
    elif "username" in data:
        find = customer.find_one({"username": data["username"]})
        if find:
            if bcrypt.check_password_hash(find["password"], data["password"]):
                payload = {
                "username": find['username'],
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)  
                }
                token = jwt.encode(payload, keyforlogin, algorithm="HS256")
                return jsonify(token), 201
    return {"message": "login fail"}, 401

@app.route("/post", methods=["POST"])
def postdata():
    data = request.get_json()
    post.insert_one(data)
    return {"message": "upload successful"}, 200


@app.route('/post/<string:_id>', methods=['GET'])
def getpost(_id):
    object_id = ObjectId(_id)  
    post.update_one({"_id": object_id}, {"$inc": {"views": 1}})
    data = post.find_one({"_id": object_id})  
    if data:
        data['_id'] = str(data['_id'])
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404
    
@app.route('/post', methods=['GET'])
def getallpost():
    data = list(post.find())  
    if data:
        for item in data:
            item['_id'] = str(item['_id'])  
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404
    
    
@app.route('/status', methods=['POST'])
def getstatus():
    data = request.get_json()
    decoded = jwt.decode(data["token"], keyforlogin, algorithms=["HS256"])
    find = customer.find_one({"username": decoded["username"]})
    if find:
        find['_id'] = str(find['_id'])  
        return jsonify(find),200
    else:
        return jsonify({"error": "Data not found"}), 404
    
@app.route('/update/like/<string:_id>', methods=["PUT"])
def updatelike(_id):
    object_id = ObjectId(_id)  
    user = request.get_json()
    find = post.find_one({"_id": object_id}) 
    if find:
        post.update_one({"_id": object_id}, {"$addToSet": {"like": user}}, upsert=True)
        return jsonify({"message": "successful"}), 200
    return jsonify({"message": "fail"}), 400

@app.route('/delete/like/<string:_id>', methods=['DELETE'])
def deletelike(_id):
    object_id = ObjectId(_id)  
    user = request.get_json()
    find = post.find_one({"_id": object_id})  
    if find:
        post.update_one({"_id": object_id}, {"$pull": {"like": user}}, upsert=True)
        return jsonify({"message": "successful"}), 200
    return jsonify({"message": "fail"}), 400