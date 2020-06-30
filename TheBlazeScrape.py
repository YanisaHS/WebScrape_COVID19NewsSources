from urllib.request import urlopen, Request
import time, random, re, json
from bs4 import BeautifulSoup as bsoup
from datetime import timedelta, date, datetime
from Classes.TheBlazeArticleInformation import TheBlazeArticleInformation
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 300 # TODO change in live samples

# keywords to use: covid-19, covid-2019, coronavirus, pandemic, epidemic
keyword = 'epidemic'

internalAPIurlFormat = 'https://www.theblaze.com/res/load_more_posts/data.js' + \
                    '?site_id=19257436' + \
                    '&rm_lazy_load=1' + \
                    '&q={keyword}' + \
                    '&exclude_post_ids=2646161817%2C2646161770%2C2646161437%2C2646155821%2C2646155706%2C2646155198%2C2646155111%2C2646154148' + \
                    '&node_id=%2Froot%2Fblocks%2Fblock%5Bsearch%5D%2Fabtests%2Fabtest%5B1%5D%2Felement_wrapper%5B2%5D%2Felement_wrapper%5B2%5D%2Fposts%5B2%5D-' + \
                    '&pn={pageNumber}&' + \
                    'resource_id=search_{keyword}' + \
                    '&site_id=19257436' + \
                    '&path_params=%7B%7D' + \
                    '&override_device=desktop'
# Overriding user agent for requests 
#   instead of thinking my requests come from python (urlopen), it will think they're from Chrome
pretendChrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
pretendDesktopSafari = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
pretendMobileSafari = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1'
# TODO change depending on device below - mobile or wifi (chrome or safari)
refererWithKeyword = 'https://www.theblaze.com/search/?q={}'.format(keyword) # TODO change referer if using in another file!!
                                                                            # TODO get it from dev tools - Request Headers - referer
headers = {'User-Agent':pretendChrome, 'Referer':refererWithKeyword, 'DNT':1}

# Create function to make random sleep intervals (rather than always 2 seconds)
def randomSleepsFunction():
    return random.randrange(10, 70, 1) / 10.0 #0.1 is step size - so it can randomize 1.1, 1.2, 1.3, ... 6.9, 7.0 etc.

# TODO make it so it looks back - either "more_posts_exist" = false OR date hits december
#   it looks like year is posted (11 April 2011) if it is earlier than 2020?
#   in soup part or before randomizing, ignore articles outside of dates range (w/ years or MAy or June)

pageNumber = 1 # to get it started
finalListOfAllArticles = []
thereIsANextPage = True
print('Loading APIs...')
while thereIsANextPage == True: 
    time.sleep(randomSleepsFunction())
    internalAPIurl = internalAPIurlFormat.format(keyword=keyword, pageNumber=pageNumber)
    print(internalAPIurl)
    pretendRequestFromChrome = Request(internalAPIurl, data=None, headers=headers)
    openingURL = urlopen(pretendRequestFromChrome).read().decode('utf-8') #json

    # Make python read as json, not as a string (outputs dictionary)
    realJSONDict = json.loads(openingURL)

    # if there is no next page, then exit loop
    if 'has_more' in realJSONDict:
        lookingForNextPage = realJSONDict['has_more']
        if lookingForNextPage == True:
            thereIsANextPage = lookingForNextPage
            pageNumber = pageNumber + 1
        else:
            thereIsANextPage = False
            break
    
    # TODO make sure the year exceptions below work before running (they were updated from ', 201' to '201)
    if 'posts_by_source' in realJSONDict:
        if 'search_results_filtered' in realJSONDict['posts_by_source']:
            inProcessListOfArticles = realJSONDict['posts_by_source']['search_results_filtered']
            listOfURLs = []
            for eachArticle in inProcessListOfArticles:
                if '/podcasts/' in eachArticle['raw_share_url']: # TODO add any url exceptions here
                    continue
                elif '201' in eachArticle['formated_full_created_ts'] \
                or '200' in eachArticle['formated_full_created_ts'] \
                or 'May' in eachArticle['formated_full_created_ts'] \
                or 'June' in eachArticle['formated_full_created_ts']: # So only ones in our Jan-Apr date range will come up
                    continue
                else:
                    listOfURLs.append(eachArticle)
    finalListOfAllArticles.extend(listOfURLs)

# Make a new list w/ only urls
listOfURLsToBeRandomized = []
for eachPartOfList in finalListOfAllArticles:
    articleURL = eachPartOfList['raw_share_url']
    listOfURLsToBeRandomized.append(articleURL)
#print(listOfURLsToBeRandomized)

# Generate a certain number of random articles within the list
print(str(len(listOfURLsToBeRandomized)) + ' total articles')
desiredNumberOfArticles = None # have to create variable outside of if statement
if len(listOfURLsToBeRandomized) < numberOfRandomSamples:
    print('Using ' + str(len(listOfURLsToBeRandomized)) + ' articles')
    desiredNumberOfArticles = listOfURLsToBeRandomized
else:
    desiredNumberOfArticles = random.sample(listOfURLsToBeRandomized, numberOfRandomSamples)
print(len(desiredNumberOfArticles))

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

    index = 1
    for eachURL in desiredNumberOfArticles:
        time.sleep(randomSleepsFunction())
        driver.get(eachURL)
        print('Starting: ' + eachURL)
    
        # Protecting against timeout errors/articles that don't work for some reason:
        retries = 0
        while retries < 2:
            try:
                wait.until(presence_of_element_located((By.CLASS_NAME, "body-description")))
                break
            except TimeoutException:
                driver.refresh()
                retries = retries + 1
                print('Retry #' + str(retries))
        if retries == 2: # if it has tried a bunch and STILL doesn't work, just skip it and keep going
            print('URL skipped - retries exceeded: ' + eachURL)
            continue
        time.sleep(2)
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bsoup(html, 'html.parser')
        firstElement = soup.find_all('div', attrs={'class': 'post-page'})
        # Wrapping in try/except so it goes around any errors
        try:
            for articleInfo in firstElement:
                # Headline
                inProcessHeadline = articleInfo.find('h1', attrs={'class': 'headline'})
                headline = inProcessHeadline.text

                # Date
                inProcessDate = articleInfo.find('span', attrs={'class': 'post-date'})
                date = inProcessDate.text

                # Authors
                inProcessAuthorsFirst = articleInfo.find('div', attrs={'class': 'post-author'})
                if inProcessAuthorsFirst != None:
                    author = inProcessAuthorsFirst.text
                else:
                    author = 'unable to retrieve author'

                # Article Type
                inProcessArticleTypeFirst = articleInfo.find('a', attrs={'class': 'widget__section'})
                if inProcessArticleTypeFirst.text.lower() == 'opinion' \
                or inProcessArticleTypeFirst.text.lower() == 'op-ed':
                    articleType = 'Opinion Article'
                else:
                    articleType = 'News Report Article'

                # Text
                text = ''
                inProcessText = articleInfo.find('div', attrs={'class': 'body-description'})
                inProcessTextSecond = inProcessText.find_all('p')
                for paragraph in inProcessTextSecond:
                    text = text + ' ' + paragraph.text
                print('Finished Article #' + str(index) + ': ' + eachURL)
                putThingsInClass = TheBlazeArticleInformation(eachURL, headline, date, author, articleType, text)
                listOfInformation.append(putThingsInClass)
                index = index + 1
        except Exception as exception:
            print('URL skipped - page doesn\'t match template: ' + eachURL)
            print(exception)
    
    # must close the driver after task finished
    driver.close()

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/TheBlaze/PrelimData/'
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