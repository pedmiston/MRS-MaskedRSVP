#!/usr/bin/env python

import random
import pandas as pd
import numpy as np

def circularList(lst,seed):
    if not isinstance(lst,list):
        lst = range(lst)
    i = 0
    random.seed(seed)
    random.shuffle(lst)
    while True:
        yield lst[i]
        if (i+1) % len(lst) ==0:
            random.shuffle(lst)
        i = (i + 1)%len(lst)

pics = pd.read_csv('targets.csv', names = ['category', ])['category'].tolist()
foils = pd.read_csv('foils.csv', names = ['category', ])['category'].tolist()

criticalTrialType = ['foil']*2 + ['category'] + ['match']*2
criticalTrialType *= 3

#distribution = ['.40', '.20', '.40'] #don't know how to integrate this in to ensure the right distribution..want 7 foils, 4 category, 7 match trials
cues = list(pics)
isMatch = ['0','0','1']
separator = ","
numIter = 1
picNum = range(1, 7)

##there are 18 targets. each is presented at the beginning of a trial (so 18 trials) and this is
##the picture the participant needs to look for. After the target, the participant sees another
## 6 pictures. On picture 2-5 of these 6 is the critical trial. On 7 of these trials, the critical
##picture is the target picture. On another 7, it is a random foil. On the remaining 4 trials, the critical
##picture is a category match to the target. These have the same names except targets' names end with
## 1 and category match names end with 2.

#In the before group, each trial began with a
#fixation cross for 500 ms, followed by the name of the target
#for 700 ms, a 200-ms blank screen, and then the sequence of
#pictures. (from a recent RSVP paper)

##picture durations: target stays up for X; trial pics stay up for X. ISI is

def randomButNot (arr, index):
    randIndex=index
    while randIndex == index:
        randIndex = random.randint(0, len(arr)-1)
    return arr[randIndex]

def main(subjCode,seed):
    testFile = open('trialList_test_'+subjCode+ '.csv','w')
    print >>testFile, separator.join(("block", "picCategory", "targetPic", "criticalTrialType", "criticalPicFile", "criticalTrialNum", "picFile1", "picFile2", "picFile3", "picFile4", "picFile5", "picFile6", "isMatch"))
    random.seed(int(seed))
    np.random.seed(int(seed)) #if you're using the numpy random number generator, you need to set the seed for it separately (!)
    trialList = []
    trialTypeToPic = {'match':'1', 'category':'2'}
    trialTypeToMatch = {'match':'1', 'category':'0'}
    conditionList = circularList(criticalTrialType,seed)
    numBlocks = 5

    for curBlock in range(numBlocks):
        trialList.append([])
        for picIndex,curPic in enumerate(pics):
            curTarget = curPic + "1"

            curTrialType = conditionList.next()
            curCriticalTrialNum = np.random.choice([2,3,4,5], 1)[0]
            distractorPics = np.random.choice(foils, 6, replace = False).tolist()

            curTrialPics = {}
            for curPicNum in picNum:
                picCol = "pic"+str(curPicNum)+"File"
                if curPicNum == curCriticalTrialNum:
                    if curTrialType == "foil":
                        curPicFile = distractorPics.pop()
                        curIsMatch = 0
                    else:
                        curPicFile = curPic + trialTypeToPic[curTrialType]
                        curIsMatch = trialTypeToMatch[curTrialType]
                

                    # duplicate information in the pic column
                    curTrialPics[curPicNum] = curPicFile
                else:
                    curTrialPics[curPicNum] = distractorPics.pop() + ""

            trialList[curBlock].append(separator.join((str(curBlock+1), curPic, curTarget, curTrialType, curPicFile, str(curCriticalTrialNum), curTrialPics[1], curTrialPics[2], curTrialPics[3], curTrialPics[4], curTrialPics[5], curTrialPics[6], str(curIsMatch))))

    for curBlock in trialList:    
        random.shuffle(curBlock)
        for curTrialList in curBlock:    
            print >>testFile, curTrialList

if __name__ == "__main__":
    trialList = main('testTrials-13',13)
