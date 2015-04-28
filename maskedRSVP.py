#!/usr/bin/env python
from difflib import SequenceMatcher
from unipath import Path

from baseDefsPsychoPy import *
from stimPresPsychoPy import *
import generateTrials

from util.dynamicmask import DynamicMask

class Exp:
    def __init__(self):

        #this is where the subject variables go.  'any' means any value is allowed as long as it's the correct type (str, int, etc.) the numbers 1 and 2 control the order in which the prompts are displayed (dicts have no natural order)
        self.optionList = {    '1':  {    'name' : 'subjCode',
                                    'prompt' : 'Subject Code: ',
                                    'options': 'any',
                                    'default':'rsvpTDCS_101',
                                    'type' : str},
                            '2' : {    'name' : 'gender',
                                    'prompt' : 'Subject Gender m/f: ',
                                    'options' : ("m","f"),
                                    'default':'',
                                    'type' : str},
                            '3' : {    'name' : 'responseDevice',
                                    'prompt' : 'Response device: keyboard/gamepad: ',
                                    'options' : ("keyboard","gamepad"),
                                    'default':'gamepad',
                                    'type' : str},
                            '4' : {    'name' : 'seed',
                                    'prompt' : 'Enter seed: ',
                                    'options' : 'any',
                                    'default':100,
                                    'type' : int},
                            '5' : {    'name' : 'expInitials',
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
                    self.outputFileTest = file('test_'+self.subjVariables['subjCode']+'.txt','w')
                    fileOpened=True
            except:
                pass
        generateTrials.main(self.subjVariables['subjCode'],self.subjVariables['seed'])

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

        self.win = visual.Window(fullscr=True, color=[.3,.3,.3], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')

        self.preFixationDelay  =     0.500
        self.postFixationDelay  =     0.500
        self.numPracticeTrials = 3
        self.takeBreakEveryXTrials = 100;
        self.finalText              = "You've come to the end of the experiment.  Thank you for participating."
        self.instructions        = \
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

        self.namePrompt = newText(self.experiment.win, "", pos=[200, 0],
                color = "black", scale = 1.6)
        self.testPrompt = newText(self.experiment.win, "?", pos=[0,0],
                color = "black", scale = 1.6)
        self.promptTextResponse = newText(self.experiment.win, "What was the name of the object you were looking for?", pos = [-300, 0],
                color = "black", scale = 1.6)

        showText(self.experiment.win, "Loading Images...",color="black",waitForKey=False)

        audioFeedbackDir = Path('stimuli', 'sounds')
        if prefs.general['audioLib'] == ['pygame']:
            self.soundMatrix = loadFiles(audioFeedbackDir, ['wav'], 'winSound')
        else:
            self.soundMatrix = loadFiles(audioFeedbackDir, ['wav'], 'sound')

        subjTrialsFile = 'trials_' + self.experiment.subjVariables['subjCode'] + '.csv'
        (self.trialListMatrix,self.fieldNames) = importTrials(subjTrialsFile, method="sequential")

        targets = loadFiles(Path('stimuli', 'images', 'targets'), 'jpg', 'image', self.experiment.win)
        distractors = loadFiles(Path('stimuli', 'images', 'distractors-1000'), 'jpg', 'image', self.experiment.win)
        print distractors.keys()

        # load targets and distractors in the same matrix
        self.pictureMatrix = targets
        self.pictureMatrix.update(distractors)

        self.stim = visual.PatchStim(self.experiment.win,mask="none",tex="none")

        # add dynamic mask
        mask_size = (320, 320)
        self.dynamic_mask = DynamicMask(win = self.experiment.win, size = mask_size)

    def checkExit(self): #I don't think this works if gamepad is in use
        if event.getKeys()==['equal','equal']:
            sys.exit("Exiting experiment")

    def presentVisualInterference(self, duration):
        MASK_REFRESH = 0.0083 * 4
        timer = core.Clock()
        startTime = timer.getTime()
        while timer.getTime() - startTime < duration:
            self.dynamic_mask.draw() # selects a new frame at random
            self.experiment.win.flip()
            core.wait(MASK_REFRESH)

    def collectWordResponse(self,stimToDraw,correctString):
        responded=False
        response=''
        respStr=''
        similarity='*'
        respText = newText(self.experiment.win," ",pos=[0,-270],color="black",scale=1)
        stimToDraw.draw()
        responseReminder = newText(self.experiment.win,"Please type the words/letters above. Don't worry about upper/lowercase",pos=[0,-150],color="gray",scale=.7)
        #newText is a function in stimPresPsychopy.. just creates a psychopy text obj
        responseReminder.setAutoDraw(True)
        self.experiment.win.flip()
        while not responded: #collect one letter response
            stimToDraw.draw()
            for key in event.getKeys():
                if key in ['enter','return']:
                    responded = True
                if key in ['backspace']:
                    if len(response) >0:
                        response = response[0:-1]
                elif key in 'abcdefghijklmnopqrstuvwxyz' or key == 'space':
                    responded = False
                    if key=='space':
                        response +=' '
                    else:
                        response += key
                else:
                    print key
                respText.setText(response)
                stimToDraw.draw()
                respText.draw()
                self.experiment.win.flip()
        print 'given:', correctString, ' responded: ',response, SequenceMatcher(None,correctString.lower(),response.lower()).ratio()
        responseReminder.setAutoDraw(False)
        return [response, SequenceMatcher(None,correctString.lower(),response.lower()).ratio()]

    def presentTestTrial(self, whichPart, curTrial, curTrialIndex):
        """
        Trial parts
        -----------
        1. Fixation
        2. Target name or blank
        3. Mask or blank
        4. Pre-sequence blank
        5. Sequence of pictures
        6. Post-sequence blank
        7. Target name or blank
        8. Mask or blank
        9. Y/N prompt
        10. 2AFC
        11. Remember target name
        """
        self.checkExit() #check for exit press the equals key twice.
        self.experiment.win.flip()

        self.namePrompt.setText(curTrial['targetName'])

        # 1. Fixation
        setAndPresentStimulus(self.experiment.win,[self.fixSpot, ])
        core.wait(self.experiment.preFixationDelay)

        # 2. Target name or blank
        textTimeWhenTargetBefore = 1.0
        if curTrial['whenTargetName'] == 'before':
            setAndPresentStimulus(self.experiment.win, [self.namePrompt, ])
        else:
            self.experiment.win.flip()
        core.wait(textTimeWhenTargetBefore)

        # 3. Mask or blank
        maskIntervalDuration = 0.200
        if curTrial['isMask'] == 1 and curTrial['whenMask'] == 'before':
            self.presentVisualInterference(maskIntervalDuration)
        else:
            self.experiment.win.flip()
            core.wait(maskIntervalDuration)

        # 4. Pre-sequence blank
        preImageBuffer = 0.200
        self.experiment.win.flip()
        core.wait(preImageBuffer)

        # 5. Sequence of pictures
        for curPicIndex in range(6):
            curPicName = curTrial['picFile'+str(curPicIndex+1)]
            curPic = self.pictureMatrix[curPicName][0]
            setAndPresentStimulus(self.experiment.win, [self.rectOuter, self.rectInner, curPic])
            core.wait(curTrial['picDurationSec'])

        # 6. Post-sequence blank
        postImageBuffer = preImageBuffer
        self.experiment.win.flip()
        core.wait(postImageBuffer)

        """
        On the "post cue" trials in Potter et al., the target name was
        presented along with the response prompt. Here we separate the
        target name from the response prompt so that participants know
        not to respond until the response prompt. That way, we can present
        the prompt very, very briefly, and then show the mask.
        """

        # 7. Target name or blank
        textTimeWhenTargetAfter = textTimeWhenTargetBefore
        if curTrial['whenTargetName'] == 'after':
            setAndPresentStimulus(self.experiment.win, [self.namePrompt, ])
        else:
            self.experiment.win.flip()
        core.wait(textTimeWhenTargetAfter)

        # 8. Mask or blank
        if curTrial['isMask'] == 1 and curTrial['whenMask'] == 'after':
            self.presentVisualInterference(maskIntervalDuration)
        else:
            self.experiment.win.flip()
            core.wait(maskIntervalDuration)

        # 9. Y/N prompt
        setAndPresentStimulus(self.experiment.win, [self.testPrompt, ])

        correctResp = str(curTrial['isTargetPresent'])
        if self.experiment.inputDevice=='keyboard':
            (yesNoResponse, yesNoRT) = getKeyboardResponse(self.experiment.validResponses.values())
        elif self.experiment.inputDevice=='gamepad':
            (yesNoResponse, yesNoRT) = getGamepadResponse(self.experiment.stick,self.experiment.validResponses.values())

        yesNoRT *= 1000.0
        print (yesNoResponse, yesNoRT)
        isTargetPresentCorrect = int(self.experiment.validResponses[correctResp]==yesNoResponse)

        if isTargetPresentCorrect:
            playAndWait(self.soundMatrix['bleep'])
        else:
            playAndWait(self.soundMatrix['buzz'])

        # 10. 2AFC
        # Only show the 2AFC if the participant responded "yes"
        if yesNoResponse == 'yes':
            targetPic = self.pictureMatrix[curTrial['targetFile'][0]]
            foilPic = self.pictureMatrix[curTrial['foilFile'][0]]

            targetLocationName = curTrial['whichTarget']
            foilLocationName = 'right' if targetLocationName == 'left' else 'left'

            targetPic.setPos(self.forcedChoiceLocations[targetLocationName])
            foilPic.setPos(self.forcedChoiceLocations[foilLocationName])

            setAndPresentStimulus(self.experiment.win, [targetPic, foilPic])

            correctLocationResp = curTrial['whichTarget']
            if self.experiment.inputDevice == 'keyboard':
                (locResponse, locRT) = getKeyboardResponse(self.experiment.validResponses.values())
            elif self.experiment.inputDevice == 'gamepad':
                (locResponse, locRT) = getGamepadResponse(self.experiment.stick, self.experiment.validResponses.values())

            locRT *= 1000.0
            print (locResponse, locRT)
            isTargetLocationCorrect = int(self.experiment.validResponses[correctLocationResp] == locResponse)
        else:
            locResponse = 'NA'
            locRT = 'NA'
            isTargetLocationCorrect = 'NA'

        # 11. Remember target name
        stimToDraw = self.promptTextResponse
        [textEntry, similarity] = self.collectWordResponse(stimToDraw, curTrial['targetName'])

        # ----------------------------------
        # Trial complete, write data to file
        self.experiment.win.flip()
        fieldVars=[]

        for curField in self.fieldNames:
            fieldVars.append(curTrial[curField])

        [header, curLine] = createRespNew(self.experiment.optionList,self.experiment.subjVariables,self.fieldNames,fieldVars,
            a_whichPart = whichPart,
            b_curTrialIndex = curTrialIndex,
            c_expTimer = self.expTimer.getTime(),
            d_yesNoResponse = yesNoResponse,
            e_isYesNoCorrect = isTargetPresentCorrect,
            f_yesNoRT = yesNoRT,
            g_targetFoilResponse = locResponse,
            h_targetFoilCorrect = isTargetLocationCorrect,
            i_targetFoilRT = locRT,
            j_rememberTarget = textEntry,
            k_rememberTargetSimilarity = similarity,
        )

        writeToFile(self.experiment.outputFileTest,curLine)
        if curTrialIndex == 0 and whichPart != "practice":
            print 'writing header to file'
            dirtyHack = {}
            dirtyHack['trialNum']=1
            writeHeader(dirtyHack, header, 'header_side_short') #fix the dirty hack later

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
