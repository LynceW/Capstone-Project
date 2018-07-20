import urllib.request
import re


'''
function GetUrlList:
to get all the statement urls on a search result page. The parameter "year" is the year of statements we want
'''
def GetUrlList(year):
    
    url = "https://www.ecb.europa.eu/press/govcdec/mopo/" + str(year) + "/html/index.en.html"       # the url of ecb website
    handle = urllib.request.urlopen(url)                                        # open the url
    content = handle.read().decode("utf-8").replace("\n", "")                   # read the url and convert it to string
    urls = re.findall(r'<span class="doc-title"><a href="(.*?)">', content)     # find all useful urls using regular expression

    # for all urls, add a prefix to make it complete
    urlList = []
    for url in urls:
        urlList.append("https://www.ecb.europa.eu" + url)

    return urlList


'''
function Url2Str:
read the url and convert the content into a string
'''
def Url2Str(url):

    handle = urllib.request.urlopen(url)        # open the url
    string = handle.read().decode("utf-8")      # read it and decode it to string (utf-8 mode)

    return string


'''
function Str2Statement:
extract the statement out of the content
'''
def Str2Statement(string):
    
    # use regular expression to extract the statement
    if len(re.findall(r"<article>(.*)</article>", string, re.DOTALL)) != 0:
        statement = re.findall(r"<article>(.*)</article>", string, re.DOTALL)[0]
        statement = re.findall(r'"ecb-pressContentPubDate">.*?</.*?>(.*)', statement, re.DOTALL)[0]
    else:
        statement = re.findall(r"Monetary policy decisions</h2>(.*?)</.*?>", string, re.DOTALL)[0]
    
    # delete all the html tags
    statement = re.sub(r"</.*?>", " ", statement)
    statement = re.sub(r"<.*?>", "", statement)
    
    # delete all the newlines
    statement = statement.replace("\n", " ")
    
    # delete all the whitespaces at the begining and end of the statement
    statement = statement.strip()

    return statement


'''
function GetDate:
extract the publication date from the url
'''
def GetDate(url):
    
    date = url.split("/")[-1]                   # split the url by "-"
    date = re.findall(r"[0-9]+", date)[0]       # extract the part with numbers in it, which is the one that contains date
    
    # convert the 6-digit date into 8-digit. e.g. 180720 -> 20180720
    if int(date) > 200000:
        date = "19" + date
    else:
        date = "20" + date
    
    date = date[0:4] + "-" + date[4:6] + "-" + date[6:8]    # add "-" in between

    return date
