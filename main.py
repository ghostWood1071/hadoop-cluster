from fastapi import FastAPI
from pyhive import hive
from fastapi import Depends
from typing import *
from starlette.middleware.cors import CORSMiddleware
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
db_host = '192.168.100.126'
account = 'hduser'
db_port = 10000

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # can alter with time
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def execute(command:str):
    conn = hive.Connection(host=db_host, username=account, port=db_port)
    cursor = conn.cursor()
    cursor.execute(command)
    return cursor.fetchall()

def read_html(path): 
    with open(path, mode='r') as f:
       content = f.read() 
       return content

@app.get("/", response_class=HTMLResponse)
def index():
    return read_html("./html/index.html")

@app.get("/query")
def query(cols:str = "", db_result:List[Any] =  Depends(execute))->List[Any]:
    if not cols:
        return db_result
    def match_schema(x:Tuple[Any]):
        schema = cols.split(',')
        if len(x) != len(schema):
            # return Response("schema not match with value", status_code=500)
            raise Exception("schema not match with value")
        return dict(zip(schema, x))
    try:
        result:List[Any] = list(map(match_schema, db_result))
        return result;
    except Exception as e:
        return Response(content=str(e), status_code=500)

    
        

