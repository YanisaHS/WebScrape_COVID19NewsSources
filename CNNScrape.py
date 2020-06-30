# This file will search every article in CNN that has at least one of our five key terms: 
#   Covid-19, Covid-2019, Coronavirus, Pandemic, Epidemic
# Next, it will extract the headline, url, date, and text information
#   CNN stores text on the main page, so it isn't necessary to actually open up those links
# Then, it counts how many articles there are, and selects random articles to store
#   The number of random articles is selected based on how many we want to incorporate in our analysis
# Last, it creates individual files for each article, using the headline as the article title

# Ones that have the word 'byline': US, World, Politics, Business, Opinion, Health, Entertainment
# Ones that do not have 'byline': Style('Authors__writers'), Travel('Article__subtitle') - (include /style/ and /travel/ after cnn.com)

# Before using, MUST CHANGE: exactArticleCount (to match when searching CNN) & Random Sample #

from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup
from datetime import datetime
import random
from Classes.CNNArticleInformation import CNNArticleInformation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time

# Start with running chrome driver with Selenium:
chromeDriverPath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/chromedriver'

chromeOptions = Options()
chromeOptions.add_argument('--headless')
webDriver = webdriver.Chrome(executable_path=chromeDriverPath, options=chromeOptions)

# Counting how many pages there will be based on the number of articles (must do manually)
defaultPageSize = 100
exactArticleCount = 3197 # ******Change for each term******* Make sure to only search "Stories"
actualPageCount = exactArticleCount // defaultPageSize

# Specifying how many random articles I will want it to sample
numberOfRandomSamples = 300

htmlList = []
# If changing page size in URL, change it above, and change keyword below
keyword = 'epidemic'
url = 'https://www.cnn.com/search?size={}&q={}&sort=newest&type=article'.format(defaultPageSize, keyword)
with webDriver as driver:
    # Set timeout time 
    wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(30)
    driver.maximize_window()

    # Change url depending on page & # of articles/etc.
    # retrive url in headless browser
    for numberOfPagesToExpect in range(1, (actualPageCount + 1)):
        updatedURL = url + '&page=' + str(numberOfPagesToExpect) + '&from=' + str(numberOfPagesToExpect * defaultPageSize - defaultPageSize)
        if numberOfPagesToExpect == 1:
            updatedURL = url + '&page=' + str(numberOfPagesToExpect)
        print('Working on: ' + updatedURL)
        driver.get(updatedURL)

        wait.until(presence_of_element_located((By.CLASS_NAME, "cnn-search__result-publish-date")))
        html = driver.execute_script("return document.documentElement.outerHTML;")
        htmlList.append(html)
        time.sleep(2)

    # Loop over list to parse link to be read by beautiful soup
    firstListOfInformation = []
    for html in htmlList:
        firstSoup = bsoup(html, 'html.parser')

        # Starting w/ first div element so I can find its children & get article name, url, date, text
        firstElement = firstSoup.find_all('div', attrs={'class': 'cnn-search__result cnn-search__result--article'})
        for remainingArticleInfo in firstElement:
            # Headline
            inProcessHeadline = remainingArticleInfo.find('h3', attrs={'class': 'cnn-search__result-headline'})
            headline = inProcessHeadline.text

            # URL
            inProcessURL = inProcessHeadline.find('a')
            url = inProcessURL.get('href')
            # Removing unrelated articles/ones that aren't v helpful for this project
            # According to CNN, "CNN News staff is not involved" w/ CNN Underscored
            if 'live-news' in url or 'cnn10' in url or 'cnn-underscored' in url:
                continue

            # Date
            inProcessDate = remainingArticleInfo.find('div', attrs={'class': 'cnn-search__result-publish-date'})
            date = inProcessDate.text

            # Text
            inProcessText = remainingArticleInfo.find('div', attrs={'class': 'cnn-search__result-body'})
            text = inProcessText.text

            # Making the info into an object from the CNN class
            putThingsInClass = CNNArticleInformation(url, headline, date, text)
            # Specifying date range between Jan 1, 2020 and Apr 30, 2020
            if putThingsInClass.date >= datetime(2020, 1, 1) and putThingsInClass.date <= datetime(2020, 4, 30):
                firstListOfInformation.append(putThingsInClass)

    # Generate a certain number of random articles within the list
    desiredNumberOfArticles = random.sample(firstListOfInformation, numberOfRandomSamples)

    print('Opening Selenium - getting article information...')

    # Making Selenium go into the list and open the URLs
    index = 1
    for eachArticle in desiredNumberOfArticles:
        time.sleep(2)
        print('First url: ' + eachArticle.url)
        driver.get(eachArticle.url)
        time.sleep(2)
        currentURL = driver.current_url # so it opens the current url in case of redirects
        print('Got current url - getting author & article type for: ' + currentURL)
        if 'live-news' in currentURL or 'cnn10' in currentURL or 'cnn-underscored' in currentURL:
            continue
        
        # Getting byline based on type of CNN article (they differ between article sections)
        # CNN Style
        if '/style/' in currentURL:
            wait.until(presence_of_element_located((By.CSS_SELECTOR, '.Authors__writer, .special-article')))
            html = driver.execute_script("return document.documentElement.outerHTML;")
            soup = bsoup(html, 'html.parser')
            authorByline = soup.find('span', attrs={'class': 'Authors__writer'})
            if authorByline == None:
                # Author
                author = 'No Author'
                articleType = 'News Report Article'
            else:
                author = authorByline.text
                eachArticle.authorCleaning(author)

                # Article Type
                if 'opinion' in author.lower():
                    articleType = 'Opinion Article'
                    eachArticle.articleType = articleType
                else:
                    articleType = 'News Report Article' 
                    eachArticle.articleType = articleType             
        
        # CNN Travel
        elif '/travel/' in currentURL: 
            wait.until(presence_of_element_located((By.CLASS_NAME, 'Article__subtitle')))
            html = driver.execute_script("return document.documentElement.outerHTML;")
            soup = bsoup(html, 'html.parser')
            authorByline = soup.find('div', attrs={'class': 'Article__subtitle'})
            if authorByline == None:
                # Author
                author = 'No Author'
                articleType = 'News Report Article'
            else:
                author = authorByline.text
                eachArticle.authorCleaning(author)

                # Article Type
                if 'opinion' in author.lower():
                    articleType = 'Opinion Article'
                    eachArticle.articleType = articleType
                else:
                    articleType = 'News Report Article' 
                    eachArticle.articleType = articleType   
        
        # All other CNN types (US, World, Politics, Business, Opinion, Health, Entertainment)
        else:
            wait.until(presence_of_element_located((By.CLASS_NAME, 'metadata'))) #(By.CSS_SELECTOR, 'p[class*="byline" i]')))
            html = driver.execute_script("return document.documentElement.outerHTML;")
            soup = bsoup(html, 'html.parser')
            authorByline = soup.find('span', attrs={'class': 'metadata__byline__author'})
            if authorByline == None:
                # Author
                author = 'No Author'
                articleType = 'News Report Article'
            else:
                author = authorByline.text
                eachArticle.authorCleaning(author)

                # Article Type
                if 'opinion' in author.lower():
                    articleType = 'Opinion Article'
                    eachArticle.articleType = articleType
                else:
                    articleType = 'News Report Article' 
                    eachArticle.articleType = articleType   
            
        print('Got info for Article #' + str(index))
        index = index + 1
    
    # must close the driver after task finished
    driver.close()

# Save them as individual .txt files
beginningFilePath = '/Users/yanisa/GoogleDrive/Publications_Conferences/Code/2020.CovidMetaphorMetonymyBookChptCollab/FinalData/CNN/PrelimData/'
for article in desiredNumberOfArticles:
    makeFile = open(beginningFilePath + article.headline + '.txt', 'w')
    makeFile.write(article.headline + '\n' + article.url + '\n' + article.dateString + '\n' + article.author + '\n' + \
            article.articleType + '\n\n' + article.text)
print('Done!!!')

# BEFORE RUNNING!!!
#   1. Is the page size (e.g. 10 or 100) what you want?
#   2. Did you change the exact article count? (actually search on CNN and input the number of search results)
#   3. Did you change the keyword?
#   4. Are you sampling the correct amount? (currently taking 300 of each, then will take 300 of that total)
#   5. Is the destination file correct?
#   6. Is the date range correct?
# (Keywords) Go in this order:
#   covid-19, covid-2019, coronavirus, pandemic, epidemic
