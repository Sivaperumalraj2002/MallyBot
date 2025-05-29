from kivy.app import App 
# from scrollView import ChatScreen
from kivy.lang import Builder
import chatScreen
import loginScreen
import registerScreen
import dashboardScreen

class BotApp(App):
    def build(self):
        return Builder.load_file("Bot.kv")

if __name__ == "__main__":
    BotApp().run()
