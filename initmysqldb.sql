create table if not exists colors(
    color_id int primary key,
    color_name varchar(100) not null,
    color_rgb varchar(11) 
)