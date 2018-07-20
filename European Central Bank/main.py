from utilities import *
import pandas as pd


statementList = []
dateList = []
for year in range(1999, 2019):
    urlList = GetUrlList(year)

    for url in urlList:
        print(url)
        date = GetDate(url)
        string = Url2Str(url)
        statement = Str2Statement(string)
        statementList.append(statement)
        dateList.append(date)

output = pd.DataFrame({"Date": dateList, "Statement": statementList})
output.to_csv("EuropeanCentralBank.csv", index=False)