from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Connect to the database
# to run in virtualenv: https://sentry.io/answers/modulenotfounderror-when-working-with-fastapi-in-python/
import os
import uvicorn
from pydantic import BaseModel
import time
import datetime
from mysql_conn import MySQLConn
def current_milli_time():
    return round(time.time() * 1000)

def getDateYYYYMMDD():
    return datetime.today().strftime('%Y-%m-%d')

myConnLocal = {
     'host':'127.0.0.1',
    'user':'root',
    'password':"",
    'db':'reg'
}


db = MySQLConn(myConnLocal)
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    user_id: int
    username: str
    password: str
    created: str
    role_id: int
    status: int
class ContactUS(BaseModel):
    contactId: int
    name: str
    email: str
    message: str
class Person(BaseModel): # Maps to MySQL Table people.
    id: int
    lastName: str
    firstName: str
    email: str
    roleId: int

@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.post("/api/user")
async def postUser (user:User):
    qry="call usp_user_save (%s,%s,%s,%s,%s)" 
    values = [user.user_id, user.username, user.password,user.role_id, user.status]
    print ("values:",values)
    resp=await db.query(qry, values)
    print ("resp:",resp[0]) 
    return {"status":200,"userId":resp[0][0],"message":resp[0][2] }
@app.post("/api/contactus")
async def postContactUs (contact:ContactUS):
    qry="call usp_contact2_save (%s,%s,%s,%s,%s)" 
    values = [contact.contactId, contact.name, contact.email, contact.message,0]
    print ("postContactUs values:",values)
    resp=await db.query(qry, values)
    print ("resp:",resp[0]) 
    return {"status":200,"contactId":resp[0][0],"message":resp[0][2] }
@app.post("/api/auth")
async def postUser (user:User):
    print ("postUser called",user)
    qry="call usp_user_auth (%s,%s)"
    values = [user.username, user.password]
    print ("values:",values)
    resp=await db.query(qry, values)
    print ("resp:",resp[0])
    return {"status":200,"userId":resp[0][0],"message":resp[0][1] }

@app.post("/api/hack")
async def postUser (user:User): # YUCK
    print ("postUser called",user)
    sql= "select * from users where username='{0}' AND password='{1}'".format(user.username,user.password)
    print ("SQL:",sql)
    resp=await query(sql)
    print ("resp:",resp)
    if len(resp)>0:
        return {"status":200,"userId":resp[0][0],"message":"success" }
    else:
        return {"status":401,"userId":0,"message":"invalid username or password" }
    #return {"status":200,"userId":resp[0][0],"message":resp[0][1] }
@app.get("/api/users")
async def getUsers ():
    results = await db.query("SELECT * FROM view_users",[])
    rows=[]
    for result in results:
        row={
            'userId': result[0],
            'username': result[1],
            'password': result[2],
            'roleId': result[3],
            'status': result[4],
            'created':result[5],
        }

        rows.append(row)
    return rows
@app.get("/api/people") # READ
async def getPeople ():
    results = await db.query("SELECT * FROM people",[])
    rows=[]
    for result in results:
        row={
            'id': result[0],
            'last_name': result[1],
            'first_name': result[2],
            'email': result[3],
            'role_id': result[4],
            'created':result[5],
        }

        rows.append(row)
    return rows
@app.post("/api/person") # CREATE
async def postPost (person:Person):
    qry="call usp_person_save (%s,%s,%s,%s,%s)" 
    #insert = "INSERT INTO people (last_name, first_name, email, role_id, created) VALUES(%s,%s,%s,%s,SYSDATE())"
    values = [person.id, person.lastName, person.firstName, person.email,person.roleId]
    print ("values:",values)
    resp=await db.query(qry, values)
    print ("resp:",resp) 
    return {"status":200,"personId":resp[0][0],"message":resp[0][2] }
   
connIndex=1
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7001)