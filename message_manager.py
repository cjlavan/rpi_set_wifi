import requests
import os
import os.path
import json

from unipath import Path
import datetime
import time
import wget

import _SETTINGS
import convert
from message_queue import message_queue


class message_manager:
    
    def __init__(self):
        self.new_messages = False
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.OUTPUT_DIR = Path(self.BASE_DIR).child('audio_output')
        os.chdir(self.OUTPUT_DIR)
        convert.remove_files(self.OUTPUT_DIR)
        
        self.latest_id = int(self.get_latest_msg_id_json())
        self.new_messages = False

        self.MessageList = []
        self.load_stored_message_json()
        
        self.DownloadMessageList = []
        self.post_download_message_json()
        if self.new_messages:
            self.alert_new_messages()
            self.download_audio()
            self.new_messages = False

    def update_loop(self):
        while True:
            convert.remove_files(self.OUTPUT_DIR)
            self.post_download_message_json()
            
            if self.new_messages:
                self.alert_new_messages()
                self.download_audio()
                self.new_messages = False
                
            convert.remove_files(self.OUTPUT_DIR)
            time.sleep(10)

    # loads the initial json file to compare to what will be downloaded
    # reads the initial json file and converts it to a list of message objects
    def load_stored_message_json(self):
        os.chdir(self.OUTPUT_DIR)
        len_mes = 0
        try:
            jsonData = open('stored_message_data.json')	
            stored_data = json.load(jsonData)		
            len_mes = len(stored_data)        
            jsonData.close()
        except:
            with open('stored_message_data.json', 'w') as f:
                json.dump([], f)
                f.close() 

        self.MessageList = []
        print "length of len_mes: " + str(len_mes)
        for x in range (0,len_mes):		
            m = {
                'msg_id' : stored_data[x]["msg_id"],
                'audio_file' : stored_data[x]["audio_file"], 
                'path' : self.OUTPUT_DIR,
                'color' : stored_data[x]["color"], 
                'ts' : stored_data[x]["ts"], 
                'played' : stored_data[x]["played"]
            }
            self.MessageList.append(m)
            # print "appened message list with " + str(m['msg_id'])
       

    # posts to server reads incoming json into download message list	
    def post_download_message_json(self):
        Downloaded_messages_json = (requests.post(_SETTINGS.url, data=json.dumps(_SETTINGS.payload))).text
        Downloaded_messages_json = json.loads(Downloaded_messages_json)
        settings = json.dumps(Downloaded_messages_json["settings"])

        i = len(Downloaded_messages_json["data"])
        with open("config.json","w") as myfile:
            myfile.write(settings)
            myfile.close()

        lookup_marker = 0    

        for x in range (i-1, 0, -1):
            if int(Downloaded_messages_json["data"][x]["msg_id"]) > self.latest_id:
            
                Downloaded_messages_json["data"][x].update({
                    'ts': str(json.dumps(datetime.datetime.now(), 
                                         default=self.get_iso_format))
                })				
                m = {
                    'msg_id' : Downloaded_messages_json["data"][x]["msg_id"],
                    'audio_file' : "",
                    'download_link' : Downloaded_messages_json["data"][x]["audio_file"], 
                    'path' : self.OUTPUT_DIR,
                    'color' : Downloaded_messages_json["data"][x]["color"], 
                    'ts' : Downloaded_messages_json["data"][x]["ts"], 
                    'played' : 0,
                }
                self.new_messages = True
                self.DownloadMessageList.append(m)                

    # downloads audio for DownloadMessageList
    def download_audio(self):						
        os.chdir(self.OUTPUT_DIR)
        i = len(self.DownloadMessageList)
        for x in range (0,i):
            message = self.DownloadMessageList[0]
            while not self.is_okay_to_work():
                time.sleep(10)				
            local_file_name = wget.download(message['download_link'])
            message['audio_file'] = local_file_name
            self.save_new_message(message)
            self.DownloadMessageList.remove(message)

    # checks to see if messages are being played
    # if no, then saves messages that has just been downloaded
    def save_new_message(self, message):
        while not self.is_okay_to_work():
            time.sleep(10)	
        convert.convert(self.OUTPUT_DIR)
        self.MessageList.append(message)
        if int(message['msg_id']) > self.latest_id:
            self.latest_id = int(message['msg_id'])
        self.write_message_data()


    def write_message_data(self):
        os.chdir(self.OUTPUT_DIR)
        while not self.is_okay_to_work:
            time.sleep(10)
        with open("stored_message_data.json","w") as output_file:				
            output_string = json.dumps(self.MessageList)
            output_file.write(output_string)
            output_file.close()
        self.set_latest_msg_id_json()


# helper methods
    # returns iso format time stamp
    def get_iso_format(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError, 'Object of type %s with value of %s is not JSON serializable' \
                  % (type(obj), repr(obj))

    def alert_new_messages(self):            
        os.chdir(self.OUTPUT_DIR)
        with open('new_message_status.json',"w") as f:			
            json.dump({'new_info':1}, f)
            f.close()            

    def get_status_json(self):
        os.chdir(self.OUTPUT_DIR)
        try:
            with open('player_status.json') as f:
                data = json.load(f)
                f.close()		
            return data['status']
        except:
            with open('player_status.json',"w") as f:		
                json.dump({'status':0}, f)	
                f.close()
            return 0

    def get_latest_msg_id_json(self):
        os.chdir(self.OUTPUT_DIR)
        try:
            with open('latest_id_status.json') as f:
                data = json.load(f)
                f.close()       
            return data['latest_msg_id']
        except:
            with open('latest_id_status.json',"w") as f:       
                json.dump({'latest_msg_id':0}, f) 
                f.close()
            return 0

    def set_latest_msg_id_json(self):
        with open('latest_id_status.json',"w") as f:            
            json.dump({'latest_msg_id':self.latest_id}, f)
            f.close()

    def is_okay_to_work(self):
        os.chdir(self.OUTPUT_DIR)
        if self.get_status_json() == 0:
            return True
        return False
