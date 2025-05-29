from kivy.uix.screenmanager import ScreenManager, Screen
import uuid
from dbCon import getSentimentalReport


class DashboardScreen(Screen):

    # to create session id using uuid lybrary. it is called in chatHistoryLog()
    @staticmethod
    def sessionID():
        # Version 4 (random)
        unique_id = uuid.uuid4()
        print('session ID: ',unique_id)  # e.g., 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        with open('sessionID.txt','w') as f:
            f.write(str(unique_id))
        return str(unique_id)
    session_ID=sessionID()

    # to create new session id while clicking the new chat
    @classmethod
    def new_session_id(cls):
        cls.session_ID=cls.sessionID()
    
    # to log the report default
    def sentimentalReport(self):
        text=''
        with open('CurrentUser.txt')as f:
            user=f.read()
        data = getSentimentalReport(user)
        if data is None:
            return ''
        for item in data:
            text+=item[0]+'  -  '+item[1]+'\n'
        return text
    
    # to log the report if relogin
    def update_report(self):
        res=self.sentimentalReport()
        self.ids.report_log.text= 'None' if res is None else res 
        
    
    

    
    