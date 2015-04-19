#!/usr/bin/env python


############################
#  Import various modules  #
############################

import time
from baseDefsPsychoPy import *
from stimPresPsychoPy import *
import generateTrialsv2


class Exp:
	def __init__(self):
	
		#this is where the subject variables go.  'any' means any value is allowed as long as it's the correct type (str, int, etc.) the numbers 1 and 2 control the order in which the prompts are displayed (dicts have no natural order)
		self.optionList = {	'1':  {	'name' : 'subjCode', 
									'prompt' : 'Subject Code: ', 
									'options': 'any', 
									'default':'rsvpTDCS_101',
									'type' : str}, 
							'2' : {	'name' : 'gender', 
									'prompt' : 'Subject Gender m/f: ', 
									'options' : ("m","f"),
									'default':'',
									'type' : str},
							'3' : {	'name' : 'responseDevice', 
									'prompt' : 'Response device: keyboard/gamepad: ', 
									'options' : ("keyboard","gamepad"),
									'default':'gamepad',
									'type' : str},
							'4' : {	'name' : 'electrode', 
									'prompt' : 'Electrode: c/a/na: ', 
									'options' : ('c','a','na'),
									'default':'na',
									'type' : str},
							'5' : {	'name' : 'sham', 
									'prompt' : 'Active stim? y/n/na: ', 
									'options' : ('y','n','na'),
									'default':'na',
									'type' : str},
							'6' : {	'name' : 'seed', 
									'prompt' : 'Enter seed: ', 
									'options' : 'any', 
									'default':100,
									'type' : int},
							'7' : {	'name' : 'expInitials', 
									'prompt' : 'Experiment Initials: ', 
									'options' : 'any', 
									'default' : '', 
									'type' : str}
								}

		optionsReceived=False
		fileOpened=False
		while not optionsReceived or not fileOpened:
			[optionsReceived,self.subjVariables] = enterSubjInfo('rsvp',self.optionList)
			if not optionsReceived:
				popupError(self.subjVariables)
			try:
				if  os.path.isfile(self.subjVariables['subjCode']+'_test.txt'):
					fileOpened=False
					popupError('Error: That subject code already exists')
				else:
					self.outputFileTest 	= file(self.subjVariables['subjCode']+'_test.txt','w')
					fileOpened=True
			except:
				pass
		generateTrialsv2.main(self.subjVariables['subjCode'],self.subjVariables['seed'])
			
		if self.subjVariables['responseDevice']=='gamepad':
			try:
				self.stick=initGamepad()
				pygame.init()
				self.inputDevice = "gamepad"
				responseInfo = " Press the GREEN key for 'Yes' and the RED' button for 'No'."
				self.validResponses = {'1':0,'0':3}
			except SystemExit:
				self.subjVariables['responseDevice']='keyboard'

		if self.subjVariables['responseDevice']=='keyboard':
			print "Using keyboard"
			self.inputDevice = "keyboard"
			self.validResponses = {'1':'up','0':'down'} #change n/o to whatever keys you want to use
			responseInfo = " Press the 'up arrow' for 'Yes' and the down arrow' for 'No'."
			
		try:
			#self.win = visual.Window([800,800], color=[.6,.6,.6], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')
			self.win = visual.Window(fullscr=True, color=[.3,.3,.3], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')
			#self.win = visual.Window([1920,1080],pos=[1440,0], color=[.6,.6,.6], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')
		except:
			self.win = visual.Window(fullscr=True, color=[.3,.3,.3], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')

		self.preFixationDelay  = 	0.500
		self.postFixationDelay  = 	0.500
		self.numPracticeTrials = 3
		self.takeBreakEveryXTrials = 100; 
		self.finalText              = "You've come to the end of the experiment.  Thank you for participating."
		self.instructions		= \
		"""Thank you for participating \nIn this experiment you will see a series of pictures. The first picture you will see (in a green frame) is the target you will be searching for. \n\n You will then see a stream of new images. Sometimes, in this stream, there will be a picture that *exactly* matches the target you saw in the green frame. 
		Other times, none of the pictures will match the target exactly. After you see each series of pictures, your task is to decide if you saw the picture in the green frame or not. If you saw the picture you should press the button for "yes". \n The first few will be practice. On these, if you make a mistake, you will hear a buzzing sound.  
		\n\nPlease let the experimenter know if you have any questions. 
		"""
	
		self.instructions+=responseInfo

		self.takeBreak = "Please take a short break.  Press 'Enter' when you are ready to continue"
		self.practiceTrials = "The next part is practice"
		self.realTrials = "Now for the real trials"
			
class trial(Exp):
	def __init__(self):
		firstStim=''
	
class ExpPresentation(trial):
	def __init__(self,experiment):
		self.experiment = experiment

	def initializeExperiment(self):	
		# Experiment Clocks
		self.expTimer = core.Clock()
		"""This loads all the stimili and initializes the trial sequence"""
		self.fixSpot = visual.TextStim(self.experiment.win,text="+",height = 30,color="black")
		self.rectOuter = newRect(self.experiment.win,size=(310,310),pos=(0,0),color='gray')
		self.rectInner = newRect(self.experiment.win,size=(305,305),pos=(0,0),color='white')

		self.targetRectOuter = newRect(self.experiment.win,size=(320,320),pos=(0,0),color='green')
		
		self.testPrompt = newText(self.experiment.win,"?",pos=[0,0],color="black",scale=1.6)
		
		showText(self.experiment.win, "Loading Images...",color="black",waitForKey=False)
		self.pictureMatrix = loadFiles('stimuli','jpg','image',self.experiment.win)
		if prefs.general['audioLib'] == ['pygame']:
			self.soundMatrix = loadFiles('stimuli',['wav'], 'winSound')
		else:
			self.soundMatrix = loadFiles('stimuli',['wav'], 'sound')
		(self.trialListMatrix,self.fieldNames) = importTrials('trialList_test_'+self.experiment.subjVariables["subjCode"]+'.csv',method="sequential")
		self.stim = visual.PatchStim(self.experiment.win,mask="none",tex="none")
	def checkExit(self): #I don't think this works if gamepad is in use
		if event.getKeys()==['equal','equal']:
			sys.exit("Exiting experiment")	

	def presentTestTrial(self,whichPart,curTrial,curTrialIndex):
		
		self.checkExit() #check for exit press the equals key twice.
		self.experiment.win.flip()
		setAndPresentStimulus(self.experiment.win,[self.fixSpot]) #show fixation cross
		core.wait(self.experiment.preFixationDelay) 
		setAndPresentStimulus(self.experiment.win,[self.rectOuter, self.rectInner, self.fixSpot]) #show blank frame w/ fixation
		core.wait(self.experiment.postFixationDelay)
		
		#the target
		setAndPresentStimulus(self.experiment.win,[self.targetRectOuter, self.rectInner, self.pictureMatrix[curTrial['targetPic']][0]]) #show target
		core.wait(1.0)

		setAndPresentStimulus(self.experiment.win,[self.rectOuter, self.rectInner]) #frame only
		core.wait(1.5)

		numFrames = 18 #about 8.3 ms / frame
		for curPic in range(6): #this should not be hardcoded
			for i in range(numFrames):
				setAndPresentStimulus(self.experiment.win,[self.rectOuter, self.rectInner, self.pictureMatrix[curTrial['picFile'+str(curPic+1)]][0]]) #show one of RSVP stream images
			
		setAndPresentStimulus(self.experiment.win,[self.rectOuter, self.rectInner, self.testPrompt]) #show prompt
		
		#correctResp = self.experiment.validResponses[str(curTrial['isMatch'])]
		correctResp = str(curTrial['isMatch'])
		if self.experiment.inputDevice=='keyboard':
			(response,rt) = getKeyboardResponse(self.experiment.validResponses.values())
		elif self.experiment.inputDevice=='gamepad':
			(response,rt) = getGamepadResponse(self.experiment.stick,self.experiment.validResponses.values())
		
		print response,rt 
		isRight = int(self.experiment.validResponses[correctResp]==response)
		
		if isRight:
			playAndWait(self.soundMatrix['bleep'])
		else:
			playAndWait(self.soundMatrix['buzz'])
	
		self.experiment.win.flip()
		fieldVars=[]
		
		for curField in self.fieldNames:
			fieldVars.append(curTrial[curField])
		[header, curLine] = createRespNew(self.experiment.optionList,self.experiment.subjVariables,self.fieldNames,fieldVars,
		a_whichPart = whichPart,
		b_curTrialIndex = curTrialIndex,
		c_expTimer = self.expTimer.getTime(),
		d_response = response,
		e_isRight = isRight,
		f_rt = rt*1000)
		writeToFile(self.experiment.outputFileTest,curLine)
		if curTrialIndex==0 and whichPart<>"practice":
			print 'writing header to file'
			dirtyHack = {}
			dirtyHack['trialNum']=1
			writeHeader(dirtyHack,header,'header_side_short') #fix the dirty hack later

	def cycleThroughExperimentTrials(self,whichPart):
		if whichPart == "practice":
			trialIndices = random.sample(range(1,50),self.experiment.numPracticeTrials)
			curTrialIndex=0
			for curPracticeTrial in trialIndices:
				self.presentTestTrial(whichPart,self.trialListMatrix.getFutureTrial(curPracticeTrial),curTrialIndex)
		else:
			curTrialIndex=0
			for curTrial in self.trialListMatrix:
				self.checkExit()
				if curTrialIndex>0 and curTrialIndex % self.experiment.takeBreakEveryXTrials == 0:
					showText(self.experiment.win,self.experiment.takeBreak,color=(0,0,0),inputDevice=self.experiment.inputDevice) #take a break
				self.presentTestTrial(whichPart,curTrial,curTrialIndex)
				curTrialIndex+=1
			#close test file
			self.experiment.outputFileTest.close()
			
currentExp = Exp()
currentPresentation = ExpPresentation(currentExp)
currentPresentation.initializeExperiment()
showText(currentExp.win,currentExp.instructions,color=(-1,-1,-1),inputDevice=currentExp.inputDevice) #show the instructions for test
showText(currentExp.win,currentExp.practiceTrials,color=(-1,-1,-1),inputDevice=currentExp.inputDevice)
currentPresentation.cycleThroughExperimentTrials("practice")
showText(currentExp.win,currentExp.realTrials,color=(0,0,0),inputDevice=currentExp.inputDevice)
currentPresentation.cycleThroughExperimentTrials("test")
showText(currentExp.win,currentExp.finalText,color=(-1,-1,-1),inputDevice=currentExp.inputDevice) #thank the subject
