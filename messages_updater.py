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


class messages_updater:

	def __init__(self):
		self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		self.OUTPUT_DIR = Path(self.BASE_DIR).child('audio_output')
		os.chdir(self.OUTPUT_DIR)
		convert.remove_files(self.OUTPUT_DIR)
		self.OldMessageList = []
		self.load_played_message_json()
		self.NewMessageList = []
		self.load_unplayed_message_json()
		self.DownloadMessageList = []
		self.post_download_message_json()
		self.download_audio()

	def update_loop(self):
		while True:
			convert.remove_files(self.OUTPUT_DIR)
			if self.is_played_message_data_changed():
				self.load_played_message_json()
				self.load_unplayed_message_json()
				self.update_played_message_data()
			
			self.post_download_message_json()
			self.download_audio()
			convert.remove_files(self.OUTPUT_DIR)
			time.sleep(10)
	
	# loads the initial json file to compare to what will be downloaded
	# reads the initial json file and converts it to a list of message objects
	def load_played_message_json(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			jsonData = open('played_message_data.json')	# Creates File Object JSONData
			stored_data = json.load(jsonData)		# Creates JSON Object NewData
			jsonData.close()
			self.OldMessageList = []
			i = len(stored_data)
			for x in range (0,i): 				# parse JSON
				m = {
					'msg_id' : stored_data[x]["msg_id"],
					'audio_file' : stored_data[x]["audio_file"], 
					'path' : self.OUTPUT_DIR,
					'color' : stored_data[x]["color"], 
					'audio_downloaded' : 0,
					'ts' : stored_data[x]["ts"], 
					'played' : 0,
					'just updated' : 0,
				}
				self.OldMessageList.append(m)
			self.update_played_message_json()
		except:
			with open('played_message_data.json', 'w') as f:
				json.dump([], f)
				f.close()
		
	# loads unplayed message json into the UnplayedMessageList	
	def load_unplayed_message_json(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			jsonData = open("unplayed_message_data.json")			# Creates File Object JSONData
			stored_data = json.load(jsonData)				# Creates JSON Object NewData
			jsonData.close()
			i = len(stored_data)
			for x in range (0,i): 				
				m = {
					'msg_id' : stored_data[x]["msg_id"],
					'audio_file' : stored_data[x]["audio_file"], 
					'path' : self.OUTPUT_DIR,
					'color' : stored_data[x]["color"], 
					'audio_downloaded' : 0,
					'ts' : stored_data[x]["ts"], 
					'played' : 0,
					'just updated' : 0,
				}
				self.NewMessageList.append(m)
		except:
			with open('unplayed_message_data.json', 'w') as f:
				json.dump([], f)
				f.close()			
		
	# posts to server reads incoming json into download message list	
	def post_download_message_json(self):
		r = requests.post(_SETTINGS.url, data=json.dumps(_SETTINGS.payload))
		# writing some random shit to files
		jsonData = open("json_data.json","w")			
		jsonData.write(r.text)					
		jsonData.close()					
		jsonData = open('json_data.json')			
		Downloaded_messages_json = json.load(jsonData)		
		jsonData.close()					
		settings = json.dumps(Downloaded_messages_json["settings"])
		
		i = len(Downloaded_messages_json["data"])
		with open("config.json","w") as myfile:
			myfile.write(settings)
			myfile.close()
		
		old_position_queue = 0
		new_position_queue = 0
		
		for x in range (0,i):
			is_new = True
			for y in range (old_position_queue,len(self.OldMessageList)):
				if self.OldMessageList[y]["msg_id"] == Downloaded_messages_json["data"][x]["msg_id"]:
					is_new = False
					old_position_queue += 1
					break
			for y in range (new_position_queue,len(self.NewMessageList)):
				if self.NewMessageList[y]["msg_id"] == Downloaded_messages_json["data"][x]["msg_id"]:
					is_new = False
					new_position_queue += 1
					break
				
			if is_new:
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
					'audio_downloaded' : 0,
					'ts' : Downloaded_messages_json["data"][x]["ts"], 
					'played' : 0,
					'just updated' : 0,
				}
				self.DownloadMessageList.append(m)

	# downloads audio for DownloadMessageList
	def download_audio(self):						
		os.chdir(self.OUTPUT_DIR)
		i = len(self.DownloadMessageList)
		for x in range (0,i):
			message = self.DownloadMessageList[0]
			while not self.is_okay_to_play():
				time.sleep(10)				
			local_file_name = wget.download(message['download_link'])
			message['audio_file'] = local_file_name
			self.save_new_message(message)
			self.DownloadMessageList.remove(message)
		
	# checks to see if messages are being played
	# if no, then saves messages that has just been downloaded
	def save_new_message(self, message):
		while not self.is_okay_to_play():
			time.sleep(10)	
		convert.convert(self.OUTPUT_DIR)	
		self.NewMessageList.append(message)
		self.write_unplayed_message_data()

	def write_unplayed_message_data(self):
		os.chdir(self.OUTPUT_DIR)
		with open("unplayed_message_data.json","w") as output_file:				
			output_string = json.dumps(self.NewMessageList)
			output_file.write(output_string)
			output_file.close()
		self.update_unplayed_message_data()
	
			
# helper methods
	# returns iso format time stamp
	def get_iso_format(self, obj):
		if hasattr(obj, 'isoformat'):
			return obj.isoformat()
		else:
			raise TypeError, 'Object of type %s with value of %s is not JSON serializable' \
			% (type(obj), repr(obj))
		
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
	
	def is_okay_to_play(self):
		os.chdir(self.OUTPUT_DIR)
		if self.get_status_json() == 0:
			return True
		return False
		
		
	def is_played_message_data_changed(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			with open('message_status.json') as f:
				data = json.load(f)
				f.close()
		except:
			return False
			
		if data['played_message_data'] == "changed":
			return True
		return False			
	
	def update_played_message_data(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			with open('message_status.json') as f:
				data = json.load(f)
				f.close()		
			new_info = data['new_info']
		except:
			new_info = 0
			
		with open('message_status.json',"w") as f:					
			json.dump({'played_message_data':'old','unplayed_message_data':new_info}, f)		
			f.close()		
	
	def update_unplayed_message_data(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			with open('message_status.json') as f:
				data = json.load(f)
				f.close()		
				played_message_data = data['played_message_data']
		except:
			played_message_data = 0
			
		with open('message_status.json',"w") as f:			
			json.dump({'played_message_data':played_message_data,'new_info':len(self.NewMessageList)}, f)
			f.close()
			
