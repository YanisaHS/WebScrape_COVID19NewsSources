from urllib.request import urlopen
import time, random, re
from bs4 import BeautifulSoup as bsoup
from datetime import timedelta, date
from Classes.WSJArticleInformation import WSJArticleInformation
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# Start with running chrome driver with Selenium:
chromeDriverPath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/chromedriver'
chromeUserPathDir = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/IgnoreFiles/Chrome_User/'

chromeOptions = Options()
#chromeOptions.add_argument('--headless')
chromeOptions.add_argument('user-data-dir="' + chromeUserPathDir + '"') # Will load the user profile I already made/signed in to
webDriver = webdriver.Chrome(executable_path=chromeDriverPath, options=chromeOptions)

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 700 

pageNumber = '' # will increment below and change to 
defaultPageSize = 20 # 20 articles per page
exactArticleCount = 2441 # should be 2,441 when using live data
actualPageCount = exactArticleCount // defaultPageSize

url = 'https://www.wsj.com/search/term.html?' + \
    'KEYWORDS=coronavirus%20' + \
    'covid-2019%20' + \
    'covid-19%20' + \
    'epidemic%20' + \
    'pandemic' + \
    '&min-date=2020/01/01' + \
    '&max-date=2020/04/30' + \
    '&isAdvanced=true' + \
    '&daysback=1y' + \
    '&andor=OR' + \
    '&sort=date-desc' + \
    '&source=wsjarticle' + \
    '&page={}'.format(pageNumber) 

htmlList = []
with webDriver as driver:
    # Set timeout time 
    wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(20)
    driver.maximize_window()

    # Change url depending on page & # of articles/etc.
    # retrive url in headless browser
    for numberOfPagesToExpect in range(1, actualPageCount + 2):
        updatedURL = url + str(numberOfPagesToExpect)
        print('Working on: ' + updatedURL)
        driver.get(updatedURL)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # scrolls to the bottom of the page

        retries = 1
        while retries <= 5:
            try:
                wait.until(presence_of_element_located((By.CLASS_NAME, "article-info")))
                break
            except TimeoutException:
                driver.refresh()
                retries = retries + 1
                print('Retry #' + str(retries))
        html = driver.execute_script("return document.documentElement.outerHTML;")
        htmlList.append(html)
        time.sleep(2)

    # Loop over list to parse link to be read by beautiful soup
    firstListOfInformation = []
    for html in htmlList:
        firstSoup = bsoup(html, 'html.parser')

        # Starting w/ first div element so I can find its children & get article name, url, date, text
        firstElement = firstSoup.find_all('div', attrs={'class': 'item-container headline-item'})
        for remainingArticleInfo in firstElement:
            # Headline
            inProcessHeadline = remainingArticleInfo.find('h3', attrs={'class': 'headline'})
            headline = inProcessHeadline.text

            # URL
            inProcessURL = inProcessHeadline.find('a')
            url = inProcessURL.get('href') 

            # Date
            inProcessDate = remainingArticleInfo.find('time', attrs={'class': 'date-stamp-container'})
            date = inProcessDate.text

            # Author
            inProcessAuthor = remainingArticleInfo.find('div', attrs={'class': 'article-info'})
            author = ''
            if inProcessAuthor.find('span') != None:
                inProcessAuthorTwo = inProcessAuthor.find('span')
                author = inProcessAuthorTwo.text
            else:
                author = 'unable to retrieve author'

            # Making the info into an object from the CNN class
            putThingsInClass = WSJArticleInformation(url, headline, date, author)
            firstListOfInformation.append(putThingsInClass)

    # Generate a certain number of random articles within the list
    desiredNumberOfArticles = random.sample(firstListOfInformation, numberOfRandomSamples)

    print('Opening Selenium - getting remaining article information...')

    # Making Selenium go into the list and open the URLs
    index = 1
    for eachArticle in desiredNumberOfArticles:
        time.sleep(2)
        print('First url: ' + eachArticle.url)
        driver.get(eachArticle.url)
        time.sleep(2)
        currentURL = driver.current_url # so it opens the current url in case of redirects
        # if '-ai-' in currentURL or 'artificial-intelligence' in currentURL: # skip articles from WSJ Pro AI (in there for some reason?)
        #     print('Skipping WSJ Pro AI article')
        #     continue
        print('Got current url - getting author & article type for: ' + currentURL)
    
        # Get remaining info: article type and text
        retries = 1
        while retries < 5:
            try:
                wait.until(presence_of_element_located((By.CLASS_NAME, "article-content")))
                break
            except TimeoutException:
                driver.refresh()
                retries = retries + 1
                print('Retry #' + str(retries))
        if retries == 5: # if it has tried 5 times and STILL doesn't work, just skip it and keep going
            continue
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = bsoup(html, 'html.parser')

        # Article Type
        articleTypeSearch = soup.find_all('li', attrs={'class': 'article-breadCrumb'})
        articleType = 'News Report Article'
        for articleInfo in articleTypeSearch:
            inProcessArticleTypeText = articleInfo.text
            if inProcessArticleTypeText.lower() == 'opinion':
                articleType = 'Opinion Article'
                eachArticle.articleType = articleType
                break
        eachArticle.articleType = articleType
            
        # Text
        text = ''
        allParagraphs = soup.find('div', attrs={'class': 'article-content'})
        inProcessParagraph = allParagraphs.find_all('p')
        for eachParagraph in inProcessParagraph[:-1]:
            text = text + ' ' + eachParagraph.text.replace('\n', ' ')
        text = re.sub(r'[ ]{2,}', ' ', text)
        eachArticle.text = text
        print('Got info for Article #' + str(index))
        index = index + 1

    # must close the driver after task finished
    driver.close()

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/WSJ/PrelimData/'
for article in desiredNumberOfArticles:
    makeFile = open(beginningFilePath + article.headline + '.txt', 'w')
    makeFile.write(article.headline + '\n' + article.url + '\n' + article.dateString + '\n' + article.author + '\n' + article.articleType + '\n\n' + article.text)
print('Done!!!')
