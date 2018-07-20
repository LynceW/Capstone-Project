import pandas as pd
from utilities import *

statementDict = {}

for i in range(1, 18):
    page = i
    urlList = GetUrlList(page)

    for url in urlList:
        if (len(re.findall(r".*fad-press-release.*", url)) != 0 or len(re.findall(r".*rate.*", url)) != 0):
            print(url)
            statement, _, strDate = GetReleaseAndDate(url)
            statementDict[strDate] = statement

keys = []
values = []
for key, value in statementDict.items():
    keys.append(key)
    values.append(value)

output = pd.DataFrame(values, index=keys)
print(output.info())
output.to_csv("statements.csv", index=True)