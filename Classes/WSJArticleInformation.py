from datetime import datetime
import re

class WSJArticleInformation:

    # Making article info objects
    def __init__(self, url, headline, date, author): # missing article type & text
        self.url = 'https://www.wsj.com' + url
        self.headline = self.headlineCleaning(headline.strip())
        self.dateString = self.dateMaking(date.strip())
        self.author = self.authorCleaning(author)

        self.text = ''
        self.articleType = ''

    # Override printing the built-in representation so it prints/functions as normal
    # This is what will print out when I print an object of this class
    def __repr__(self):
        finalPrint = self.headline + ' ' + self.url + ' ' + str(self.date) + ' ' + (self.text[:30] + '...')
        return finalPrint

    # Making it so python parses the date directly as an actual date
    def dateMaking(self, date): 
        dateReplace = date.replace('.', '').replace(',', '')
        dateParts = dateReplace.split(' ')
        month = dateParts[0][:3]
        day = dateParts[1]
        finalDate = month + ' ' + day
        return finalDate

    def headlineCleaning(self, headline):
        if headline == None:
            finalHeadline = 'unable to retrieve headline'
            return finalHeadline
        else:
            finalHeadline = re.sub(r'\/', '_', headline)
            return finalHeadline

    # getting the text after by (unless null)
    def authorCleaning(self, author):
        indexOfBy = 0
        if author == None:
            cleanAuthor = 'unable to retrieve author'
            return cleanAuthor
        else:
            cleanAuthor = author.lower()
            if 'by' in cleanAuthor:
                indexOfBy = cleanAuthor.index('by') + 3
                cleanAuthor = author[indexOfBy:]
            return cleanAuthor