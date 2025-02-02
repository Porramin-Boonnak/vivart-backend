import azure.functions as func
from flask import request, Flask,jsonify
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from bson import json_util
uri = "mongodb+srv://se1212312121:se1212312121@cluster0.kjvosuu.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(uri)

app = Flask(__name__)

db = client["vivart"]
customer = db["customer"]
post = db["post"]

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the WSGI handler.
    """
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

@app.route("/", methods=["GET"])
def test():
    return("lfkpowkoefk")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    find = customer.find_one({"username": data["username"]})
    if not find:
        customer.insert_one(data)
        return {"message": "Signup successful"}, 201
    return {"message": "Signup fail"}, 401

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    find = customer.find_one({"username": data["username"], "password": data["password"]})
    if find:
        return {"message": "login successful"}, 201
    return {"message": "login fail"}, 401

@app.route("/post", methods=["POST"])
def postdata():
    data = request.get_json()
    post.insert_one(data)
    return {"message": "upload successful"}, 200


@app.route('/post/<string:_id>', methods=['GET'])
def getpost(_id):
    object_id = ObjectId(_id)  # แปลง _id เป็น ObjectId
    data = post.find_one({"_id": object_id})  # ค้นหาจาก MongoDB
    if data:
        data['_id'] = str(data['_id'])  # แปลง ObjectId เป็น string เพื่อให้ JSON ใช้ได้
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404
    
@app.route('/post', methods=['GET'])
def getallpost():
    data = list(post.find())  # ดึงข้อมูลทั้งหมดจาก MongoDB
    if data:
        # แปลง ObjectId เป็น string ในทุก document
        for item in data:
            item['_id'] = str(item['_id'])  # แปลง ObjectId เป็น string
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404