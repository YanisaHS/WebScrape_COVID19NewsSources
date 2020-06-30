from datetime import datetime
import re

class NYTArticleInformation:

    # Making article info objects
    def __init__(self, url, headline, date, author, articleType):
        self.url = url
        self.headline = self.headlineCleaning(headline.strip())
        self.date = self.dateMaking(date.strip())
        self.author = self.authorCleaning(author)
        self.articleType = articleType 

        self.dateString = self.date.strftime('%B %d')
        self.text = ''

    # Override printing the built-in representation so it prints/functions as normal
    # This is what will print out when I print an object of this class
    def __repr__(self):
        finalPrint = self.headline + ' ' + self.url + ' ' + str(self.date) + ' ' + (self.text[:30] + '...')
        return finalPrint

    # Making it so python parses the date directly as an actual date
    def dateMaking(self, date):
        format = '%Y-%m-%dT%H:%M:%S%z'
        finalDate = datetime.strptime(date, format)
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
            lowercaseAuthorLine = author.lower()
            if 'by' in lowercaseAuthorLine:
                indexOfBy = lowercaseAuthorLine.index('by') + 3
                cleanAuthor = author[indexOfBy:]
            return cleanAuthor