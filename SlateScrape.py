from urllib.request import urlopen, Request
import time, random, re, json
from bs4 import BeautifulSoup as bsoup
from datetime import timedelta, date
from Classes.SlateArticleInformation import SlateArticleInformation
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 180

# keywords to use: covid-19, covid-2019, coronavirus, pandemic, epidemic
keyword = 'epidemic'

# have to change cse_tok sometimes
internalAPIurlFormat = 'https://cse.google.com/cse/element/v1' + \
                    '?rsz=filtered_cse' + \
                    '&num=10' + \
                    '&hl=en' + \
                    '&source=gcsc&gss=.com' + \
                    '&cselibv=57975621473fd078&cx=011089738672311785372:yrshxu5c-pw' + \
                    '&q={keyword}' + \
                    '&safe=off' + \
                    '&cse_tok=AJvRUv3ZbMaSbqhquJNjAijUWqGE:1591151053668' + \
                    '&sort=date:r:{date}:{date}' + \
                    '&exp=csqr,cc,4355061' + \
                    '&oq={keyword}' + \
                    '&gs_l=partner-generic.12...0.0.0.35270.0.0.0.0.0.0.0.0..0.0.csems%2Cnrl%3D13...0.0....34.partner-generic..0.0.0.&callback=google.search.cse.api14465'

# Overriding user agent for requests 
#   instead of thinking my requests come from python (urlopen), it will think they're from Chrome
pretendChrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
pretendDesktopSafari = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
pretendMobileSafari = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1'
# TODO change depending on device below - mobile or wifi
refererWithKeyword = 'https://slate.com/search?q={}&via=nav_search'.format(keyword)
headers = {'User-Agent':pretendDesktopSafari, 'Referer':refererWithKeyword, 'DNT':1} 

# Create function to make random sleep intervals (rather than always 2 seconds)
def randomSleepsFunction():
    return random.randrange(10, 70, 1) / 10.0 #0.1 is step size - so it can randomize 1.1, 1.2, 1.3, ... 6.9, 7.0 etc.

# Set up the date loop to increment the date & page count in the url
def dateRangeFunction(startDate, endDate):
    for n in range(int((endDate - startDate).days)):
        yield startDate + timedelta(n)

startDate = date(2020, 1, 1) # TODO change dates before live
endDate = date(2020, 5, 1) # doesn't count last day (5/1)
finalListOfAllArticles = []
pageCountURLAddOn = '&start={}' # Will have to be added to the API url - {} page count will be added below
for singleDate in dateRangeFunction(startDate, endDate):
    time.sleep(randomSleepsFunction())
    dateOfArticle = singleDate.strftime("%Y%m%d")
    internalAPIurl = internalAPIurlFormat.format(keyword=keyword, date=dateOfArticle)
    print(internalAPIurl)
    pretendRequestFromChrome = Request(internalAPIurl, data=None, headers=headers)
    openingURL = urlopen(pretendRequestFromChrome).read().decode('utf-8') #json

    # Cleaning out the junk at the top and bottom of the json file before parsing
    locationOfFirstParenthesis = openingURL.index('(') + 1
    openingURL = openingURL[locationOfFirstParenthesis:-2]
    #print(openingURL)

    # Make python read as json, not as a string (outputs dictionary)
    realJSONDict = json.loads(openingURL)

    # Entering dictionary to look for my things - adds all things (& info from entire items key) from 'results' key into my final list
    if 'results' in realJSONDict:
        inProcessListOfAllArticles = realJSONDict['results']
        listParsedOutURLs = []
        for eachArticle in inProcessListOfAllArticles:
            if '/tag/' in eachArticle['url'] or '/doonesbury' in eachArticle['url'] \
                or '/podcasts/' in eachArticle['url'] or '/transcripts/' in eachArticle['url'] \
                or '/author/' in eachArticle['url'] or '/live/' in eachArticle['url']: # TODO add any url exceptions here
                continue
            else:
                listParsedOutURLs.append(eachArticle)
        finalListOfAllArticles.extend(listParsedOutURLs) # add the 10 from that page into the list - used
        # .extend rather than .append so it adds the list as a list to the new list - not as one object
    
    # Calculate how many pages there will be total to put in the API url
    print('Working on ' + dateOfArticle)
    if 'resultCount' in realJSONDict['cursor']:
        numberOfResults = int(realJSONDict['cursor']['resultCount'].replace(',', '')) # find the number of total results
        if numberOfResults > 99: 
            numberOfResults = 99 # Google CSE only allows max 100 results per day/query at once
                                #   technically, I am randomizing not from all articles, but from GCSE's top articles
                                #   (based on whatever "relevancy" alg.) from my query (w/ specific date incrementing)
    else:
        continue

    # Parse over pages to increase (Google CSE only allows 10 results max)
    for startingPageCount in range(10, numberOfResults, 10):
        print('on page count ' + str(startingPageCount))
        time.sleep(randomSleepsFunction())
        newAPI = internalAPIurl + pageCountURLAddOn.format(startingPageCount)
        pretendRequestFromChrome = Request(newAPI, data=None, headers=headers)
        openingURL = urlopen(pretendRequestFromChrome).read().decode('utf-8') #json

        # Cleaning out the junk at the top and bottom of the json file before parsing
        locationOfFirstParenthesis = openingURL.index('(') + 1
        openingURL = openingURL[locationOfFirstParenthesis:-2]

        realJSONDict = json.loads(openingURL)
        if 'results' in realJSONDict:
            inProcessListOfAllArticles = realJSONDict['results']
            listParsedOutURLs = []
            for eachArticle in inProcessListOfAllArticles:
                if '/tag/' in eachArticle['url'] or '/doonesbury' in eachArticle['url'] \
                or '/podcasts/' in eachArticle['url'] or '/transcripts/' in eachArticle['url'] \
                or '/author/' in eachArticle['url'] or '/live/' in eachArticle['url']: #TODO have to change here too if added anything
                    continue
                else:
                    listParsedOutURLs.append(eachArticle)
            finalListOfAllArticles.extend(listParsedOutURLs)

# Generate a certain number of random articles within the list
print(len(finalListOfAllArticles))
desiredNumberOfArticles = random.sample(finalListOfAllArticles, numberOfRandomSamples)
print(len(desiredNumberOfArticles))

# To get the urls from that list (which has a bunch of dictionaries) and add them to a new list:
listOfURLs = []
for eachPartOfList in desiredNumberOfArticles:
    articleURL = eachPartOfList['url']
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
    driver.implicitly_wait(10)
    driver.maximize_window()
    print('Opening Selenium...')

    # Making Selenium go into the list and open the URLs
    index = 1
    for eachURL in listOfURLs:
        time.sleep(randomSleepsFunction())
        driver.get(eachURL)
        print('Starting: ' + eachURL)

        # Protecting against timeout errors/articles that don't work for some reason:
        retries = 0
        while retries < 3:
            try:
                wait.until(presence_of_element_located((By.CLASS_NAME, "article__body")))
                break
            except TimeoutException:
                driver.refresh()
                retries = retries + 1
                print('Retry #' + str(retries))
        if retries == 3: # if it has tried 5 times and STILL doesn't work, just skip it and keep going
            print('URL skipped - retries exceeded: ' + eachURL)
            continue
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bsoup(html, 'html.parser')
        firstElement = soup.find_all('div', attrs={'class': 'main'})
        # Wrapping in try/except so it goes around any errors
        try:
            for articleInfo in firstElement:
                # Headline
                inProcessHeadline = articleInfo.find('h1', attrs={'class': 'article__hed'})
                headline = inProcessHeadline.text

                # Date
                inProcessDate = articleInfo.find('span', attrs={'class': 'article__date'})
                date = inProcessDate.text

                # Authors
                inProcessAuthorsFirst = articleInfo.find('span', attrs={'class': 'article__author'})
                if inProcessAuthorsFirst.find('a') != None:
                    inProcessAuthorsSecond = inProcessAuthorsFirst.find('a')
                    author = inProcessAuthorsSecond.text
                else:
                    author = 'unable to retrieve author'

                # Article Type
                articleType = 'Non-specific article type - Slate'

                # Text
                text = ''
                inProcessText = articleInfo.find('div', attrs={'class': 'article__content'})
                inProcessTextSecond = inProcessText.find_all('p', attrs={'class': 'slate-paragraph'})
                for paragraph in inProcessTextSecond:
                    text = text + ' ' + paragraph.text
                #print('Got info for Article #' + str(index))
                print('Finished Article #' + str(index) + ': ' + eachURL)
                putThingsInClass = SlateArticleInformation(eachURL, headline, date, author, articleType, text)
                listOfInformation.append(putThingsInClass)
                index = index + 1
        except Exception as exception:
            print('URL skipped - page doesn\'t match template: ' + eachURL)
            print(exception)

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/Slate/PrelimData/'
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