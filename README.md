# MallyBot
create a database as mally and configure the db as in dbCon.py.
install other dependency which have used in project. those are obiously mentioned in project.
This project currently using the gemma3:1b LLM model.

# In MySQL

create DB
---------
create DB as mally
username: root
password: miraj

create table
------------
CREATE TABLE `log` (
  `SINO` int NOT NULL AUTO_INCREMENT,
  `TIMESTAMP` datetime DEFAULT CURRENT_TIMESTAMP,
  `USERNAME` char(20) NOT NULL,
  `MODEL` char(20) NOT NULL,
  `PROMPT` text NOT NULL,
  `RESPONSE` text NOT NULL,
  `MOOD` decimal(3,2) NOT NULL,
  `session` char(64) NOT NULL,
  PRIMARY KEY (`SINO`)
);

CREATE TABLE `user` (
  `username` char(20) NOT NULL,
  `password` char(20) NOT NULL,
  PRIMARY KEY (`username`)
);

create views as
---------------
create or replace view history as
select session,username, group_concat(event) as event
from (select concat('[b]You:[/b] ',prompt,':\n\n','[b]MallyBot:[/b] ',response,':\n\n') as event,
	  session, username
	from log) as chat
group by session,username;

create or replace view sentiment as
select date(timestamp) as date,avg(mood) as mood,username  
from log
group by date(timestamp),username
order by date;

you have to create these two views on mally database

# ollama
install the ollama and download gemma3:1b llm model.
you can change the model by,
download it first and then,
change the model name in chatScreen.py's class ChatScreen's attribute llmModel='<model-name>'