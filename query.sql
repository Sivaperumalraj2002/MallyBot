create view history as
with cte1 as (
select concat('[b]You:[/b] ',prompt,':\n\n') as prompt , 
concat('[b]MallyBot:[/b] ',response,':\n\n') as response,
session 
from log
), cte2 as (
select concat(prompt,response), session from cte1
)
select * from cte2;

create or replace view history as
select session,username, group_concat(event) as event
from (select concat('[b]You:[/b] ',prompt,':\n\n','[b]MallyBot:[/b] ',response,':\n\n') as event,
	  session, username
	from log) as chat
group by session,username;

select * from log;
use mally;

select * from history where username ='root';

create or replace view sentiment as
select date(timestamp) as date,avg(mood) as mood,username  
from log
group by date(timestamp),username
order by date;

select * from sentiment;