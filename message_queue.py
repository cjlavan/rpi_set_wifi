import json
import os
import os.path

from unipath import Path


class message_queue:
	def __init__(self):
		self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		self.OUTPUT_DIR = Path(self.BASE_DIR).child('audio_output')
		
		self.MessageList = []
		self.NewMessageColorList = []
		self.colorIndex = 0
		self.load_stored_message_json()

		self.queued_filename = ""
		self.queued_color = ""		
		
		self.new_message_queue_position = -1
		self.queuePos = self.new_message_queue_position
		self.get_queue_info()

		self.replaying_last = False
		
	def queue_next(self):
		self.set_status_json_to_playing()
		self.queuePos += 1

		print "queue position: " + str(self.queuePos)
		print "out of " + str(len(self.MessageList)) + " messages"

		if self.queuePos > self.new_message_queue_position:
			self.new_message_queue_position = self.queuePos

		if self.queuePos > (len(self.MessageList) - 1) and self.replaying_last:
			self.queuePos = len(self.MessageList) - 1
			self.new_message_queue_position = self.queuePos
			self.queued_filename = "no new messages"
			self.queued_color = (255, 0, 0)	
			self.replaying_last = False
		elif self.queuePos <= (len(self.MessageList) - 1):			
			self.queued_filename = '%s.mp3' % self.MessageList[self.queuePos]['audio_file'][:-4]
			self.queued_color = self.MessageList[self.queuePos]['color']
			print self.MessageList[self.queuePos]['msg_id']
		else:	
			self.queuePos = len(self.MessageList) - 1
			self.queued_filename = '%s.mp3' % self.MessageList[self.queuePos]['audio_file'][:-4]
			self.queued_color = self.MessageList[self.queuePos]['color']
			replaying_last = True
			print self.MessageList[self.queuePos]['msg_id']
			self.replaying_last = True
			
		self.set_queue_info()
		
	def queue_previous(self):
		print "queue position: " + str(self.queuePos)
		print "out of " + str(len(self.MessageList)) + " messages"

		self.set_status_json_to_playing()
		
		if self.queuePos == -1:
			self.queued_filename = "start of queue"
		
		else:	
			self.queuePos -= 1
			self.queued_filename = '%s.mp3' % self.MessageList[self.queuePos]['audio_file'][:-4]
			self.queued_color = self.MessageList[self.queuePos]['color']
			
		self.set_queue_info()

	def queue_last(self):
		self.set_status_json_to_playing()
		
		if self.queuePos == -1:
			self.queued_filename = "start of queue"
		
		else:	
			self.queued_filename = '%s.mp3' % self.MessageList[self.queuePos]['audio_file'][:-4]
			self.queued_color = self.MessageList[self.queuePos]['color']
			
		self.set_queue_info()	
		
	def load_stored_message_json(self):
		os.chdir(self.OUTPUT_DIR)
		len_mes = 0
		try:
			jsonData = open('stored_message_data.json')	# Creates File Object JSONData
			stored_data = json.load(jsonData)		# Creates JSON Object NewData
			len_mes = len(stored_data)
			jsonData.close()
		except:
			with open('stored_message_data.json', 'w') as f:
				json.dump([], f)
				f.close()	

		self.MessageList = []

		for x in range (0,len_mes): 				# parse JSON
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
	
	def color_queue(self):
		self.colorIndex += 1
		if self.colorIndex < self.new_message_queue_position:
			self.colorIndex = self.new_message_queue_position
		elif self.colorIndex >= len(self.MessageList):
			self.colorIndex = self.new_message_queue_position
		
		return self.MessageList[self.colorIndex]['color']

#setters		
	def set_status_json_to_playing(self):
		os.chdir(self.OUTPUT_DIR)
		with open('player_status.json',"w") as f:			
			json.dump({'status':1}, f)
			f.close()	
		
	def set_status_json_to_stopped(self):
		os.chdir(self.OUTPUT_DIR)
		with open('player_status.json',"w") as f:			
			json.dump({'status':0}, f)
			f.close()	
			
	def check_alert_new_messages(self):
		os.chdir(self.OUTPUT_DIR)
		try:
			with open('new_message_status.json') as f:
				data = json.load(f)
				f.close()		
			return data['new_info']
		except:
			with open('new_message_status.json',"w") as f:		
				json.dump({'new_info':0}, f)	
				f.close()
			return 0		

	def silence_alert_new_messages(self):            
		os.chdir(self.OUTPUT_DIR)
		with open('new_message_status.json',"w") as f:			
			json.dump({'new_info':0}, f)
			f.close()   	 

	def set_queue_info(self):
		with open('queue_status.json',"w") as f:			
			json.dump({'queuePos':self.queuePos, 'new_message_queue_position':self.new_message_queue_position}, f)
			f.close()		
			
	def get_queue_info(self):
		try:
			with open('queue_status.json') as f:
				data = json.load(f)
				f.close()		

			self.new_message_queue_position = data['new_message_queue_position']
			self.queuePos = self.new_message_queue_position
		except:
			with open('queue_status.json',"w") as f:		
				json.dump({'queuePos': 0, 'new_message_queue_position': 0}, f)
				f.close()
			return 0