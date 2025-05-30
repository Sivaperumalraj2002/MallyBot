from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from textblob import TextBlob
from textGen import llmOut
from textGen import llmStream
from kivy.uix.screenmanager import ScreenManager, Screen
from dbCon import chatHistoryLog
import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.metrics import dp
import uuid
from dbCon import chatHistory
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex


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
    def on_press_logout(self):
        ChatScreen.new_session_id()
    
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
        # Main content layout
        content = BoxLayout(
            orientation='vertical', 
            padding=dp(10),
            spacing=dp(10),
            #background_color=get_color_from_hex("#f5f5f5")  # Light grey background
        )
        
        scroll = ScrollView(size_hint=(1, 1))

        # Container for history buttons
        history_container = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=dp(8), 
            padding=dp(8)
        )
        history_container.bind(minimum_height=history_container.setter('height'))

        # Create the popup first
        popup = Popup(
            title='Chat History',
            content=content,
            title_color=get_color_from_hex("#181B1E"),
            separator_color=get_color_from_hex("#acebe9"),
            size_hint=(None, None),
            size=(dp(360), dp(520)),
            auto_dismiss=True,
            background='',
            background_color=get_color_from_hex("#ececec")
            # background='atlas://data/images/defaulttheme/button_pressed',  # You can change this to a custom background
        )

        # 'New Chat' button
        new_chat_btn = Button(
            text='   +  Create New Chat',
            size_hint_y=None,
            height=dp(50),
            size_hint_x=1,
            font_size='16sp',
            halign='left',
            valign='middle',
            text_size=(dp(300), None),
            background_normal='',
            background_color=get_color_from_hex("#d0f0ef"),  # Blue
            color=get_color_from_hex('#181B1E'),  # White text
            bold=True
        )
        new_chat_btn.bind(on_press=lambda instance, popup=popup: self.on_new_chat(popup))
        history_container.add_widget(new_chat_btn)

        # Read current user
        with open('CurrentUser.txt', 'r') as f:
            username = f.read()

        # History buttons
        for item in chatHistory(username):
            history_btn = Button(
                text='  '+item[1][11:67].replace("\n\n[b]MallyBot:[/b]",' @Bot:'),
                size_hint_y=None,
                height=dp(50),
                size_hint_x=1,
                font_size='15sp',
                halign='left',
                valign='middle',
                text_size=(dp(300), None),
                background_normal='',
                background_color=get_color_from_hex("#adadad"),  # Light grey button
                color=get_color_from_hex('#181B1E'),  # Dark text
            )
            history_btn.bind(on_press=lambda instance, item=item, popup=popup: self.on_history_button_press(item, popup))
            history_container.add_widget(history_btn)

        # Add scroll to content
        scroll.add_widget(history_container)
        content.add_widget(scroll)

        # Open the styled popup
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
    
    # to clear chat while logout
    def clearChat(self):
        self.ids.chat_log.text=''
        self.chat_history=''
