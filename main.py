from fastapi import FastAPI
from datetime import datetime
app = FastAPI()

login_logs = []

@app.get("/")
def read_root():
    return {"Hello": "User"}

@app.post("/login")
def read_item(username: str, password: str):
    if username == "admin" and password == "test123":
        login_logs.append({"username": username, "status": "Success", "timestamp": datetime.now()})
        return {"message": "Login Success"}
    else:
        login_logs.append({"username": username, "status": "Failed", "timestamp": datetime.now()})
        return {"message": "Login Failed"}

@app.get("/access_logs")
def generate_report():
    return {"data": login_logs}
