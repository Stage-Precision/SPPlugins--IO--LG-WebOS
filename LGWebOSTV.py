import sp
import os
import os.path
import sys
import json
import pickle
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"lib"))

import pywebostv.connection
from pywebostv.connection import WebOSClient
import pywebostv.controls
from pywebostv.controls import MediaControl
from pywebostv.controls import SystemControl
from pywebostv.controls import ApplicationControl
from pywebostv.controls import SourceControl
#import pywebostv.model 
#from pywebostv.model import *


class LGWebOSTV(sp.BaseModule):

	#plugin info used 
	pluginInfo = {
        "name" : "LG WebOS TV",
        "description" : "remote communication with LG WebOS TVs 2.0",
        "author" : "SP",
        "version" : (1, 0),
        "spVersion" : (1, 2, 0),
		"helpPath" : os.path.join(os.path.dirname(os.path.abspath(__file__)),"help.md")
    }

	def __init__(self):
		sp.BaseModule.__init__(self)
		self.WebOSClient  = None
		self.clientKey = {}
		self.media = None
		self.system = None
		self.app = None
		self.appList = None
		self.source = None
		self.sourceList = None
		self.audioList = None
		#self.tokenKey = None
		
	def checkConnection(self):
		print("checking connection....")
		if (len(self.clientKey) == 0):
			try:
				tokenKey = os.path.join(os.path.dirname(os.path.abspath(__file__)),"{}.pickle".format(self.hostip.value))
				if os.path.isfile(tokenKey):
					self.clientKey=pickle.load(open(tokenKey,"rb"))
					print("Read token key from file")
				else:
					self.clientKey = {}
			except EOFError:
				self.clientKey = {}
		try:
			self.WebOSClient = WebOSClient(self.hostip.value)
			try:
				self.WebOSClient.connect()
				for status in self.WebOSClient.register(self.clientKey):
					if status == self.WebOSClient.PROMPTED:
						print("Please accept the connection on the TV!")
					elif status == self.WebOSClient.REGISTERED:
						print("Registration successful!")
				tokenKey = os.path.join(os.path.dirname(os.path.abspath(__file__)),"{}.pickle".format(self.hostip.value))
				with open(tokenKey, 'wb') as file:
					pickle.dump(self.clientKey, file)
				self.media = MediaControl(self.WebOSClient)
				self.system = SystemControl(self.WebOSClient)
				self.app = ApplicationControl(self.WebOSClient)
				self.source = SourceControl(self.WebOSClient) 
				print("Connection successful")
				return True
			except TimeoutError:
				print("Connection Timeout. Please try again later.")
				return False
		except Exception as e:
			print(e)
			return False


	def afterInit(self):
		self.data = self.moduleContainer.addDataParameter("Data")
		self.hostip = self.moduleContainer.addIPParameter("TV IP", False)
		
		self.addAction("Screen on", "screenOn", self.screenOn)
		self.addAction("Screen off", "screenOff", self.screenOff)
		
		readAction = self.addAction("Update Device Infos", "readinfos", self.getDeviceStatus)

		self.addAction("Volume Up", "volumeUp", self.volumeUp)
		self.addAction("Volume Down", "volumeDown", self.volumeDown)
		muteAction = self.addAction("Mute", "volumeMute", self.volumeMute) #can change to have a bool parameter
		muteAction.addBoolParameter("Status", False)
		self.addAction("Play", "mediaPlay", self.mediaPlay)
		self.addAction("Pause", "mediaPause", self.mediaPause)
		self.addAction("Fast Forward", "mediaFastForward", self.mediaFastForward)
		self.addAction("Rewind", "mediaRewind", self.mediaRewind)
		volAction = self.addAction("Set Volume", "setVolume", self.setVolume)
		volAction.addFloatParameter("Volume", 50, 1, 100)

		appAction = self.addAction("Start App", "startApp", self.startApp)
		#appAction.addStringParameter("App Name", "")
		appAction.addDataTargetParameter("App Name", ".host/data","AppList")

		playContentAction = self.addAction("Select Source", "selectSource", self.selectSource)
		#playContentAction.addStringParameter("Source Name", "")
		playContentAction.addDataTargetParameter("Source Name", ".host/data","Sources")

		audioOutputAction = self.addAction("Select Audio Source", "SelectAudioSource", self.selectAudio)
		#audioOutputAction.addStringParameter("Audio Source Name", "")
		audioOutputAction.addDataTargetParameter("Audio Name", ".host/data","Audio")

		if self.hostip.value != "":
			self.getDeviceStatus()

		#self.addTimer("checker", 30, self.checkfunction)

	def onParameterFeedback(self, parameter):
		if parameter == self.hostip:
			if self.hostip.value != "": 
				self.getDeviceStatus()

	
	def screenOn(self):
		if self.checkConnection():
			try:
				self.system.screen_on()
			except:
				print("cannot turn screen on")
		
	def screenOff(self):
		if self.checkConnection():
			try:
				self.system.screen_off()
			except:
				print("cannot turn screen off")
	
	def setVolume(self, vol):
		if self.checkConnection():
			try:
				self.media.set_volume(int(vol))
			except:
				print("cannot set volume")
	
	def volumeUp(self):
		if self.checkConnection():
			try:
				self.media.volume_up()
			except:
				print("cannot volume up")
	def volumeDown(self):
		if self.checkConnection():
			try:
				self.media.volume_down()
			except:
				print("cannot volume down")
	def volumeMute(self, status):
		if self.checkConnection():
			try:
				self.media.mute(status)
			except:
				print("cannot mute volume")
	def mediaPlay(self):
		if self.checkConnection():
			try:
				self.media.play()
			except:
				print("cannot play media")
	def mediaPause(self):
		if self.checkConnection():
			try:
				self.media.pause()
			except:
				print("cannot pause media")
	def mediaFastForward(self):
		if self.checkConnection():
			try:
				self.media.fast_forward()
			except:
				print("cannot fast forward")
	def mediaRewind(self):
		if self.checkConnection():
			try:
				self.media.rewind()
			except:
				print("cannot rewind")

	def startApp(self, appName):
		if self.checkConnection():
			try:
				launchApp = [x for x in self.appList if appName in x["title"]][0]
				self.app.launch(launchApp)  
			except:
				print("cannot launch app")
	
	def selectSource(self, sourceName):
		print("Select Video Source: " + sourceName)
		if self.checkConnection():
			try:
				switchSource = [x for x in self.sourceList if sourceName in x["label"]][0]
				self.source.set_source(switchSource)  
			except:
				print("cannot select source")
			#for x in self.sourceList:
			#	if self.sourceList[x]["label"] == sourceName:
			#		try:
			#			self.source.set_source(self.sourceList[x])
			#		except:
			#			print("cannot select source")

	def selectAudio(self, audioName):
		if self.checkConnection():
			for x in self.audioList:
				if audioName in x.data:
					try:
						self.media.set_audio_output(x)
					except:
						print("cannot select audio source")
		
				
	def getDeviceStatus(self):
		if self.checkConnection():
			self.data.setTreeValueWithJson("System", str(json.dumps(self.system.info())))
			print(json.dumps(self.system.info()))
			self.appList = self.app.list_apps()
			jsonAppList = {}
			i = 0
			for x in self.appList:
				jsonAppList.update({"App " + str(i): str(x["title"])})
				i+=1
			print(json.dumps(jsonAppList))
			self.data.setTreeValueWithJson("AppList", str(json.dumps(jsonAppList)))
			self.sourceList = self.source.list_sources()
			jsonSourceList = {}
			i = 0
			for x in self.sourceList:
				jsonSourceList.update({"Source " + str(i): str(x["label"])})
				i+=1
			print(json.dumps(jsonSourceList))
			self.data.setTreeValueWithJson("Sources", str(json.dumps(jsonSourceList)))
			self.audioList = self.media.list_audio_output_sources()
			jsonAudioList = {}
			i = 0
			for x in self.audioList:
				jsonAudioList.update({"Audio " + str(i): str(x.data)})
				i+=1
			print (json.dumps(jsonAudioList))
			self.data.setTreeValueWithJson("Audio", str(json.dumps(jsonAudioList))) 

	def checkfunction(self):
		self.getDeviceStatus()


if __name__ == "__main__":
    sp.registerPlugin(LGWebOSTV)