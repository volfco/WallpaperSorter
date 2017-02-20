import argparse
import os
import shutil
from PIL import Image
from bs4 import BeautifulSoup
import requests
import re
import pickle

# Variables
__MINRESOLUTION = [1920, 1080]

# Functions
def download(fileName, cookie):
    name = fileName.split('/')[-1].split('?')[0]
    if os.path.exists('DLs\\' + name):
        print("Already Exists.")
        return

    r = requests.get(fileName, allow_redirects=True, stream=True, cookies=cookie)
    with open('DLs\\' + name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("--collection")

    args = parser.parse_args()

    if args.username is None:
        print("Need a username")
        exit()

    if args.collection is None:
        COLLECTION = ["?catpath=/", "0"]
    else:
        COLLECTION = [args.collection, args.collection]

    URL = "http://{0}.deviantart.com/favourites/{1}".format(args.username, COLLECTION[0])

    # Get the initial page
    Req = requests.get(URL, allow_redirects=True)
    __HTML = Req.text

    REQUESTID = re.findall(r'"requestid":"(.{36})",',__HTML)[0] + "-iym8qw2j-1.2"
    CSRF = re.findall(r'"csrf":"(.*)","', __HTML)[0]

    soup = BeautifulSoup(__HTML, 'html.parser')

    Links = []
    DownloadLinks = []

    # Scrape the initial page
    Soup = soup.findAll(attrs={'class': 'torpedo-thumb-link'})
    for item in Soup:
        Links.append(item.get('href'))

    # Now, loop through the API
    __CONTINUE = True
    __OFFSET = 24
    while __CONTINUE:
        print("API Depth: ", __OFFSET)

        payload = {
            'username': args.username,
            'offset': '{0}'.format(__OFFSET),
            'limit': '24',
            '_csrf': CSRF,
            'dapilid': REQUESTID
        }

        if COLLECTION[1] is 0:
            payload['catpath'] = '/'

        req = requests.post("http://www.deviantart.com/dapi/v1/collection/{0}?iid={1}&mp=2".format(COLLECTION[1], REQUESTID), data=payload,
                            cookies=Req.cookies)

        __CONTINUE = req.json()['content']['has_more']
        __OFFSET = req.json()['content']['next_offset']

        for Img in req.json()['content']['results']:
            _SOUP = BeautifulSoup(Img['html'], 'html.parser')
            _LINKS = _SOUP.findAll(attrs={'class': 'torpedo-thumb-link'})
            if _LINKS.__len__() is 1:
                Links.append(_LINKS[0].get('href'))


    print("Total Links Found:", Links.__len__())

    # Loop through each link we've found
    TOTAL_LINKS = Links.__len__()
    POS = 1

    for __link in Links:
        try:
            Request = requests.get(__link, cookies=Req.cookies)
            RequestSoup = BeautifulSoup(Request.text, 'html.parser')
            DownloadLink = RequestSoup.findAll(attrs={'class': 'dev-page-download'})
            if DownloadLink.__len__() is 1:
                # print("DL Link")
                ResContainer = DownloadLink[0].findAll(attrs={'class': 'text'})[0].text.split(' ')
                Res = [int(ResContainer[1]), int(ResContainer[3])]
                if Res[0] >= __MINRESOLUTION[0] and Res[1] >= __MINRESOLUTION[1]:
                    LinkURL = DownloadLink[0].get('href')
                    print("[{0}/{1}] {2}".format(POS, TOTAL_LINKS, LinkURL))
                    download(LinkURL, Req.cookies)
            else:
                FullSizeSoup = RequestSoup.findAll(attrs={'class': 'dev-content-full'})
                if FullSizeSoup.__len__() is 0:
                    continue
                else:
                    LinkURL = FullSizeSoup[0].get('src')
                    print("[{0}/{1}] {2}".format(POS, TOTAL_LINKS, LinkURL))
                    download(LinkURL, Req.cookies)
        except Exception as e:
            print("Exception", e, __link)

        POS += 1
