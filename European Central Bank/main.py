'''
This is a web crawling program that collects European Central Bank's monetary policy decision data.
'''
from utilities import *         # self-made functions to perform scrapping
import pandas as pd             # use pandas to output csv file


statementList = []              # create empty list to store statements and dates
dateList = []

for year in range(1999, 2019):          # the records are from 1999 to 2018
    urlList = GetUrlList(year)          # get a list of all urls

    for url in urlList:                     # loop over all urls on the list
        print(url)                          # print the url to track the progress
        date = GetDate(url)                 # extract the publication date
        string = Url2Str(url)               # convert the url content to string
        statement = Str2Statement(string)   # extract the statement
        statementList.append(statement)     # add the statement and the date
        dateList.append(date)               # to the list

output = pd.DataFrame({"Date": dateList, "Statement": statementList})       # output the data as .csv file
output.to_csv("EuropeanCentralBank.csv", index=False)
