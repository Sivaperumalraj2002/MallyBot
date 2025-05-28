
import pymysql


def chatHistory(username):
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="miraj",
            database="mally"
        )
        print('DB Connection Established...')
    except Exception as e:
        print('Connection failed: ',e)
    else:
        cursor=db.cursor()
        cursor.execute('select session, event from history where username = %s',(username))
        data=cursor.fetchall()
    finally:
        if db.open:
            cursor.close()
            db.close()
            print('DB Connection Closed.')
    # print(type(data))
    # # for i in data:
    # #     print(i)   
    # print(data)
    return data
def getUser(user):
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="miraj",
            database="mally"
        )
        print('DB Connection Established...')
    except Exception as e:
        print('Connection failed: ',e)
    else:
        cursor=db.cursor()
        cursor.execute(f'select * from user where username=%s',(user,))
        data=cursor.fetchone()
    finally:
        if db.open:
            cursor.close()
            db.close()
            print('DB Connection Closed.')
    if data is None:
        return {None:None}
    return {data[0]:data[1]}

def regUser(username,password):
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="miraj",
            database="mally"
        )
        print('DB Connection Established....')
    except Exception as e:
        db.rollback()
        print('Connection failed: ',e)
    else:
        cursor=db.cursor()
        cursor.execute(f'select * from user where username=%s',(username,))
        data=cursor.fetchone()
        if data is None:
            cursor.execute('insert into user (username,password) values (%s,%s)',(username,password))
            db.commit()
            print('Registration Successfull.')
    finally:
        if db.open:
            cursor.close()
            db.close()
            print('DB Connection Closed.')
    if data is not None:
        return False
    return True

def chatHistoryLog(username,model,prompt,response,mood,session):
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="miraj",
            database="mally"
        )
        print('DB Connection Established....')
    except Exception as e:
        db.rollback()
        print('Connection failed: ',e)
    else:
        cursor=db.cursor()
        cursor.execute('insert into log (username,model,prompt,response,mood,session) values (%s,%s,%s,%s,%s,%s)',(username,model,prompt,response,mood,session))
        db.commit()
        print('Registration Successfull.')
    finally:
        if db.open:
            cursor.close()
            db.close()
            print('DB Connection Closed.') 

# cursor = db.cursor()
# cursor.execute("SELECT * FROM user")

# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# cursor.close()
# db.close()
