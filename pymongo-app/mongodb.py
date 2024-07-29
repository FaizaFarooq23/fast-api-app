from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from bson.objectid import ObjectId
from datetime import datetime
from typing import List

# MongoDB connection
uri = "mongodb+srv://faizafarooq2325:0wN0L7ARAYZoOKP5@fastapp.cq8sl5t.mongodb.net/?retryWrites=true&w=majority&appName=FastApp"
client = MongoClient(uri)
db = client.fastapp
users = db.users
access_logs = db.access_logs

# FastAPI app
app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class AccessLog(BaseModel):
    username: str
    status: str
    timestamp: datetime

# Custom encoder function
def serialize_mongo_document(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
        doc['timestamp'] = doc['timestamp'].isoformat()
    return doc

# Routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/register")
def create_user(user: User):
    # Hash the user's password
    hashed_password = pwd_context.hash(user.password)
    user_dict = {"username": user.username, "password": hashed_password}

    try:
        users.insert_one(user_dict)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already exists")

    return {"message": "User registered successfully"}

@app.post("/login")
def login_user(user: User):
    user_in_db = users.find_one({"username": user.username})

    # Log the access attempt only if the user exists
    if user_in_db:
        status = "Success" if pwd_context.verify(user.password, user_in_db["password"]) else "Failed"
        access_log = AccessLog(username=user.username, status=status, timestamp=datetime.now())
        access_logs.insert_one(access_log.model_dump())
        
        if status == "Failed":
            raise HTTPException(status_code=400, detail="Invalid username or password")
    else:
        # Log the attempt for an invalid user
        access_log = AccessLog(username=user.username, status="Failed", timestamp=datetime.now())
        access_logs.insert_one(access_log.dict())
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}

@app.get("/access_logs")
def get_access_logs():
    # Retrieve all user names
    registered_users = {user['username'] for user in users.find({}, {"_id": 0, "username": 1})}
    
    # Filter access logs to only include logs for registered users
    logs = access_logs.find({"username": {"$in": list(registered_users)}})
    return [serialize_mongo_document(log) for log in logs]

@app.put("/update-password")
def update_password(user: User):
    user_in_db = users.find_one({"username": user.username})

    if user_in_db:
        # Hash the new password
        hashed_password = pwd_context.hash(user.password)
        users.update_one({"username": user.username}, {"$set": {"password": hashed_password}})
        return {"message": "Password updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="User not found")
    
@app.delete("/delete-user")
def delete_user(user: User):
    user_in_db = users.find_one({"username": user.username})

    if user_in_db:
        users.delete_one({"username": user.username})
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid User")
