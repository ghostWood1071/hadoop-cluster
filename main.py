from fastapi import FastAPI
from pyhive import hive
from fastapi import Depends
from typing import *
from starlette.middleware.cors import CORSMiddleware
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import requests
from starlette.responses import StreamingResponse
from mysql import connector
from db import Helper

app = FastAPI()
db_host = '192.168.100.126'
account = 'hduser'
db_port = 10000
dbname = 'videoprocessing'

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # can alter with time
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

mysqlHelper = Helper('localhost', '3307', 'root', 'hduser@123')
mysqlHelper.init_db('video_processing_dim')
mysqlHelper.create_table('colors', ['color_id int primary key', 'color_name varchar(20) not null', 'color_rgb varchar(11)'])
mysqlHelper.create_table('objects', ['object_id int primary key', 'object_name varchar(50) not null'])


app.mount("/static", StaticFiles(directory="static"), name="static")

class Person(BaseModel):
    upper: str = Field(default=None)
    lower: str = Field(default=None)

class Obj(BaseModel):
    name: str = Field(default=None)
    color: str = Field(default=None)

class QueryModel(BaseModel):
    just_human: bool = Field(default=False) 
    just_object: bool = Field(default=False)
    have_human: bool = Field(default=False)
    have_object: bool = Field(default=False)
    camera: str = Field(default=None)
    people: List[Person] = Field(default=None)
    objs: List[Obj] = Field(default=None)
    time_ranges:List[float] = Field(default=[0,0])

def execute(command:str):
    conn = hive.Connection(host=db_host, username=account, port=db_port, database=dbname)
    cursor = conn.cursor()
    cursor.execute(command)
    return cursor.fetchall()

def read_html(path): 
    with open(path, mode='r') as f:
       content = f.read() 
       return content

class ConditionBuilder():
    def __init__(self, camera:str,  people:List[Person], objs: List[Obj], times:List[float], just_human, just_object, have_human, have_object): 
        self.camera = camera
        self.times = times
        self.people = people
        self.objs = objs
        self.just_human = just_human
        self.just_object = just_object
        self.have_human = have_human
        self.have_object = have_object

    def get_person_properties(self, person:Person):
        person_condition = ""
        if person.upper is not None and person.upper != '':
            person_condition+=f"p.upper = '{person.upper}'"
        if person.lower is not None and person.lower != '':
            if person.upper is not None and person.upper != '':
                person_condition+= f" and p.lower = '{person.lower}'"
            else:
                person_condition += f"p.lower = '{person.lower}'"
        if person_condition == "" or (person.upper is None or person.upper == '') or  (person.lower is None or person.lower == ''): 
            return person_condition
        return f"({person_condition})"
        
    
    def get_object_properties(self, obj: Obj):
        object_condition = ""
        if obj.name is not None and obj.name != '':
            object_condition += f"o.name = '{obj.name}'"
        if obj.color is not None and obj.color !='':
            if obj.name is not None and obj.name != '':
                object_condition += f" and o.color = '{obj.color}'"
            else:
                object_condition += f"o.color = '{obj.color}'"
        if object_condition == "" or (obj.name is None or obj.name == '') or (obj.color is None or obj.color == ''):
            return object_condition
        return f"({object_condition})"
    
    def build_people_condition(self):
        if self.have_human:
            return "p.rowkey is not null"
        if len(self.people) >= 2:
            people_conditions = list(map(self.get_person_properties, self.people))
            if len(people_conditions) >= 2:
                return  ' or '.join(people_conditions)
        if  len(self.people) == 1:
            return self.get_person_properties(self.people[0])
        
    
    def build_objects_condtion(self):
        if self.have_object: 
            return 'o.rowkey is not null'
        if len(self.objs) >= 2:
            objects_conditions = map(self.get_object_properties, self.objs)
            return ' or '.join(list(objects_conditions))
        if len(self.objs) == 1:
            return self.get_object_properties(self.objs[0])
        
        
    def build_times(self):
        q_time_min = self.times[0]
        q_time_max = self.times[1]
        if q_time_max < q_time_min:
            if q_time_max >0:
                raise Exception("wrong time range")
        if q_time_min == 0:
            return f"({q_time_max}>=s.time_end and s.time_start<{q_time_max})"
        if q_time_max == 0:
            return f"(s.time_start>={q_time_min})"
        return f"({q_time_max}>=s.time_end and s.time_start<{q_time_max})\nand ({q_time_min}<s.time_end and s.time_start<={q_time_min})"
    
    def build(self, tbl_con = 'segment_id', tbl_alias = 's', op='and'):
        cam_condition =""
        if (self.camera  is not None) and self.camera != '':
            cam_condition = f"v.location = '{self.camera}'"
        
        print(cam_condition)

        if self.times[0] == 0 and self.times[1] == 0:
            time_condition = ""
        else:
            time_condition =  self.build_times()
        
        where_condition = ""
        if self.just_object:
            where_condition = f"exists (select o.{tbl_con} from things o where {self.build_objects_condtion()} and o.{tbl_con} = {tbl_alias}.rowkey)"
        elif self.just_human:
            where_condition = f"exists (select p.{tbl_con} from people p where {self.build_people_condition()} and p.{tbl_con} = {tbl_alias}.rowkey)"
        else:
            people_condition = self.build_people_condition()
            objects_condition = self.build_objects_condtion()
            if people_condition != '' and objects_condition !='':
                where_condition = f"(exists (select p.{tbl_con} from people p where {people_condition} and p.{tbl_con} = {tbl_alias}.rowkey)) {op} (exists (select o.{tbl_con} from things o where {objects_condition} and o.{tbl_con} = {tbl_alias}.rowkey))"

            if  objects_condition != '' and people_condition == '':
                where_condition = f'exists (select o.{tbl_con} from things o where {objects_condition} and o.{tbl_con} = {tbl_alias}.rowkey)'
            
            if objects_condition == '' and people_condition != '':
                where_condition = f'exists (select p.{tbl_con} from people p where {people_condition} and p.{tbl_con} = {tbl_alias}.rowkey)'
                

        conditions = [cam_condition, time_condition, where_condition]
        for i in range(0, conditions.count('')):
            conditions.remove('')
        if len(conditions) == 0:
            return ''
        #if (cam_condition != '' or  time_condition != '' or cam_condition is not None or time_condition is not None) and (where_condition == '' or where_condition is None):
        return 'where '+ ' and '.join(conditions)
        # return 'where exists ()'
        #where_condition = where_condition + time_condition
      


def get_query(camera, people, objs, times, just_human, just_object, have_human, have_object):
    builder = ConditionBuilder(camera, people, objs, times, just_human, just_object, have_human, have_object)
    query = f'''
        select s.rowkey as segment_id,
        s.video_id,
        v.location,
        s.url,
        s.time_start,
        s.time_end,
        f.content as cover
        from segments as s
        join  frames as f
        on s.cover = f.rowkey
        join cameras as v
        on v.rowkey = s.video_id
        {builder.build()} order by s.time_start;
    '''
    return query


def handle_result(cols:str = "", db_result:List[Any]=None):
    if not cols:
        return db_result
    def match_schema(x:Tuple[Any]):
        schema = cols.split(',')
        if len(x) != len(schema):
            raise Exception("schema not match with value")
        return dict(zip(schema, x))
    result:List[Any] = list(map(match_schema, db_result))
    return result


@app.get("/", response_class=HTMLResponse)
def index():
    return read_html("./html/index.html")

@app.post('/segments/')
def get_segments(params:QueryModel):
    try:
        query = get_query(params.camera, params.people, params.objs, params.time_ranges, params.just_human, params.just_object, params.have_human, params.have_object)
        print(query)
        query = query.replace('\n', ' ').replace('\t',' ').replace('         ',' ')
        db_result = execute(query)
        cols = 'segment_id,video_id,location,url,time_start,time_end,cover'
        result = handle_result(cols, db_result)
        return result
    except Exception as e:
        return Response(str(e), 500)
    
@app.post("/frames")
def get_frames(segment_id:str, video_id:str, params:QueryModel):
    builder = ConditionBuilder('', params.people, params.objs, params.time_ranges, params.just_human, params.just_object, params.have_human, params.have_object)
    condition = builder.build(tbl_con='frame_id', tbl_alias='f', op='or')
    query = f'''
                select f.rowkey,
                f.video_id,
                f.segment_id,
                f.send_time,
                f.content
                from frames f where
                f.segment_id = '{segment_id}' and f.video_id = '{video_id}'
                { ' and '+ condition.strip('where') if condition!='' else '' } order by f.send_time
                '''.replace('\n', ' ').replace('\t',' ').replace('         ',' ')
    print(query)
    cols = 'rowkey,video_id,segment_id,send_time,content'
    db_result = execute(query)
    result = handle_result(cols,db_result)
    return result


@app.get("/video")
def get_video_stream(link:str='lol'):
    return "lol"
#     with requests.get(link, stream=True) as r:
#         r.raise_for_status()
#         for chunk in r.iter_content(2048):
#             yield chunk
#    return StreamingResponse(video_generate(), media_type='video/webm')

    
@app.get('/object-names')
def get_object_names():
    objects = ['bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench',
    'bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee',
    'skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup',
    'fork','nife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant',
    'bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book',
    'clock','vase','scissors','teddy bear','hair drier','toothbrush']
    return objects

@app.get('/colors')
def get_colors():
    data = mysqlHelper.excute("select * from colors")
    print(data)
    # colors = ['red', 'white', 'black', 'yellow', 'blue', 'green', 'brown', 'pink', 'gray', 'olive']
    return data  

@app.get('/cameras')
def get_cameras():
    cams = ['CNPM']
    return cams


