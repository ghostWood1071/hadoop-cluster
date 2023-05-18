select s.rowkey as segment_id,
s.video_id,
v.location,
s.url,
s.time_start,
s.time_end
from segments as s
left join  frames as f
on s.cover = f.rowkey
left join cameras as v
on v.rowkey = s.video_id
left join things o on o.segment_id = s.rowkey
left join people p on p.segment_id = s.rowkey
where (p.rowkey is not null) and (o.name = 'car') order by s.time_start;

http://master:9870/webhdfs/v1/video_cam/c370a4d1-f4b9-4906-a66d-a7292b86ee3a/30bf7c0c-7661-425d-8320-7a4e5c13dae9.webm?op=OPEN

select f.rowkey,f.video_id,f.segment_id,f.send_time,f.content from  (select * from frames where frames.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9') f  join segments as s  on f.segment_id = s.segment_id join cameras as v on v.rowkey = f.video_id where (exists (select p.segment_id from people p where p.rowkey is not null and p.segment_id = s.rowkey)) and (exists (select o.segment_id from things o where o.name = 'truck' and o.segment_id = s.rowkey)) order by f.send_time

select f.rowkey, f.video_id, f.segment_id, f.send_time, f.content from frames f 
where  f.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9'  
and   v.location = 'CNPM' 
and (exists (select p.frame_id from people p   p.rowkey is not null and p.frame_id = f.rowkey)) 
and (exists (select o.frame_id from things o   o.name = 'truck' and o.frame_id = f.rowkey)) 
order by f.send_time


select f.rowkey,         
f.video_id,         
f.segment_id,         
f.send_time,         
f.content         
from frames f where         
f.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9'   
and (exists (select p.frame_id from people p where p.rowkey is not null and p.frame_id = f.rowkey)) or (exists (select o.frame_id from things o where o.name = 'truck' and o.frame_id = f.rowkey)) order by f.send_time;


select f.rowkey,         
f.video_id,         
f.segment_id,         
f.send_time             
from frames f where         
f.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9' and   
(exists (select o.frame_id from things o where o.name = 'truck' and o.frame_id = f.rowkey))



select f.rowkey,         
f.video_id,         
f.segment_id,         
f.send_time,         
f.content         
from frames f where         
f.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9' 
and f.video_id = 'c370a4d1-f4b9-4906-a66d-a7292b86ee3a'  and  v.location = 'CNPM' and (exists (select p.frame_id from people p where p.rowkey is not null and p.frame_id = f.rowkey)) or (exists (select o.frame_id from things o where o.name = 'truck' and o.frame_id = f.rowkey)) order by f.send_time 


select f.rowkey,         
f.video_id,         
f.segment_id,        
 f.send_time,         
 f.content         
 from frames f where         
 f.segment_id = '30bf7c0c-7661-425d-8320-7a4e5c13dae9'  
  and (exists (select p.frame_id from people p where p.rowkey is not null and p.frame_id = f.rowkey)) or (exists (select o.frame_id from things o where o.name = 'truck' and o.frame_id = f.rowkey)) order by f.send_time