# Import file w/ preliminary data, randomize 300 to pick, and put them in final data file

import os
import random
from datetime import timedelta, date, datetime

newsSource = 'TheBlaze'
numberOfSamples = 300
origDataFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/{}/PrelimData/'.format(newsSource)

listToBeCheckedForKeywords = []
origDataFile = os.listdir(origDataFilePath)
for eachFile in origDataFile:
    # Opening file - if any characters program can't recognize, will just save them (w/o reading) and copy them back in at the end
    openedFile = open(origDataFilePath + eachFile, errors="surrogateescape")
    readFile = openedFile.read()
    listToBeCheckedForKeywords.append(readFile)

listToBeRandomized = []
for article in listToBeCheckedForKeywords:
    lowerArticle = article.lower()
    if 'covid-19' in lowerArticle \
    or 'covid-2019' in lowerArticle \
    or 'coronavirus' in lowerArticle \
    or 'pandemic' in lowerArticle \
    or 'epidemic' in lowerArticle:
        listToBeRandomized.append(article)

# TODO will have to un-comment this out if not doing The Blaze
#randomData = random.sample(listToBeRandomized, numberOfSamples)

# Loop over each file to read, check the date, and change it to the format I want
#   then write to the new folder by month
finalDataFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/{}/FinalData/'.format(newsSource)
# for singleArticle in randomData:
#     allLines = singleArticle.split('\n') # turn each element in the list into another list where each line is an element
#     inputFormat = '%Y-%m-%d %H:%M:%S%z' # TODO change depending on input from files
#     outputFormat = '%B %d'
#     inProcessDate = datetime.strptime(allLines[2], inputFormat)
#     finalDate = inProcessDate.strftime(outputFormat)
#     allLines[2] = finalDate
#     dateOfArticle = allLines[2].split(' ')
#     monthOfPublication = dateOfArticle[0]
#     finalData = open(finalDataFilePath + monthOfPublication + '/' + allLines[0] + '.txt', 'w')
#     finalData.write('\n'.join(allLines)) #, errors="surrogateescape")
# print('Done! :)')

# For WSJ/Slate/Breitbart/Buzzfeed (since date wasn't taken in as a datetime format) to sort into month folders:
#baseFinalDataFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/{}/FinalData/'.format(newsSource)
# januaryPath = 'January/'
# februaryPath = 'February/'
# marchPath = 'March/'
# aprilPath = 'April/'
# for singleArticle in randomData:
#     allLines = singleArticle.split('\n')
#     dateOfArticle = allLines[2].split(' ')
#     monthOfPublication = dateOfArticle[0][:3]
#     if 'Jan' in monthOfPublication:
#         finalData = open(baseFinalDataFilePath + januaryPath + allLines[0] + '.txt', 'w')
#         finalData.write('\n'.join(allLines))
#     elif 'Feb' in monthOfPublication:
#         finalData = open(baseFinalDataFilePath + februaryPath + allLines[0] + '.txt', 'w')
#         finalData.write('\n'.join(allLines))
#     elif 'Mar' in monthOfPublication:
#         finalData = open(baseFinalDataFilePath + marchPath + allLines[0] + '.txt', 'w')
#         finalData.write('\n'.join(allLines))
#     elif 'Apr' in monthOfPublication:
#         finalData = open(baseFinalDataFilePath + aprilPath + allLines[0] + '.txt', 'w')
#         finalData.write('\n'.join(allLines))
#     else:
#         finalData = open(baseFinalDataFilePath + allLines[0] + '.txt', 'w') # write to larger file - just in case some weird formatting
#         finalData.write('\n'.join(allLines))
# print('Done!! :)')

# The Blaze function - accidentally grabbed some data outside of date range, so have to parse them out again here
baseFinalDataFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/{}/FinalData/'.format(newsSource)
januaryPath = 'January/'
februaryPath = 'February/'
marchPath = 'March/'
aprilPath = 'April/'
listToBeRandomizedWithDate = []
for singleArticle in listToBeRandomized:
    allLines = singleArticle.split('\n')
    dateOfArticle = allLines[2].split(' ')
    monthOfPublication = dateOfArticle[0][:3]
    yearOfPublication = dateOfArticle[-1]
    if 'Jan' in monthOfPublication \
    and '201' not in yearOfPublication \
    and '200' not in yearOfPublication:
        listToBeRandomizedWithDate.append(singleArticle)
    elif 'Feb' in monthOfPublication \
    and '201' not in yearOfPublication \
    and '200' not in yearOfPublication:
        listToBeRandomizedWithDate.append(singleArticle)
    elif 'Mar' in monthOfPublication \
    and '201' not in yearOfPublication \
    and '200' not in yearOfPublication:
        listToBeRandomizedWithDate.append(singleArticle)
    elif 'Apr' in monthOfPublication \
    and '201' not in yearOfPublication \
    and '200' not in yearOfPublication:
        listToBeRandomizedWithDate.append(singleArticle)
    else:
        continue

# Take random sample now - The Blaze (skipping dates out of range)
randomData = random.sample(listToBeRandomizedWithDate, numberOfSamples)

for singleArticle in randomData:
    allLines = singleArticle.split('\n')
    dateOfArticle = allLines[2].split(' ')
    monthOfPublication = dateOfArticle[0][:3]
    if 'Jan' in monthOfPublication:
        finalData = open(baseFinalDataFilePath + januaryPath + allLines[0] + '.txt', 'w')
        finalData.write('\n'.join(allLines))
    elif 'Feb' in monthOfPublication:
        finalData = open(baseFinalDataFilePath + februaryPath + allLines[0] + '.txt', 'w')
        finalData.write('\n'.join(allLines))
    elif 'Mar' in monthOfPublication:
        finalData = open(baseFinalDataFilePath + marchPath + allLines[0] + '.txt', 'w')
        finalData.write('\n'.join(allLines))
    elif 'Apr' in monthOfPublication:
        finalData = open(baseFinalDataFilePath + aprilPath + allLines[0] + '.txt', 'w')
        finalData.write('\n'.join(allLines))
    else:
        finalData = open(baseFinalDataFilePath + allLines[0] + '.txt', 'w') # write to larger file - just in case some weird formatting
        finalData.write('\n'.join(allLines))
print('Done!! :)')

# BEFORE RUNNING!!!
#   Did you change the news source?
#   Are your files named correctly?
#   Is there anything you should delete from the files first?
#   Do you need to have the date part? (if YES, add incoming date as inputFormat and un-comment out
#       lines inputFormat = __________ to allLines[2] = finalDate