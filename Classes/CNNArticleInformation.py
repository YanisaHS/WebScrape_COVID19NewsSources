from datetime import datetime
import re

class CNNArticleInformation:

    # Making article info objects
    def __init__(self, url, headline, date, text): # missing author and article type
        self.url = 'https://' + url.strip()[2:]
        self.headline = self.headlineCleaning(headline.strip())
        self.date = self.dateMaking(date.strip())
        self.text = self.textCleaning(text.strip())

        self.dateString = self.date.strftime('%B %d')
        self.author = 'unable to retrieve author' # default unless author is found in script
        self.articleType = 'News Report Article' # make default 'News Report Article' - in case it doesn't grab anything because
                                                #   of weird formatting things w/ some CNN sites (style/travel) 
                                                #        I know it is report article type if not grabbed by 'opinion'
    
    # Override printing the built-in representation so it prints/functions as normal
    # This is what will print out when I print an object of this class
    def __repr__(self):
        finalPrint = self.headline + ' ' + self.url + ' ' + str(self.date) + ' ' + (self.text[:30] + '...')
        return finalPrint

    # Making it so python parses the date directly as an actual date
    def dateMaking(self, date):
        format = '%b %d, %Y'
        finalDate = datetime.strptime(date, format)
        return finalDate

    # Clean text - remove the headings (e.g. ##Health##)
    def textCleaning(self,text):
        finalText = re.sub(r'##\S*##', '', text)
        return finalText

    def headlineCleaning(self, headline):
        finalHeadline = re.sub(r'\/', '_', headline)
        return finalHeadline

    # getting the text in between to get the author
    def authorCleaning(self, author):
        lowercaseAuthorLine = author.lower()
        indexOfBy = 0
        indexOfCommaCNN = len(author) # in case there is no "by" or ", CNN"
        if 'by' in lowercaseAuthorLine:
            indexOfBy = lowercaseAuthorLine.index('by') + 3
        if ', cnn' in lowercaseAuthorLine:
            indexOfCommaCNN = lowercaseAuthorLine.index(', cnn')
        cleanAuthor = author[indexOfBy:indexOfCommaCNN]
        self.author = cleanAuthor
