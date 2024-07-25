from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from bson.objectid import ObjectId

# MongoDB connection
uri = "mongodb+srv://faizafarooq2325:0wN0L7ARAYZoOKP5@fastapp.cq8sl5t.mongodb.net/?retryWrites=true&w=majority&appName=FastApp"
client = MongoClient(uri)
db = client.fastapp
users = db.users


# FastAPI app
app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class User(BaseModel):
    user: str
    password: str


# Routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/register")
def create_user(user: User):
    # Hash the user's password
    hashed_password = pwd_context.hash(user.password)
    user_dict = {"user": user.user, "password": hashed_password}
    
    try:
        users.insert_one(user_dict)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"msg": "User registered successfully"}

@app.post("/login")
def login_user(user: User):
    user_in_db = users.find_one({"user": user.user})
    if not user_in_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify password
    if not pwd_context.verify(user.password, user_in_db["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"msg": "Login successful"}
