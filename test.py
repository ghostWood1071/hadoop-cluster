from typing import *
class ConditionBuilder():
    def __init__(self, names:List[str], times:List[float]): 
        self.names = names
        self.times = times
    def build_names(self):
        name_str_lst = str(tuple(self.names))
        return f"name in {name_str_lst}"
    def build_times(self):
        q_time_min = self.times[0]
        q_time_max = self.times[1]
        if q_time_max < q_time_min:
            if q_time_max >0:
                raise Exception("wrong time range")
        if q_time_min == 0:
            return f"({q_time_max}>=s.time_end and s.time_start<{q_time_max})"
        if q_time_max == 0:
            return f"(s.time_start<={q_time_min})"
        return f"({q_time_max}>=s.time_end and s.time_start<{q_time_max})\nand ({q_time_min}<s.time_end and s.time_start<={q_time_min})"
    def get_condtion(self):
        if self.times[0] == 0 and self.times[1] == 0:
            if not self.names:
                return ""
            else:
                return f"where {self.build_names()}"
        else:
            if not self.names:
                return f"where {self.build_times()}"
            else:
                return f"where {self.build_names()} and {self.build_times()}"
        

def get_query(names, properties=None, operator=None, time_ranges=None):
    builder = ConditionBuilder(names, time_ranges)
    query = f'''
        Select s.url,
        s.video_id,
        s.time_start,
        s.time_end
        from
        segments as s
        join tracking t 
        on s.video_id  = t.video_id and s.segment_id = t.segment_id
        join videos as v
        on v.video_id = s.video_id
        {builder.get_condtion()} order by s.time_start;
    '''
    return query
