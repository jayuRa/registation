from multiprocessing import connection
import shutil,json,sqlalchemy,os,math,datetime
from fastapi import FastAPI,Request,Body,File,UploadFile,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine,MetaData,Table,Column,ForeignKey
from pydantic import BaseModel  
from sqlalchemy.sql.sqltypes import Integer, String
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import relationship,Session



app=FastAPI()

templates=Jinja2Templates(directory="templates")

engine=create_engine("mysql+pymysql://admin:admin@localhost/db1")

conn=engine.connect()
meta=MetaData()
meta.create_all(engine)

student=Table(
    'student',meta,
    Column('id',Integer,primary_key=True),
    Column('fname',String(255)),
    Column('lname',String(255)),
    Column('course',String(255)),
    Column('gender',String(255)),
    Column('phone',String(255)),
    Column('country',String(255)),
    Column('state',String(255)),
    Column('city',String(255)),
    Column('address',String(255)),
    Column('vehicle',String(255)),
    Column('image',String(255))
)

country=Table(
    'country',meta,
    Column('id',Integer, ForeignKey("student.country")),
    Column('name',String(255))
)

state=Table(
    'state',meta,
    Column('id',Integer,primary_key=True),
    Column('name',String(255)),
    Column('country_id',Integer)
)
city=Table(
    'city',meta,
    Column('id',Integer,primary_key=True),
    Column('name',String(255)),
    Column('state_id',Integer)
)

class User(BaseModel):
    fname:str
    lname:str
    course:str
    gender:str
    phone:str
    country:str
    state:str
    city:str
    address:str
    vehicle:str
    image:str

meta.create_all(engine)

def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

date=datetime.datetime.now()#
year=date.strftime("%Y")
month=date.strftime("%b")
day_of_month = datetime.datetime.now().day
week = (day_of_month - 1) // 7 + 1

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

app.mount(
    "/home/python/Documents/registration_page/registation/image_file",
    StaticFiles(directory=Path(__file__).parent.absolute() / "image_file"),
    name="image_file",
)


@app.api_route("/", response_class=HTMLResponse,methods=['GET','POST'])
async def showData(request: Request):
    
    formData=await request.form()
    pageid=formData.get('pageid')
    if pageid ==None:
        pageid=1
        
    pageId=int(pageid)

    result1=conn.execute(f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id').fetchall()
    resultLen=(len(result1))
    limit=5
    start=(pageId - 1)* limit

    result=conn.execute(f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id limit {start},{limit}').fetchall()   
    return templates.TemplateResponse('display.html', {"request": request,"result":result,"resultLen":resultLen})

@app.get("/update/{id}", response_class=HTMLResponse)
async def getStudentData(id:int ,request: Request):
    
    result=conn.execute(student.select().where(student.c.id==id)).fetchone()
    countryData=conn.execute(country.select()).fetchall()
    
    return templates.TemplateResponse('update.html', {"request": request,"result":result,"countryData":countryData})

@app.post("/updatestudentdata",response_class=HTMLResponse)
async def updateStudentData(request:Request, image: UploadFile = File(...)):
   
    formData = await request.form()
    insertUpdateData('update',formData,image) 

    #result=conn.execute(student.select()).fetchall()
    url="/"
    response = RedirectResponse(url=url)
    return response
    #return templates.TemplateResponse('display.html', {"request": request,"result":result})

@ app.get("/delete/{id}", response_class=HTMLResponse)
async def deleteStudentData(id:int,request: Request):

    conn.execute(student.delete().where(student.c.id==id))
    data=conn.execute(student.select()).fetchall()
    
    url="/"
    response = RedirectResponse(url=url)   # how to redirect to regsiter endpoint with user data ?
    return response


@app.get("/registration", response_class=HTMLResponse)
def registrationPage(request: Request):
    countryData=conn.execute(country.select()).fetchall()
    return templates.TemplateResponse('registration.html', {"request": request,"countryData":countryData})


@app.post("/createstudent")
async def createStudent(request:Request, image: UploadFile = File(...)):
    formData=await request.form()
    insertUpdateData('insert',formData,image) 
   
    url="/"
    response = RedirectResponse(url=url) 
    return response
    
@app.api_route("/cancle", response_class=HTMLResponse,methods=['GET','POST'])
async def cancle(request: Request):
    url="/"
    response = RedirectResponse(url=url)
    return response

@app.api_route("/stateData", response_class=HTMLResponse, methods=['POST'])
async def stateData(request: Request):

    formData = await request.form() 
    getData = formData.get('countryData')
    print(getData)
    return getStateDetails(getData,'state','country_id')

@app.api_route("/cityData", response_class=HTMLResponse, methods=['POST'])
async def cityData(request: Request):
    
    formData = await request.form()
    getData = formData.get('stateData')
    return getStateDetails(getData,'city','state_id')
    
@app.api_route("/getRecords", response_class=HTMLResponse, methods=['POST'])
async def ajax_response(request: Request):
    formData = await request.form()
    pageid=formData.get('pageid')
    input=formData.get('input')

    if input != '':
        query=f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id WHERE fname LIKE "%%{input}%%" OR lname LIKE "%%{input}%%" OR course LIKE "%%{input}%%" OR gender LIKE "{input}" OR phone LIKE "%%{input}%%" OR country LIKE "%%{input}%%" OR state LIKE "%%{input}%%" OR city LIKE "%%{input}%%" OR address LIKE "%%{input}%%" OR vehicle LIKE "%%{input}%%"'
    else:
        query=student.select()
    
    resultLength=conn.execute(query).fetchall()
    resultLength=len(resultLength)

    if pageid ==None:
        pageid=1
        
    pageid=int(pageid)
    limit=5
    start=(pageid - 1)* limit

    query=f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id limit {start},{limit}'

    if input != '':
        query=f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id WHERE fname LIKE "%%{input}%%" OR lname LIKE "%%{input}%%" OR course LIKE "%%{input}%%" OR gender LIKE "{input}" OR phone LIKE "%%{input}%%" OR country LIKE "%%{input}%%" OR state LIKE "%%{input}%%" OR city LIKE "%%{input}%%" OR address LIKE "%%{input}%%" OR vehicle LIKE "%%{input}%%" limit {start},{limit} '

    result=conn.execute(query).fetchall()
    record={}
    k=0
    for i in result:
        d=dict(i)
        record[k]=d
        k+=1

    jsonData = json.dumps({'record':record,'totalCount':resultLength})
    return jsonData
    
    
@app.api_route("/search", response_class=HTMLResponse,methods=['GET','POST'])
async def searchData(request: Request):
    formData = await request.form()
    input=formData.get('input')
    pageid=formData.get('pageid')

    query=f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id WHERE fname LIKE "%%{input}%%" OR lname LIKE "%%{input}%%" OR course LIKE "%%{input}%%" OR gender LIKE "{input}" OR phone LIKE "%%{input}%%" OR country LIKE "%%{input}%%" OR state LIKE "%%{input}%%" OR city LIKE "%%{input}%%" OR address LIKE "%%{input}%%" OR vehicle LIKE "%%{input}%%"'

    resultLength=conn.execute(query).fetchall()
    resultLength=len(resultLength)

    if pageid ==None:
        pageid=1
            
    pageid=int(pageid)
    limit=5
    start=(pageid - 1)* limit

    query=f'SELECT student.*, country.name, statedata.name as sname, citydata.name as cname FROM student JOIN country on student.country = country.id JOIN statedata on student.state = statedata.id JOIN citydata on student.city =citydata.id WHERE fname LIKE "%%{input}%%" OR lname LIKE "%%{input}%%" OR course LIKE "%%{input}%%" OR gender LIKE "{input}" OR phone LIKE "%%{input}%%" OR country LIKE "%%{input}%%" OR state LIKE "%%{input}%%" OR city LIKE "%%{input}%%" OR address LIKE "%%{input}%%" OR vehicle LIKE "%%{input}%%" limit {start},{limit}'
 
    result=conn.execute(query).fetchall()

    data={}
    k=0
    for i in result:
        d=dict(i)
        data[k]=d
        k+=1

    jsonData = json.dumps({'data':data,'totalCount':resultLength})
    return jsonData

def getStateDetails(getData,tableName,columnName):
    value=tableName,getData,columnName
    stateQuery=f"SELECT id,name FROM {tableName} WHERE {columnName}={getData}"
    stateList=conn.execute(stateQuery).fetchall()#===>
    st=dict(stateList)    
    jsonData = json.dumps(st)

    return jsonData

def insertUpdateData(type,formData,image: UploadFile = File(...)):
    
    dateNow=date.strftime("%Y-%m-%d")
    imageFilename=f'{dateNow}_'+image.filename

    if not os.path.isdir(f"/home/python/Documents/registration_page/registation/image_file/{year}/{month}/{week}"):
        os.makedirs(f"/home/python/Documents/registration_page/registation/image_file/{year}/{month}/{week}")

    if image.filename != '':
        with open(f"/home/python/Documents/registration_page/registation/image_file/{year}/{month}/{week}/{imageFilename}","wb+") as buffer:
            shutil.copyfileobj(image.file,buffer)

    imageName=f"/home/python/Documents/registration_page/registation/image_file/{year}/{month}/{week}/{imageFilename}"

    fname=formData["firstname"]
    lname=formData["lastname"]
    course=formData["course"]
    gender=formData.get("gender") # for single values 
    phone=formData["phone"]
    country=formData["country"]
    state=formData["state"]
    city=formData["city"]
    address=formData["address"]
    vehicl=formData.getlist("vehicle[]") # for multiple values 
    vehicle=(','.join(vehicl))


    if type == 'insert':
        query=f"INSERT INTO student (fname,lname,course,gender,phone,country,state,city,address,vehicle,image) VALUES ('{fname}','{lname}','{course}','{gender}','{phone}','{country}','{state}','{city}','{address}','{vehicle}','{imageName}')"
        result=conn.execute(query)
    else:
        id = formData['id'] 
        query=f"UPDATE student SET fname='{fname}',lname='{lname}',course='{course}',gender='{gender}',phone='{phone}',country='{country}',state='{state}',city='{city}',address='{address}',vehicle='{vehicle}' WHERE id={id}"
        result=conn.execute(query)

        if image.filename !="":
            query=f"UPDATE student SET image='{imageName}' WHERE id={id}"
            conn.execute(query)
        