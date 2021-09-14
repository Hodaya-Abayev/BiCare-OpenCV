import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.config import Config
from plyer import notification
Config.set('graphics', 'resizable', True)
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import threading,time
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.core.window import Window

Window.clearcolor = (26/255.0,26/255.0,26/255.0,1)

class popup():
    def build(self):
        self.content_cancel = Button(text='close', size_hint_y=None, size=(75,50))
        self.content = GridLayout()
        self.content.cols = 1
        #self.content_policy = Button(text='call policy', size_hint_y=None, height=40)

        self.content.add_widget(Label(text='Warning!!! probably someone stole your bike',color=(1,0,0)))
        # self.content.add_widget(VideoPlayer(source=r"C:\Users\מירי\Desktop\bicycle project\Sunrise.mp4",
        #                               state='play', options={'allow_stretch': True}))

        video = Video(source='mm.mp4', state = 'play',
                      options = {'eos': 'loop'}, allow_stretch = True, size_hint=(1,1) )
        self.content.add_widget(video)
        self.content.add_widget(Label(text='We suggest you go to the closest police station\n'
                                           'show them this video from the time of the theft'))
        #self.content_policy.bind(on_press=self.popupWindow.dismiss)
        #self.content.add_widget(self.content_policy)
        self.content.add_widget(self.content_cancel)

        self.popupWindow = Popup(title="", separator_height=0,
                      size_hint=(None, None), size=(400, 500),
                      content=self.content)
        #self.content_policy.bind(on_press=self.call_policy)
        self.content_cancel.bind(on_press=self.popupWindow.dismiss)
        self.popupWindow.open()



# creating the App class
class Pos_Size_App(App):

    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.add_widget(Image(source=r"logo.jpg"
                                     , width=800,size_hint_x= None))

        self.b1 = Button(size_hint=(.2, .2),color=(53/255.0,36/255.0,123/255.0),
                    pos_hint={'center_x': .7, 'center_y': .5},
                    text="I took the bike")


        self.b2 = Button(size_hint=(.2, .2), color=(53/255.0,36/255.0,123/255.0),
                    pos=(200, 200),
                    text="I don't know where the bike are")

        # adding button to widget
        self.b1.bind(on_press=self.call_back1)
        self.b2.bind(on_press=self.call_back2)
        self.window.add_widget(self.b1)
        self.window.add_widget(self.b2)

        return self.window

    def call_back1(self, instance):
        self.b1.text = "Enjoy your ride"
        self.b2.disabled=True



    def call_back2(self,instance):
        self.b1.disabled = True
        popup().build()


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)


def get_video():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 5 files the user has access to.
    """
    service = get_gdrive_service()
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=1, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)").execute()
    # get the results
    items = results.get('files', [])
    # list all 20 files & folders
    return items[0]["id"], items[0]["modifiedTime"], items[0]["name"]

flag = True
stop_threads = False
def call_notification():
    global flag
    global stop_threads
    while True:
        video_id, video_time, name = get_video()
        date_now = datetime.now().timestamp()
        datetime_video = datetime.strptime(video_time,'%Y-%m-%dT%H:%M:%S.%fZ')
        epoch_video=datetime(datetime_video.year,datetime_video.month,
                                      datetime_video.day,datetime_video.hour,datetime_video.minute).timestamp()
        if date_now-epoch_video<=300:
            flag=True
        if flag is True:
            notification.notify(
            title="Bicare",
            message="The bikes are not in place Do you know anything about it?"
            )
            flag=False
            stop_threads=True

        if stop_threads:
            break

if __name__ == "__main__":
    flag = True
    download_thread = threading.Thread(target=call_notification, name="Downloader")
    download_thread.start()
    Pos_Size_App().run()
    stop_threads = True