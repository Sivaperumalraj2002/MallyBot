from kivy.uix.screenmanager import ScreenManager, Screen
from dbCon import getUser


class LoginScreen(Screen):
    def do_login(self):
        username = self.ids.login_username.text
        password = self.ids.login_password.text
        users = getUser(username)
        if username in users and users[username] == password:
            self.manager.current = 'chat'
            with open('CurrentUser.txt','w') as f:
                f.write(username)

        else:
            self.ids.login_msg.text = 'Invalid username or password'