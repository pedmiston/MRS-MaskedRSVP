#!/usr/bin/env python
import pandas as pd
import random

from collections import OrderedDict
from itertools import product
from unipath import Path

def chooseTargetAndFoil(name, opts):
    """
    opts is a DataFrame with columns 'picName' and 'picFile'
    """
    choices = opts[opts.picName == name]
    pics = choices.picFile.tolist()
    assert len(pics) >= 2, \
        "There weren't enough pics with the name {}".format(name)
    random.shuffle(pics)
    return pics[0:2]

def listToLine(orderedList):
    stringParams = map(str, orderedList)
    trialRow = ','.join(stringParams) + '\n'
    return trialRow

def main(trialsFileName, seed):
    random.seed(seed)

    orderedFields = (
        'part', 'blockNum',
        'targetName', 'targetFile', 'foilFile', 'whenTargetName',
        'isMask', 'whenMask',
        'picDurationType', 'picDurationSec', 'targetPos',
        'picFile1', 'picFile2', 'picFile3', 'picFile4', 'picFile5', 'picFile6',
        'isTargetPresent', 'whichTarget',
    )

    curTrial = OrderedDict()
    for field in orderedFields:
        curTrial[field] = ''

    picDurationTypeOpts = ['long', 'short']
    picDurationMap = {'long': 0.083, 'short': 0.025}
    whenTargetNameOpts = ['before', 'after']

    # randomly decide whether participants get the target name before
    # blocks first or the target name after blocks first
    random.shuffle(whenTargetNameOpts)

    blockOpts = {}
    blockOpts['picDurationType'] = picDurationTypeOpts
    blockOpts['whenTargetName'] = whenTargetNameOpts
    blockItems = list(product(*blockOpts.values()))
    blocks = pd.DataFrame(blockItems, columns = blockOpts.keys())

    blocks['part'] = 'test'

    practiceBlockInfo = {}
    practiceBlockInfo['whenTargetName'] = 'before'
    practiceBlockInfo['picDurationType'] = 'long'
    practiceBlockInfo['part'] = 'practice'
    practiceBlock = pd.DataFrame(practiceBlockInfo, index = [-1, ])

    blocks = blocks.append(practiceBlock).sort()

    numPracticeTrials = 5
    trialsPerBlock = 32
    proportionTargetPresent = 0.75

    targetPresentTrials = int(trialsPerBlock * proportionTargetPresent)
    targetAbsentTrials = trialsPerBlock - targetPresentTrials

    withinBlockOpts = {}
    withinBlockOpts['isTargetPresent'] = [1,] * targetPresentTrials + \
                                         [0,] * targetAbsentTrials
    assert targetPresentTrials % 2 == 0, \
        ("If there aren't an even number of target present trials,"
         "the mask can't be evenly split")
    withinBlockOpts['isMask'] = [1, 0] * (trialsPerBlock/2)

    withinBlockTrials = pd.DataFrame(withinBlockOpts)

    targets = pd.read_csv(Path('stimuli', 'images', 'targets.csv'))
    targetNameList = targets.picName.unique().tolist()
    random.shuffle(targetNameList)

    distractors = pd.read_csv(Path('stimuli', 'images', 'distractors-1000.csv'),
            names = ['picFile', ])
    distractorList = distractors.picFile.tolist()
    random.shuffle(distractorList)

    trialList = open('trials_' + trialsFileName + '.csv', 'w')
    header = listToLine(curTrial.keys())
    trialList.write(header)

    for blockNum, blockInfo in blocks.iterrows():
        curBlock = []

        curPart = blockInfo['part']
        whenTargetName = blockInfo['whenTargetName']
        picDurationType = blockInfo['picDurationType']
        picDurationSec = picDurationMap[picDurationType]

        curTrial['part'] = curPart
        curTrial['blockNum'] = blockNum
        curTrial['whenTargetName'] = whenTargetName
        curTrial['picDurationType'] = picDurationType
        curTrial['picDurationSec'] = picDurationSec

        for trialN, trialInfo in withinBlockTrials.iterrows():
            if curPart == 'practice' and trialN > numPracticeTrials:
                break

            curTrial['isMask'] = trialInfo['isMask']
            curTrial['isTargetPresent'] = trialInfo['isTargetPresent']
            curTrial['whenMask'] = curTrial['whenTargetName']

            # determine the target name to appear as text in this trial
            try:
                targetName = targetNameList.pop()
            except IndexError:
                print 'Ran out of unique targets! Resetting...'
                targetNameList = targets.picName.unique().tolist()
                random.shuffle(targetNameList)
                targetName = targetNameList.pop()
            curTrial['targetName'] = targetName

            # set the parameters for target present|absent trials
            if curTrial['isTargetPresent'] == 1:
                targetFile, foilFile = chooseTargetAndFoil(targetName, targets)
                targetPos = random.choice([2, 3, 4, 5])
                whichTarget = random.choice(['left', 'right'])

                curTrial['targetFile'] = targetFile
                curTrial['foilFile'] = foilFile
                curTrial['targetPos'] = targetPos
                curTrial['whichTarget'] = whichTarget
            else:
                stringForNAValue = 'NA'
                curTrial['targetFile'] = stringForNAValue
                curTrial['foilFile'] = stringForNAValue
                curTrial['targetPos'] = -1
                curTrial['whichTarget'] = stringForNAValue

            # determine pictures in the sequence
            for picPos in [1, 2, 3, 4, 5, 6]:
                picFileID = 'picFile{}'.format(picPos)

                if picPos == curTrial['targetPos']:
                    picFile = curTrial['targetFile']
                else:
                    try:
                        picFile = distractorList.pop()
                    except IndexError:
                        print 'Ran out of unique distractors! Resetting...'
                        distractorList = distractors.picFile.tolist()
                        random.shuffle(distractorList)
                        picFile = distractorList.pop()

                curTrial[picFileID] = picFile

            # all params for curTrial have been set. Add to curBlock
            curBlock.append(curTrial.values())

        # all trials for curBlock have been created. Shuffle and write
        random.shuffle(curBlock)
        for trialParams in curBlock:
            trial = listToLine(trialParams)
            trialList.write(trial)

if __name__ == "__main__":
    main('test', 13)
