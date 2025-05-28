from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, BooleanProperty
from textblob import TextBlob
from textGen import llmOut
from textGen import llmStream
from kivy.uix.screenmanager import ScreenManager, Screen
from dbCon import chatHistoryLog
import threading
from kivy.clock import Clock


class ChatScreen(Screen):
    llmModel='gemma3:1b'
    chat_history = ""
    # def send_message(self):
    #     user_text = self.ids.user_input.text.strip()
    #     if user_text == "":
    #         return

    #     self.chat_history += f"[b]You:[/b] {user_text}\n"
    #     self.ids.user_input.text = ""

    #     # Chatbot response (sentiment check)
    #     blob = TextBlob(user_text)
    #     polarity = blob.sentiment.polarity

    #     if polarity > 0.3:
    #         reply = "I'm glad you're feeling good today! 😊"
    #     elif polarity < -0.3:
    #         reply = "I'm here for you. Want to talk more about it?"
    #     else:
    #         reply = "Thanks for sharing. How else are you feeling?"

    #     self.chat_history += f"[b]Bot:[/b] {reply}\n"
    #     self.ids.chat_log.text = self.chat_history

    def send_message(self):
        with open('CurrentUser.txt','r') as f:
            username=f.read()
        user_text=self.ids.user_input.text.strip()
        if not user_text:
            return
        self.chat_history += f"[b]You:[/b] {user_text}\n"
        self.ids.user_input.text = ""
        resp=llmOut(self.llmModel,user_text)
        self.chat_history+=f'[b]MallyBot:[/b] {resp}\n'
        self.ids.chat_log.text = self.chat_history
        #(sentiment check)
        blob = TextBlob(user_text)
        polarity = blob.sentiment.polarity
        print(polarity)
        chatHistoryLog(username,self.llmModel,user_text,resp,polarity)

    # def chatStream(self):
    #     with open('CurrentUser.txt','r') as f:
    #         username=f.read()
    #     user_text=self.ids.user_input.text.strip()
    #     if not user_text:
    #         return
    #     self.chat_history += f"[b]You:[/b] {user_text}\n"
    #     self.ids.user_input.text = ""
    #     self.chat_history+=f'[b]MallyBot:[/b] '
    #     self.ids.chat_log.text = self.chat_history
    #     resp=len(self.chat_history)
    #     for chunk in llmStream(self.llmModel,user_text):
    #         self.chat_history+= chunk['message']['content']
    #         self.ids.chat_log.text = self.chat_history
    #     #(sentiment check)
    #     blob = TextBlob(user_text)
    #     polarity = blob.sentiment.polarity
    #     print(polarity)
    #     chatHistoryLog(username,self.llmModel,user_text,self.chat_history[resp:],polarity)
    
    def chatStream(self):
        with open('CurrentUser.txt', 'r') as f:
            username = f.read()

        user_text = self.ids.user_input.text.strip()
        if not user_text:
            return

        self.chat_history += f"[b]You:[/b] {user_text}\n"
        self.chat_history += f"[b]MallyBot:[/b] "
        self.ids.user_input.text = ""
        self.ids.chat_log.text = self.chat_history
        start_idx = len(self.chat_history)

        def stream_response():
            for chunk in llmStream(self.llmModel, user_text):
                text = chunk['message']['content']
                Clock.schedule_once(lambda dt: update_chat_log(text))

            # After the loop, do sentiment and logging
            blob = TextBlob(user_text)
            polarity = blob.sentiment.polarity
            response_part = self.chat_history[start_idx:]
            chatHistoryLog(username, self.llmModel, user_text, response_part, polarity)
            update_chat_log('\n')

        def update_chat_log(text):
            self.chat_history += text
            self.ids.chat_log.text = self.chat_history

        # Start background thread
        threading.Thread(target=stream_response, daemon=True).start()
