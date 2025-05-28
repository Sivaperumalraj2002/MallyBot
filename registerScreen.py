from kivy.uix.screenmanager import ScreenManager, Screen
from dbCon import regUser

class RegisterScreen(Screen):
    def do_register(self):
        username = self.ids.reg_username.text
        password = self.ids.reg_password.text
        isValide=regUser(username,password)
        if not isValide:
            self.ids.reg_msg.text = 'Username already exists!'
        else:
            self.ids.reg_msg.text = 'Registered successfully!'
        