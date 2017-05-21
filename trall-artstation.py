import requests
import math
import piexif
import os


def download(fileName, cookie):
    name = fileName.split('/')[-1].split('?')[0]
    path = 'DLs\\' + name
    if os.path.exists(path):
        print("Already Exists.")
        return

    r = requests.get(fileName, allow_redirects=True, stream=True, cookies=cookie)
    with open(path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    return path


def writeEXIF(obj, path):
    fullName = obj['full_name']
    pass

args = None
URL = "https://www.artstation.com/artist/user/profile"

Req = requests.get(URL)

# Get all URLs
__CONTINUE = True
__PAGE = 1
__TOTAL_PAGES = -1
__TOTAL_ASSETS = 0
__IGNORE_RATIO = 1.5    # Ignore any Images below this ratio
__CURRENT = 0

while __CONTINUE:
    page = requests.get("https://www.artstation.com/users/{0}/likes.json?page={1}".format('user', __PAGE),
                        cookies=Req.cookies)
    payload = page.json()

    if __TOTAL_PAGES is -1:
        __TOTAL_PAGES = round(payload['total_count'] / 50)
        __TOTAL_ASSETS = payload['total_count']

    if __TOTAL_PAGES is __PAGE:
        __CONTINUE = False
        break
    else:
        __PAGE += 1

    print("Page: ", __PAGE)

    for _element in payload['data']:
        if _element['assets_count'] > 1:
            print("Multi-Asset")
            # We need additional processing
            id = _element['hash_id']
            projPage = requests.get("https://www.artstation.com/projects/{0}.json".format(id), cookies=Req.cookies)
            projResp = projPage.json()
            for _asset in projResp['assets']:
                print("[{0}/{1}] {2}".format(__CURRENT, __TOTAL_ASSETS, _asset['image_url']))
                path = download(_asset['image_url'], projPage.cookies)
                writeEXIF(projResp['user'], path)
        else:
            rawUrl = _element['cover']['medium_image_url']
            fullUrl = rawUrl.replace('/medium/', '/large/')
            print("[{0}/{1}] {2}".format(__CURRENT, __TOTAL_ASSETS, fullUrl))
            path = download(fullUrl, Req.cookies)
            writeEXIF(_element['user'], path)

        __CURRENT += 1

# .findAll(attrs={'class':'project-image'
#
#