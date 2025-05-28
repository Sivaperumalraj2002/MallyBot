from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
# from kivy.properties import StringProperty, BooleanProperty
from textblob import TextBlob
from textGen import llmOut
from textGen import llmStream
from kivy.uix.screenmanager import ScreenManager, Screen
from dbCon import chatHistoryLog
import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
import uuid
from dbCon import chatHistory
from kivy.uix.button import Button


class ChatScreen(Screen):
    llmModel='gemma3:1b'
    chat_history = ""

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
    
    # to load the past history in chatscreen. it is used in open_chat_history()
    def on_history_button_press(self,item,popup):
        popup.dismiss()
        ChatScreen.session_ID=item[0]
        self.chat_history=item[1]
        self.ids.chat_log.text = self.chat_history
    
    # to initilize the new chat. it is called in open_chat_history()
    def on_new_chat(self,popup):
        popup.dismiss()
        ChatScreen.session_ID=self.sessionID()
        self.chat_history=''
        self.ids.chat_log.text = self.chat_history

    # this fuc called by clicking the chat history button
    def open_chat_history(self):
        content = BoxLayout(orientation='vertical', 
                            padding=dp(10),
                            spacing=dp(10))
        
        scroll = ScrollView(size_hint=(1, 1))

        history_container = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=dp(5), 
            padding=dp(5)
        )

        popup = Popup(
            title='Chat History',
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(500)),
            auto_dismiss=True
        )
        history_container.bind(minimum_height=history_container.setter('height'))
        message_button = Button(
                text='New Chat',
                size_hint_y=None,
                height=dp(50),  # Constant height
                size_hint_x=1,  # Fill width
                font_size='16sp',
                halign='left',
                valign='middle',
                text_size=(dp(300), None)  # You can tweak this
            )
        # Bind the button to a method (pass item as argument using lambda)
        message_button.bind(on_press=lambda instance, popup=popup: self.on_new_chat(popup))
        history_container.add_widget(message_button)

        for item in chatHistory('root'):
            message_button = Button(
                text=item[0],
                size_hint_y=None,
                height=dp(50),  # Constant height
                size_hint_x=1,  # Fill width
                font_size='16sp',
                halign='left',
                valign='middle',
                text_size=(dp(300), None)  # You can tweak this
            )
            # Bind the button to a method (pass item as argument using lambda)
            message_button.bind(on_press=lambda instance, item=item, popup=popup: self.on_history_button_press(item, popup))
            history_container.add_widget(message_button)

        scroll.add_widget(history_container)
        content.add_widget(scroll)
        popup.content = content
        popup.open()
        


    # to send the msg to chat with out stream msg. so for it not used
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
        chatHistoryLog(username,self.llmModel,user_text,resp,polarity,ChatScreen.session_ID)
    
    # to steam the msg in chat screen
    def chatStream(self):
        with open('CurrentUser.txt', 'r') as f:
            username = f.read()

        user_text = self.ids.user_input.text.strip()
        if not user_text:
            return

        self.chat_history += f"[b]You:[/b] {user_text}\n\n"
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
            chatHistoryLog(username, self.llmModel, user_text, response_part, polarity,ChatScreen.session_ID)
            update_chat_log('\n\n')

        def update_chat_log(text):
            self.chat_history += text
            self.ids.chat_log.text = self.chat_history

        # Start background thread
        threading.Thread(target=stream_response, daemon=True).start()
