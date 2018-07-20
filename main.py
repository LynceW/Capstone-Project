import pandas as pd             # use Pandas to output csv file
from utilities import *         # self-made utility functions to crawl the website

statementDict = {}              # create an empty dictionary to store the data

for i in range(1, 18):          # there are 17 pages of statements on the website. We loop over all pages to get the data
    page = i
    urlList = GetUrlList(page)  # get the urls from the current page

    for url in urlList:         # loop over all urls on the current page
        # some certain rules to filter out useless statements
        if (len(re.findall(r".*fad-press-release.*", url)) != 0 or len(re.findall(r".*rate.*", url)) != 0):
            print(url)
            statement, date = GetReleaseAndDate(url)      # extract the statement and the release date
            statementDict[date] = statement                  # put the data into the dictionary

# extract the keys and the values in the dictionary separately
keys = []
values = []
for key, value in statementDict.items():
    keys.append(key)
    values.append(value)

# output the data
output = pd.DataFrame(values, index=keys)
print(output.info())
output.to_csv("BankOfCanada.csv", index=True)
