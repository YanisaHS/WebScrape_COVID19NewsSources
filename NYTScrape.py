from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup
import json, random, time, pytz
from datetime import datetime, timedelta, date
from Classes.NYTArticleInformation import NYTArticleInformation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 500 

fullListOfArticles = []
def getArticlesEachMonthJSONFunction(month):
    openNYTMonthJSON = open('/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/NYT_AllArticleInfo_{}2020.txt'.format(month))
    readNYTMonthAsJSON = json.load(openNYTMonthJSON)

    keywordInProcessList = readNYTMonthAsJSON['response']['docs'] 

    # check if my keywords are in the keywords from the articles
    articleInfoBeforeDateCheck = []
    for eachArticle in keywordInProcessList:
        if 'keywords' in eachArticle:
            keywordList = eachArticle['keywords']
            for keywordValue in keywordList:
                valueToSearch = keywordValue['value']
                lowercaseValue = valueToSearch.lower()
                if 'covid-19' in lowercaseValue \
                or 'covid-2019' in lowercaseValue \
                or 'coronavirus' in lowercaseValue \
                or 'pandemic' in lowercaseValue \
                or 'epidemic' in lowercaseValue:
                    articleInfoBeforeDateCheck.append(eachArticle)

    # check to make sure the dates are within the correct range and toss out 'multimedia' articles
    articleInfoInDateRange = []
    startDate = datetime(2020, 1, 1)
    endDate = datetime(2020, 4, 30)
    utc = pytz.UTC
    for eachArticle in articleInfoBeforeDateCheck:
        dateFormat = '%Y-%m-%dT%H:%M:%S%z'
        dateOfArticle = datetime.strptime(eachArticle['pub_date'], dateFormat)
        if dateOfArticle >= utc.localize(startDate) and dateOfArticle <= utc.localize(endDate) \
            and eachArticle['document_type'] != 'multimedia':
            articleInfoInDateRange.append(eachArticle)

    # Getting all the article info except text: headline, url, date, author, article type
    for eachPartOfList in articleInfoInDateRange:
        # Headline
        headline = eachPartOfList['headline']['main']

        # URL
        url = eachPartOfList['web_url']

        # Date
        date = eachPartOfList['pub_date']

        # Author
        author = eachPartOfList['byline']['original']

        # Article Type
        if eachPartOfList['section_name'].lower() == 'opinion':
            articleType = 'Opinion Article'
        else:
            articleType = 'News Report Article'
        
        # Making the info into an object from the NYT class
        putThingsInClass = NYTArticleInformation(url, headline, date, author, articleType)
        fullListOfArticles.append(putThingsInClass)

getArticlesEachMonthJSONFunction('Jan')
getArticlesEachMonthJSONFunction('Feb')
getArticlesEachMonthJSONFunction('March')
getArticlesEachMonthJSONFunction('April')

# Generate a certain number of random articles within the list
desiredNumberOfArticles = random.sample(fullListOfArticles, numberOfRandomSamples)

# Preparing to start with running chrome driver with Selenium:
chromeDriverPath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/chromedriver'

chromeOptions = Options()
chromeOptions.add_argument('--headless')
webDriver = webdriver.Chrome(executable_path=chromeDriverPath, options=chromeOptions)

fullArticleText = []
with webDriver as driver:
    # Set timeout time 
    wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(20)
    driver.maximize_window()
    print('Opening Selenium...')

    # Making Selenium go into the list and open the URLs
    index = 1
    for eachArticle in desiredNumberOfArticles:
        time.sleep(2)
        #print('First url: ' + eachArticle.url)
        driver.get(eachArticle.url)
        time.sleep(2)
        currentURL = driver.current_url # so it opens the current url in case of redirects
        print('Got current url: ' + currentURL)
        wait.until(presence_of_element_located((By.CLASS_NAME, "StoryBodyCompanionColumn")))

        # Click the "Show Full Article" button if there is one
        print('Loading full article...')
        try:
            lookForXPath = driver.find_element_by_xpath("//button[contains(text(), 'Show Full Article')]")
            lookForXPath.click()
            time.sleep(2)
        except NoSuchElementException:
            dummyVariable = 'ok program...' # literally just put this dummy in because I'm not sure what to put here?
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bsoup(html, 'html.parser')

        # Get the paragraphs of text and removes last section w/ author info/ending info
        #   some articles have a "bottom-of-article" class for the author stuff and some don't for some reason
        inProcessGetParagraphs = []
        if soup.find('div', attrs={'class': 'bottom-of-article'}) != None:
            inProcessGetParagraphs = soup.find_all('div', attrs={'class': 'StoryBodyCompanionColumn'})
        else: 
            inProcessGetParagraphs = soup.find_all('div', attrs={'class': 'StoryBodyCompanionColumn'})[:-1]
        listOfEachArticleText = []
        wasItSuccessful = True 
        headlinesOfFailedArticles = []
        text = ''
        for eachText in inProcessGetParagraphs:
            getParagraphs = eachText.find_all('p')
            if getParagraphs == None:
                wasItSuccessful = False
                headlinesOfFailedArticles.append(eachText.headline)
            else:
                for paragraph in getParagraphs:
                    text = text + ' ' + paragraph.text
                    # listOfEachArticleText.append(text)
        # this part was to avoid articles which
        if wasItSuccessful == False:
            continue
        
        # Now have a list of all paragraphs - need to join together to make one string
        # fullArticleText = ' '.join(listOfEachArticleText)
        eachArticle.text = text # assigning the text property to object
        print('Got info for Article #' + str(index))
        index = index + 1

    # must close the driver after task finished
    driver.close()

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/NYT/PrelimData/'
for article in desiredNumberOfArticles:
    makeFile = open(beginningFilePath + article.headline + '.txt', 'w')
    makeFile.write(article.headline + '\n' + article.url + '\n' + article.dateString + '\n' + article.author + '\n' + article.articleType + '\n\n' + article.text)
print('Done!!!')
