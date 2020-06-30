
from urllib.request import urlopen
import time, random, json # i am good
from bs4 import BeautifulSoup as bsoup
from datetime import timedelta, date
from Classes.FoxArticleInformation import FoxArticleInformation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 300

keyword = 'epidemic'
# Filtered based on: keyword, article (rather than video/etc.), date, source/came from Fox)
internalAPIurlFormat = 'https://api.foxnews.com/search/web' + \
                '?q={keyword}+more:pagemap:metatags-pagetype:article+more:pagemap:metatags-dc.type:Text.Article' + \
                '+more:pagemap:metatags-dc.date:{date}+more:pagemap:metatags-dc.source:Fox%20News' + \
                '&siteSearch=foxnews.com' + \
                '&siteSearchFilter=i'

# Set up the date loop to increment the date & page count in the url
def dateRangeFunction(startDate, endDate):
    for n in range(int((endDate - startDate).days)):
        yield startDate + timedelta(n)

startDate = date(2020, 1, 1)
endDate = date(2020, 5, 1) # doesn't count last day (5/1)
finalListOfAllArticles = []
pageCountURLAddOn = '&start={}' # Will have to be added to the API url - {} page count will be added below
for singleDate in dateRangeFunction(startDate, endDate):
    dateOfArticle = singleDate.strftime("%Y-%m-%d")
    internalAPIurl = internalAPIurlFormat.format(keyword=keyword, date=dateOfArticle)
    openingURL = urlopen(internalAPIurl).read() #json

    # Make python read as json, not as a string (outputs dictionary)
    realJSONDict = json.loads(openingURL)

    # Entering dictionary to look for my things - adds all things (& info from entire items key) from 'item' key into my final list
    if 'items' in realJSONDict:
        inProcessListOfAllArticles = realJSONDict['items']
        finalListOfAllArticles.extend(inProcessListOfAllArticles) # add the 10 from that page into the list - used
        # .extend rather than .append so it adds the list as a list to the new list - not as one object

    # Calculate how many pages there will be total to put in the API url
    print('Working on ' + dateOfArticle)
    if 'nextPage' in realJSONDict['queries']:
        numberOfResults = int(realJSONDict['queries']['nextPage'][0]['totalResults']) # find the number of total results
        if numberOfResults > 99: 
            numberOfResults = 99 # Google CSE only allows max 100 results per day/query at once
                                #   technically, I am randomizing not from all articles, but from GCSE's top articles
                                #   (based on whatever "relevancy" alg.) from my query (w/ specific date incrementing)
    else:
        continue
    # Parse over pages to increase (Fox only allows 10 results max)
    for startingPageCount in range(10, numberOfResults, 10):
        print('on page count ' + str(startingPageCount))
        time.sleep(2)
        newAPI = internalAPIurl + pageCountURLAddOn.format(startingPageCount)
#       print(newAPI)
        openingURL = urlopen(newAPI).read() #json
        realJSONDict = json.loads(openingURL)
        if 'items' in realJSONDict:
            inProcessListOfAllArticles = realJSONDict['items']
            finalListOfAllArticles.extend(inProcessListOfAllArticles)

# Generate a certain number of random articles within the list
desiredNumberOfArticles = random.sample(finalListOfAllArticles, numberOfRandomSamples)

# To get the urls from that list (which has a bunch of dictionaries) and add them to a new list:
listOfURLs = []
for eachPartOfList in desiredNumberOfArticles:
    articleURL = eachPartOfList['link']
    listOfURLs.append(articleURL)
#print(listOfURLs)

# Preparing to start with running chrome driver with Selenium:
chromeDriverPath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/chromedriver'

chromeOptions = Options()
chromeOptions.add_argument('--headless')
webDriver = webdriver.Chrome(executable_path=chromeDriverPath, options=chromeOptions)

listOfInformation = []
with webDriver as driver:
    # Set timeout time 
    wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(15)
    driver.maximize_window()
    print('Opening Selenium')

    # Making Selenium go into the list and open the URLs
    index = 1
    for eachURL in listOfURLs:
        time.sleep(2)
        driver.get(eachURL)
        wait.until(presence_of_element_located((By.CLASS_NAME, 'author-byline')))
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bsoup(html, 'html.parser')
        firstElement = soup.find_all('div', attrs={'class': 'page-content'})
        for articleInfo in firstElement:
            # Headline
            inProcessHeadline = articleInfo.find('h1', attrs={'class': 'headline'})
            headline = inProcessHeadline.text 

            # Date
            inProcessDate = articleInfo.find('div', attrs={'class': 'article-date'})
            date = inProcessDate.text

            # Authors
            inProcessAuthorsFirst = articleInfo.find('div', attrs={'class': 'author-byline'})
            inProcessAuthorsSecond = inProcessAuthorsFirst.find('a')
            author = inProcessAuthorsSecond.text

            # Article Type
            inProcessArticleType = articleInfo.find('div', attrs={'class': 'eyebrow'})
            inProcessArticleTypeSecond = inProcessArticleType.find('a')
            inProcessArticleTypeText = inProcessArticleTypeSecond.text
            if inProcessArticleTypeText.lower() == 'opinion':
                articleType = 'Opinion Article'
            else:
                articleType = 'News Report Article'

            # Text - get each paragraph, clean out ad links & extra info, then put them together
            text = ''
            inProcessText = articleInfo.find('div', attrs={'class': 'article-body'})
            inProcessTextSecond = inProcessText.find_all('p', recursive=False)
            for paragraph in inProcessTextSecond:
                if paragraph.find('strong') != None:
                    continue
                else:
                    text = text + ' ' + paragraph.text
            print('Got info for Article #' + str(index))
            putThingsInClass = FoxArticleInformation(eachURL, headline, date, author, articleType, text)
            listOfInformation.append(putThingsInClass)
            index = index + 1

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/Fox/PrelimData/'
for article in listOfInformation:
    makeFile = open(beginningFilePath + article.headline + '.txt', 'w')
    makeFile.write(article.headline + '\n' + article.url + '\n' + str(article.date) + '\n' + article.author + '\n' + article.articleType + '\n\n' + article.text)
print('Done!!!')

# Change date range and number of random samples before doing it for real!!
# BEFORE RUNNING!!!
#   - Did you change the keyword?
#   - Is the date range correct?
#   - Are you sampling the correct amount? (currently taking 300 of each, then will take 300 of that total)
#   - Is the destination file correct?
# (Keywords) Go in this order:
#   covid-19, covid-2019, coronavirus, pandemic, epidemic