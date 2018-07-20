import urllib.request
import re


def GetUrlList(page):
    page = str(page)
    url = "https://www.bankofcanada.ca/press/press-releases/?mtf_search=overnight%2Brate%2Btarget&mt_orderby=0&location%5B%5D=1509&mt_page="
    url = url + page

    handle = urllib.request.urlopen(url)
    result = handle.read().decode('utf-8')
    result = re.findall(r'<a href="(.*?)" data-content-type="Press Releases', result)

    return result


def Url2Str(url):
    handle = urllib.request.urlopen(url)
    string = handle.read().decode('utf-8')

    return string


def CleanStr(string):

    string = string.replace('\n', '')
    string = re.findall(r"<span class='post-content'>(.*)</span>", string)
    string = string[0].replace("\r", '')
    string = re.sub(r"(<.*?>)", "", string)
    string = string.strip()
    string = re.findall(r".*\.", string)[0]

    return string


def GetDate(string):

    date = re.findall(r'meta name="publication_date" content="(.*)"', string)[0]
    strDate = date
    date = tuple(date.split('-'))
    year, month, day = date
    year = int(year)
    month = int(re.findall(r"^0?(.*)$", month)[0])
    day = int(re.findall(r"^0?(.*)$", day)[0])

    return (year, month, day), strDate


def GetReleaseAndDate(url):

    string = Url2Str(url)
    release = CleanStr(string)
    date, strDate = GetDate(string)

    return release, date, strDate