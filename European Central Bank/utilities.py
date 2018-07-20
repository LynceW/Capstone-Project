import urllib.request
import re


def GetUrlList(year):

    url = "https://www.ecb.europa.eu/press/govcdec/mopo/" + str(year) + "/html/index.en.html"
    handle = urllib.request.urlopen(url)
    content = handle.read().decode("utf-8").replace("\n", "")
    urls = re.findall(r'<span class="doc-title"><a href="(.*?)">', content)

    urlList = []
    for url in urls:
        urlList.append("https://www.ecb.europa.eu" + url)

    return urlList


def Url2Str(url):

    handle = urllib.request.urlopen(url)
    string = handle.read().decode("utf-8")

    return string


def Str2Statement(string):

    if len(re.findall(r"<article>(.*)</article>", string, re.DOTALL)) != 0:
        statement = re.findall(r"<article>(.*)</article>", string, re.DOTALL)[0]
        statement = re.findall(r'"ecb-pressContentPubDate">.*?</.*?>(.*)', statement, re.DOTALL)[0]
    else:
        statement = re.findall(r"Monetary policy decisions</h2>(.*?)</.*?>", string, re.DOTALL)[0]

    statement = re.sub(r"</.*?>", " ", statement)
    statement = re.sub(r"<.*?>", "", statement)
    statement = statement.replace("\n", " ")
    statement = statement.strip()

    # if len(re.findall(r'"ecb-pressContentPubDate">.*?<p>(.*?)</article>', string, re.DOTALL)) != 0:
    #     statement = re.findall(r'"ecb-pressContentPubDate">.*?<p>(.*?)</article>', string, re.DOTALL)[0]
    # else:
    #     statement = re.findall(r"Monetary policy decisions</h2>(.*?)</article>", string, re.DOTALL)[0]
    # statement = statement.replace("\n", "")
    #
    return statement


def GetDate(url):

    date = url.split("/")[-1]
    date = re.findall(r"[0-9]+", date)[0]

    if int(date) > 200000:
        date = "19" + date
    else:
        date = "20" + date

    date = date[0:4] + "-" + date[4:6] + "-" + date[6:8]

    return date