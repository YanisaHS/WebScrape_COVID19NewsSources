from urllib.request import urlopen, Request
import time, random, re, json
from bs4 import BeautifulSoup as bsoup
from datetime import timedelta, date, datetime
from Classes.BuzzfeedArticleInformation import BuzzfeedArticleInformation
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

internalAPIurlFormat = 'https://www.buzzfeed.com/search/api' + \
                    '?q={keyword}' + \
                    '&page={pageNumber}' + \
                    '&page_size=50' # max page size is 50

# Overriding user agent for requests 
#   instead of thinking my requests come from python (urlopen), it will think they're from Chrome
pretendChrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
pretendDesktopSafari = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
pretendMobileSafari = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1'
# TODO change depending on device below - mobile or wifi (chrome or safari)
refererWithKeyword = 'https://www.buzzfeed.com/search?q={}'.format(keyword) # TODO change referer if using in another file!!
                                                                            # TODO get it from dev tools - Request Headers - referer
headers = {'User-Agent':pretendChrome, 'Referer':refererWithKeyword, 'DNT':1}

# Create function to make random sleep intervals (rather than always 2 seconds)
def randomSleepsFunction():
    return random.randrange(10, 70, 1) / 10.0 #0.1 is step size - so it can randomize 1.1, 1.2, 1.3, ... 6.9, 7.0 etc.

startDate = 'January 1, 2020' 
endDate = 'May 1, 2020' # TODO change dates before live
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
    if 'next' in realJSONDict:
        lookingForNextPage = realJSONDict['next']
        if lookingForNextPage != None:
            pageNumber = lookingForNextPage
        else:
            thereIsANextPage = False
            break
    
    if 'results' in realJSONDict:
        inProcessListOfAllArticles = realJSONDict['results']
        listParsedOutURLs = []
        # Parsing out dates outside of the date range
        for eachArticle in inProcessListOfAllArticles:
            dateFormat = '%B %d, %Y'
            dateFromEachArticle = datetime.strptime(eachArticle['time_since'], dateFormat)
            if dateFromEachArticle < datetime.strptime(startDate, dateFormat) \
            or dateFromEachArticle >= datetime.strptime(endDate, dateFormat):
                continue
            else:
                # Parsing out bad urls - only looking in Buzzfeed News
                if '/video' in eachArticle['canonical_url'] \
                or '/newsoclock/' in eachArticle['canonical_url'] \
                or 'buzzfeed.com' in eachArticle['canonical_url'] \
                or 'most-powerful-photos-of-this-week' in eachArticle['canonical_url']: # TODO add any url exceptions here
                    continue
                else:
                    eachArticle = eachArticle['canonical_url'].replace('\\', '')
                    listParsedOutURLs.append(eachArticle)
    finalListOfAllArticles.extend(listParsedOutURLs) # add the 10 from that page into the list - used
    # .extend rather than .append so it adds the list as a list to the new list - not as one object

# Generate a certain number of random articles within the list
print(str(len(finalListOfAllArticles)) + ' total articles')
desiredNumberOfArticles = None # have to create variable outside of if statement
if len(finalListOfAllArticles) < numberOfRandomSamples:
    print('Using ' + str(len(finalListOfAllArticles)) + ' articles')
    desiredNumberOfArticles = finalListOfAllArticles
else:
    desiredNumberOfArticles = random.sample(finalListOfAllArticles, numberOfRandomSamples)
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
                wait.until(presence_of_element_located((By.CLASS_NAME, "subbuzz-text")))
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
        firstElement = soup.find_all('div', attrs={'class': 'grid-layout-main'})
        # Wrapping in try/except so it goes around any errors
        try:
            for articleInfo in firstElement:
                # Headline
                inProcessHeadline = articleInfo.find('h1', attrs={'class': 'news-article-header__title'})
                headline = inProcessHeadline.text

                # Date
                inProcessDate = articleInfo.find('p', attrs={'class': 'news-article-header__timestamps-posted'})
                date = inProcessDate.text

                # Authors
                inProcessAuthorsFirst = articleInfo.find('span', attrs={'class': 'news-byline-full__info-wrapper'})
                if inProcessAuthorsFirst.find('span', attrs={'class': 'news-byline-full__name'}) != None:
                    inProcessAuthorsSecond = inProcessAuthorsFirst.find('span', attrs={'class': 'news-byline-full__name'})
                    author = inProcessAuthorsSecond.text
                else:
                    author = 'unable to retrieve author'

                # Article Type
                inProcessArticleTypeFirst = articleInfo.find('li', attrs={'class': 'news-article-breadcrumbs__label'})
                inProcessArticleTypeSecond = inProcessArticleTypeFirst.find('a')
                if inProcessArticleTypeSecond.text.lower() == 'opinion':
                    articleType = 'Opinion Article'
                else:
                    articleType = 'News Report Article'

                # Text
                text = ''
                inProcessText = articleInfo.find_all('div', attrs={'class': 'subbuzz-text'})
                listOfParagraphs = []
                # Must search for appropriate sections w/ paragraphs (some in the middle that are a different class)
                for eachText in inProcessText:
                    inProcessTextSecond = eachText.find_all('p')
                    listOfParagraphs.extend(inProcessTextSecond)
                for paragraph in listOfParagraphs:
                    if paragraph.find('i') != None:
                        continue
                    else:
                        text = text + ' ' + paragraph.text
                print('Finished Article #' + str(index) + ': ' + eachURL)
                putThingsInClass = BuzzfeedArticleInformation(eachURL, headline, date, author, articleType, text)
                listOfInformation.append(putThingsInClass)
                index = index + 1
        except Exception as exception:
            print('URL skipped - page doesn\'t match template: ' + eachURL)
            print(exception)

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/Buzzfeed/PrelimData/'
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