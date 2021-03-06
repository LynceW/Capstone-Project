import urllib.request
import re

'''
function GetUrlList:
Get a list of all urls on a certain page of the search result
'''
def GetUrlList(page):

    # set the url to the search result
    page = str(page)
    url = "https://www.bankofcanada.ca/press/press-releases/?mtf_search=overnight%2Brate%2Btarget&mt_orderby=0&location%5B%5D=1509&mt_page="
    url = url + page

    handle = urllib.request.urlopen(url)                                                # open the website
    result = handle.read().decode('utf-8')                                              # read the contents on the web page
    result = re.findall(r'<a href="(.*?)" data-content-type="Press Releases', result)   # use regular expression to extract
                                                                                        # all useful urls
    return result

'''
function Url2Str:
read the content on the url and convert it to string
'''
def Url2Str(url):

    handle = urllib.request.urlopen(url)        # open the web page
    string = handle.read().decode('utf-8')      # read the content and convert it to string

    return string


'''
function Str2Statement:
extract the statement out of the url content
'''
def Str2Statement(string):

    # use regular expression to clean the string and extract the statement
    string = string.replace('\n', '')
    string = re.findall(r"<span class='post-content'>(.*)</span>", string)[0]
    string = string.replace("\r", '')
    string = re.sub(r"(<.*?>)", "", string)
    string = string.strip()
    string = re.findall(r".*\.", string)[0]
    statement = re.sub(r"[^a-zA-Z0-9,.\s/]", '', string)

    return statement


'''
function GetDate:
extract the date out of the url content
'''
def GetDate(string):

    # use regular expression to extract the publication date of the statement
    date = re.findall(r'meta name="publication_date" content="(.*)"', string)[0]

    return date


'''
function GetReleaseAndDate:
a composite functio to get both statement data and publication date
'''
def GetReleaseAndDate(url):

    string = Url2Str(url)                # read the content and put it into string
    statement = Str2Statement(string)    # extract the statement
    date = GetDate(string)               # extract the date

    return statement, date
