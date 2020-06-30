from datetime import datetime
import re

class TheBlazeArticleInformation:  

    # Making article info objects
    def __init__(self, url, headline, date, author, articleType, text):
        self.url = url
        self.headline = self.headlineCleaning(headline.strip())
        self.date = self.dateCleaning(date.strip())
        self.author = author.strip()
        self.articleType = articleType
        self.text = self.textCleaning(text)

    # Override printing the built-in representation so it prints/functions as normal
    # This is what will print out when I print an object of this class
    def __repr__(self):
        finalPrint = self.headline + '\n' + self.url + '\n' + self.date + '\n' + \
            self.author + '\n' + self.articleType + '\n' + self.text#[:30] + '...')
        return finalPrint

    def headlineCleaning(self, headline):
        finalHeadline = re.sub(r'\/', '_', headline)
        finalHeadline = re.sub(r'\s+', ' ', finalHeadline)
        return finalHeadline
    
    def dateCleaning(self, date): 
        finalDate = date.replace(', 2020', '')
        return finalDate

    def textCleaning(self, text):
        finalText = re.sub(r'\s+', ' ', text)
        return finalText