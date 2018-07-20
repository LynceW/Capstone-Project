import pandas as pd             # use Pandas to output csv file
from utilities import *         # self-made utility functions to crawl the website

statementList = []              # create empty list to store the statement and the date
dateList = []

# there are 17 pages of statements on the website. We loop over all pages to get the data
for page in range(1, 18):

    # get the urls from the current page
    urlList = GetUrlList(page)

    # loop over all urls on the current page
    for url in urlList:         

        # some certain rules to filter out useless statements
        if (len(re.findall(r".*fad-press-release.*", url)) != 0 or len(re.findall(r".*rate.*", url)) != 0):
            print(url)

            # extract the statement and the release date
            statement, date = GetReleaseAndDate(url)

            statementList.append(statement)
            dateList.append(date)

# reverse these two lists so that the data has the oldest record on top
statementList.reverse()
dateList.reverse()

# output the data
output = pd.DataFrame({"Date": dateList, "Statement": statementList})
output.to_csv("BankOfCanada.csv", index=False)