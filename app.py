import imp
import xml.etree.ElementTree as ElementTree
import unicodedata as ud
import requests
from re import sub
import urllib3
import os
urllib3.disable_warnings()
DEBUG = 0


def f_remove_accents(old):
    """
    Removes common accent characters, lower form.
    Uses: regex.
    """
    new = old.lower()
    new = sub(r'[àáâãäå]', 'a', new)
    new = sub(r'[èéêë]', 'e', new)
    new = sub(r'[ìíîï]', 'i', new)
    new = sub(r'[òóôõöő]', 'o', new)
    new = sub(r'[ùúûü]', 'u', new)
    return new


def snake_case(s):
    return f_remove_accents('_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower())


def mkdir_p(path):
    import errno
    import os
    try:
        os.makedirs(path)
    except OSError as exc:  # Python ≥ 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        # possibly handle other errno cases here, otherwise finally:
        else:
            raise


def handleDataDirPath(enclosure: dict):
    mkdir_p(f"data/{snake_case(enclosure['type'])}/{str(enclosure['year'])}")


def pprint(object):
    pass


if DEBUG == 1:
    from pprint import pprint
    f = open('example.feed', 'r+')
    lines = f.read()
else:
    lines = requests.get("https://magyarkozlony.hu/feed", verify=False).text

tree = ElementTree.fromstring(lines)
for e in tree.findall('./channel/item'):
    enc = e.find('enclosure').attrib
    pdfName = f"{enc['serial']}.pdf"
    handleDataDirPath(enc)
    if not os.path.isfile(f"data/{snake_case(enc['type'])}/{str(enc['year'])}/{pdfName}"):
        lnk = e.find('link')
        url = sub('megtekintes', 'letoltes', lnk.text)
        print(
            f"[ + ] Downloading: {snake_case(enc['type'])}/{str(enc['year'])}/{enc['serial']}")
        response = requests.get(url, verify=False)
        with open(f"data/{snake_case(enc['type'])}/{str(enc['year'])}/{pdfName}", 'wb') as f:
            f.write(response.content)
