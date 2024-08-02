import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, datetime

# Database connection
mydb = mysql.connector.connect(
    host="localhost", user="root", password="", database="demobase"
)

# Pydantic model for customer
class Customer(BaseModel):
    name: str
    address: str
    date_of_birth: str
    education: str

# Function to calculate age from date of birth
def calculate_age(born):
    today = date.today()
    try: 
        birthday = born.replace(year=today.year)
    except ValueError: 
        birthday = born.replace(year=today.year, month=born.month + 1, day=1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year

# FastAPI application
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/create_table")
def create_table():
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255), date_of_birth DATE, age INT, education VARCHAR(255))")
    return {"Table": "Created"}

@app.post("/insert")
def insert_data(data: Customer):
    mycursor = mydb.cursor()
    born = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    age = calculate_age(born)
    sql = "INSERT INTO customers (name, address, date_of_birth, age, education) VALUES (%s, %s, %s, %s, %s)"
    val = (data.name, data.address, born, age, data.education)
    mycursor.execute(sql, val)
    mydb.commit()
    return {"Data": "Inserted"}

@app.get("/get_data")
def get_data():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM customers")
    myresult = mycursor.fetchall()
    return myresult

@app.delete("/delete_data")
def delete_data(id: int):
    mycursor = mydb.cursor()
    sql = "DELETE FROM customers WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    mydb.commit()
    return {"Data": "Deleted"}

@app.post("/update_data")
def update_data(id: int, data: Customer):
    mycursor = mydb.cursor()
    born = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    age = calculate_age(born)
    sql = "UPDATE customers SET name = %s, address = %s, date_of_birth = %s, age = %s, education = %s WHERE id = %s"
    val = (data.name, data.address, born, age, data.education, id)
    mycursor.execute(sql, val)
    mydb.commit()
    return {"Data": "Updated"}
