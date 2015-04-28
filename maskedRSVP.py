#!/usr/bin/env python
from difflib import SequenceMatcher
from unipath import Path
import random

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
                                    'default':'MRS101',
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
                self.responseInfo = " Press the GREEN key for 'Yes' and the RED' button for 'No'."
                self.validResponses = {'1':0,'0':3}
                assert False, 'Left right responses not implemented for gamepad. Try keyboard'
                self.leftRightResponses = dict()
                self.leftRightResponseInfo = ""
            except SystemExit:
                self.subjVariables['responseDevice']='keyboard'

        if self.subjVariables['responseDevice']=='keyboard':
            print "Using keyboard"
            self.inputDevice = "keyboard"
            self.validResponses = {'1':'up','0':'down'} #change n/o to whatever keys you want to use
            self.leftRightResponses = {'left': 'left', 'right': 'right'}
            self.responseInfo = "Press the up arrow for 'Yes' and the down arrow for 'No'."
            self.leftRightResponseInfo = "Press the left arrow for the left image and the right arrow for the right image."

        self.win = visual.Window(fullscr=True, color=[.3,.3,.3], allowGUI=False, monitor='testMonitor',units='pix',winType='pyglet')

        self.takeBreakEveryXTrials = 32  # number of trials in a block
        self.finalText = "You've come to the end of the experiment. Thank you for participating."
        self.instructions = \
            ("Welcome to the MRS study!\n\n"
             "In this experiment you will see a sequence of pictures. "
             "Your goal is to remember as many of the pictures as you can "
             "because we will ask you questions about what you saw.\n\n"
             "For example, we might ask you if you saw a picture of a dog. "
             "Sometimes you will know what to look for before you see the "
             "pictures, but other times we won't ask you about what you saw "
             "until after the images are gone.\n\n"
             "After you answer if you saw the target image or not, some of "
             "the time we will ask you to pick which image you saw, and "
             "other times we will ask you to type in the name of the picture "
             "you were looking for even if you didn't see it.\n\n"
             "Please let the experimenter know when you have completed "
             "reading these instructions\n\n")

        self.instructions += self.responseInfo

        self.takeBreak = "Please take a short break. Press 'Enter' when you are ready to continue"
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

        #self.rectOuter = newRect(self.experiment.win,size=(310,310),pos=(0,0),color='gray')
        #self.rectInner = newRect(self.experiment.win,size=(305,305),pos=(0,0),color='white')
        #self.targetRectOuter = newRect(self.experiment.win,size=(320,320),pos=(0,0),color='green')

        self.namePrompt = newText(self.experiment.win, "", pos=[0,0],
                color = "black", scale = 1.6)
        self.testPrompt = newText(self.experiment.win, "Yes or No?\n"+self.experiment.responseInfo, pos=[0,200],
                color = "black", scale = 1.6)
        self.promptTextResponse = newText(self.experiment.win, "What was the object you were looking for?", pos = [0,200],
                color = "black", scale = 1.0)
        self.promptLeftRightResponse = newText(self.experiment.win, "Left or Right?\n"+self.experiment.leftRightResponseInfo, color = 'black', scale = 1.0, pos = [0, 200])

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

        # load targets and distractors in the same matrix
        self.pictureMatrix = targets
        self.pictureMatrix.update(distractors)

        self.stim = visual.PatchStim(self.experiment.win,mask="none",tex="none")

        # add dynamic mask
        mask_size = (320, 320)
        self.dynamic_mask = DynamicMask(win = self.experiment.win, size = mask_size)

        # locations for 2AFC images
        gutter = 200
        self.forcedChoiceLocations = {'left': [-gutter, 0], 'right': [gutter, 0]}

    def checkExit(self): #I don't think this works if gamepad is in use
        if event.getKeys()==['equal','equal']:
            sys.exit("Exiting experiment")

    def presentVisualInterference(self, duration):
        MASK_REFRESH = 0.0083
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
        respText = newText(self.experiment.win," ",pos=[0,0],color="black",scale=1)
        stimToDraw.draw()
        responseReminder = newText(self.experiment.win,"Please type your answer to the question above. Don't worry about upper/lowercase",pos=[0,100],color="gray",scale=.7)

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
        10A. 2AFC
        10B. Remember target name
        """
        self.checkExit() #check for exit press the equals key twice.
        self.experiment.win.flip()

        self.namePrompt.setText(curTrial['targetName'])

        # 1. Fixation
        timeForFixation = 0.500
        setAndPresentStimulus(self.experiment.win,[self.fixSpot, ])
        core.wait(timeForFixation)

        # 2. Target name or blank
        textTimeWhenTargetBefore = 0.700
        maskIntervalDuration = 0.500
        if curTrial['whenTargetName'] == 'before':
            setAndPresentStimulus(self.experiment.win, [self.namePrompt, ])
            core.wait(textTimeWhenTargetBefore)

            if curTrial['isMask'] == 1:
                self.presentVisualInterference(maskIntervalDuration)
            else:
                self.experiment.win.flip()
                core.wait(maskIntervalDuration)
        else:
            self.experiment.win.flip()

        # 4. Pre-sequence blank
        preImageBuffer = 0.200
        self.experiment.win.flip()
        core.wait(preImageBuffer)

        # 5. Sequence of pictures
        for curPicIndex in range(6):
            curPicName = curTrial['picFile'+str(curPicIndex+1)]
            curPic = self.pictureMatrix[curPicName][0]
            setAndPresentStimulus(self.experiment.win, [curPic, ])
            core.wait(curTrial['picDurationSec'])

        # 6. Post-sequence blank
        postImageBuffer = preImageBuffer
        self.experiment.win.flip()
        core.wait(postImageBuffer)

        # 7. Target name or blank
        textTimeWhenTargetAfter = textTimeWhenTargetBefore
        if curTrial['whenTargetName'] == 'after':
            setAndPresentStimulus(self.experiment.win, [self.namePrompt, ])
            core.wait(textTimeWhenTargetAfter)

            if curTrial['isMask'] == 1:
                self.presentVisualInterference(maskIntervalDuration)
            else:
                self.experiment.win.flip()
                core.wait(maskIntervalDuration)
        else:
            self.experiment.win.flip()

        # 9. Y/N prompt
        setAndPresentStimulus(self.experiment.win, [self.testPrompt, ])

        correctResp = str(curTrial['isTargetPresent'])
        if self.experiment.inputDevice=='keyboard':
            (yesNoResponse, yesNoRT) = getKeyboardResponse(self.experiment.validResponses.values())
        elif self.experiment.inputDevice=='gamepad':
            (yesNoResponse, yesNoRT) = getgamepadResponse(self.experiment.stick,self.experiment.validResponses.values())

        yesNoRT *= 1000.0
        print (yesNoResponse, yesNoRT)
        isTargetPresentCorrect = int(self.experiment.validResponses[correctResp]==yesNoResponse)

        if isTargetPresentCorrect:
            playAndWait(self.soundMatrix['bleep'])
        else:
            playAndWait(self.soundMatrix['buzz'])

        # 10. 2AFC
        # Only show the 2AFC if the participant responded "yes"
        locResponse = None

        participantRespondedYes = (yesNoResponse == self.experiment.validResponses['1'])
        if participantRespondedYes:
            showPictures = random.choice([True, False])
            if showPictures:
                targetPic = self.pictureMatrix[curTrial['targetFile']][0]
                foilPic = self.pictureMatrix[curTrial['foilFile']][0]

                targetLocationName = curTrial['whichTarget']
                foilLocationName = 'right' if targetLocationName == 'left' else 'left'

                targetPic.setPos(self.forcedChoiceLocations[targetLocationName])
                foilPic.setPos(self.forcedChoiceLocations[foilLocationName])

                setAndPresentStimulus(self.experiment.win, [self.promptLeftRightResponse, targetPic, foilPic])

                correctLocationResp = curTrial['whichTarget']
                if self.experiment.inputDevice == 'keyboard':
                    (locResponse, locRT) = getKeyboardResponse(self.experiment.leftRightResponses.values())
                elif self.experiment.inputDevice == 'gamepad':
                    (locResponse, locRT) = getGamepadResponse(self.experiment.stick, self.experiment.leftRightResponses.values())

                locRT *= 1000.0
                print (locResponse, locRT)
                isTargetLocationCorrect = int(self.experiment.leftRightResponses[correctLocationResp] == locResponse)

        if not locResponse:
            locResponse = 'NA'
            locRT = 'NA'
            isTargetLocationCorrect = 'NA'

            # 11. Remember target name
            stimToDraw = self.promptTextResponse
            [textEntry, similarity] = self.collectWordResponse(stimToDraw, curTrial['targetName'])
        else:
            textEntry = 'NA'
            similarity = 'NA'

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
            e_yesNoRT = yesNoRT,
            f_yesNoCorrect = isTargetPresentCorrect,
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
            curTrialIndex = 0
            for curTrial in self.trialListMatrix:
                if curTrial['blockNum'] > -1:  # stop when you reach the real trials
                    break
                self.presentTestTrial(whichPart, curTrial, curTrialIndex)
                curTrialIndex += 1
        else:
            curTrialIndex=0
            for curTrial in self.trialListMatrix:
                if curTrial['blockNum'] > -1:  # should just jump over practice trials
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
