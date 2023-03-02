Select * 
From segments as s
Where exists (
select *
from trackings as t
Where t.segment_id = s.row_key and s.video_id = t.video_id and t.name in ( 'person', 'refrigerator'));