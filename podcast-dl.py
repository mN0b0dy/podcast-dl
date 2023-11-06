#!/usr/bin/env python3
import os
import sys
import xml
from lxml import etree
from datetime import datetime
import dateutil
from click import secho
import re
from dateutil.parser import parse as dtparser
from bs4 import BeautifulSoup as bs
from pathlib import Path

from const import *
#from downloaders import pycurl_download as download
from downloaders import async_download as download
from mp3 import tagmp3

DEBUG=0

inpf = sys.argv[1]
outdir = Path(inpf).with_suffix("").name.strip().replace(" ", "_")
Path(f'./{outdir}/mp3').mkdir(parents=True, exist_ok=True)
Path(f'./{outdir}/img').mkdir(parents=True, exist_ok=True)
Path(f'./{outdir}/txt').mkdir(parents=True, exist_ok=True)
#outdir += "/"

data = None
with open(inpf, 'rb') as fp:
    data = fp.read()

tree = etree.XML(data)
abortif('tree is None')
elems = tree[0]
abortif('elems.tag != "channel"', 0)
ns = tree.nsmap

def getel_noabort(el: str, parent=elems):
    ret = parent.xpath(el, namespaces=ns)
    return ret

def getel(el: str, parent=elems):
    ret = parent.xpath(el, namespaces=ns)
    abortif("ret is None")
    abortif(f"len(ret) == 0 # {el} -> {parent} || ret -> {ret}")
    return ret[0]

def gets(child: str, parent: str):
    return getel(child, getel(parent))
# print(f'{gets("itunes:name", "itunes:owner").text}')

def getitems(root=elems):
    ret = root.xpath("//item")
    #globals()['ret'] = ret
    abortif('ret is None')
    return ret
    
'''
    Podcast Info
'''
title = getel("title").text
print(f"Title: {title}")
author = getel(KEY_AUTHOR).text
print(f"Author: {author}")
owner = getel(KEY_NAME, getel(KEY_OWNER)).text
if owner != author:
    print(f"Owner: {owner}")
categ = getel(KEY_CATEGORY)
print(f'Category: {categ.get("text")}')
podimg_url = getel(KEY_IMAGE).get('href')
if DEBUG:
    print(f'Image: {podimg_url}')
description = getel("description").text
print(f'Description:\n{description}\n')

img_main = f"{outdir}/img/main_image.jpg"
download(podimg_url, img_main)

desc = f'''Title: {title}
Author: {author}
Owner: {owner}
Image: {img_main}
Remote image: {podimg_url}

Description: \n\n{description}\n
'''
with open(f"{outdir}/txt/main_description.txt", "w") as fp:
    fp.write(desc)

'''
    Podcast Episodes
'''
# anonymous class :P
files = type("", (), { \
    "__init__": (lambda self, **kwargs: self.__dict__.update(kwargs)), \
    "__eq__": (lambda self, other: self.__dict__ == other.__dict__) } \
)(mp3=[], img=[], txt=[])

items = getitems()
extra_count = 0
no_extra = False
for item in reversed(items):
    is_extra = False
    ep_index = getel_noabort(KEY_EPISODE_NO, item)
    if len(ep_index) == 0:
        ep_index = f'{extra_count:03d}'
        extra_count += 1
        is_extra = True
    if not is_extra:
        ep_type = getel_noabort(KEY_EPISODE_TYPE, item)
        if len(ep_type) > 0:
            ep_type = ep_type[0].text.strip()
            if ep_type != "full":
                ep_index = f'{extra_count:03d}'
                extra_count += 1
                is_extra = True
    if DEBUG:
        if is_extra:
            ep_title = getel_noabort(KEY_TITLE, item)
            if len(ep_title) == 0:
                ep_title = getel("title", item).text
            else:
                ep_title = ep_title[0].text
            print(f'Found Extra episode: [{ep_type}] {ep_index} - {ep_title}')

if extra_count == len(items):
    no_extra = True

i=0
for item in getitems():
    print("")
    ep_title = getel_noabort(KEY_TITLE, item)
    if len(ep_title) == 0:
        ep_title = getel("title", item).text
    else:
        ep_title = ep_title[0].text

    ep_index = getel_noabort(KEY_EPISODE_NO, item)
    is_extra = False
    if len(ep_index) == 0:
        ep_index = f'{extra_count:03d}'
        extra_count -= 1
        if not no_extra:
            is_extra = True
    else:
        ep_index = f'{int(ep_index[0].text):03d}'
    if not (no_extra or is_extra):
        ep_type = getel_noabort(KEY_EPISODE_TYPE, item)
        if len(ep_type) > 0:
            ep_type = ep_type[0].text.strip()
            if ep_type != "full":
                ep_index = f'{extra_count:03d}'
                extra_count -= 1
                is_extra = True

    if DEBUG:
        print(f'{ep_index} - {ep_title}')

    ep_duration = getel(KEY_DURATION, item).text
    if DEBUG:
        print(f'    Duration: {minutes(ep_duration)}')
    
    ep_date = getel("pubDate", item).text
    if DEBUG:
        print(f'    Date: {ep_date}')
    fmtdate = dtparser(ep_date).strftime('%Y%m%d_%H%M%S')
    #print(f'    Date: {fmtdate}')
    
    ep_author = getel_noabort(KEY_AUTHOR, item)
    if len(ep_author) == 0:
        ep_author = getel_noabort("author", item)
        if len(ep_author) > 0:
            ep_author = ep_author[0].text
        else:
            ep_author = getel_noabort("creator", item)
            if len(ep_author) > 0:
                ep_author = ep_author[0].text
            else:
                ep_author = author
    else:
        ep_author = ep_author[0].text

    if DEBUG:
        print(f'    Author: {ep_author}')

    ep_image = getel_noabort(KEY_IMAGE, item)
    img_dlurl = None
    if len(ep_image) != 0:
        img_dlurl = ep_image[0].get('href')
        if DEBUG:
            print(f'    Image: {img_dlurl}')

    ep_enclosure = getel("enclosure", item)
    if ep_enclosure is None:
        print(f"[x] No download link for episode: {ep_index} - {ep_title}")
    ep_dlurl = ep_enclosure.get("url")
    ep_fsize = ep_enclosure.get("length")
    if not ep_dlurl:
        print(f"[x] No download link for episode: {ep_index} - {ep_title}")
    if (len(ep_dlurl)):
        if DEBUG:
            print(f'    Download: {ep_dlurl}')
        pass

    ep_description = getel("description", item).text
    #print(f'\n{ep_description}')
    soup = bs(ep_description, 'html.parser')
    ep_desc = soup.text
    if DEBUG:
        print(f'    Description: {ep_desc}')
        pass

    _ep_title = ''.join(x for x in ep_title.split(f"{title}...")).strip()
    _ep_title = _ep_title.replace(" ", "_")
    clean = re.sub(r"[/\\?%*:|\"<>&]", "-", _ep_title)
    _ep_title = clean
    ep_fmt = f'{ep_index}_{_ep_title}_{fmtdate}'
    if DEBUG:
        print(f"    Episode: {ep_fmt}")
        print("")
    else:
        secho(f"Episode: {ep_fmt}", fg='blue')
    if is_extra:
        ep_fmt = "Extra_" + ep_fmt

    # Episode Audio
    ep_filename = f"{outdir}/mp3/ep{ep_fmt}_audio.mp3"
    is_new = False
    files.mp3.append(ep_filename)
    if not os.path.isfile(ep_filename):
        download(ep_dlurl, ep_filename)
    else:
        sz = os.stat(ep_filename).st_size
        if int(sz) < int(ep_fsize):
            secho(f"    RE-DOWNLOADING (local:{sz} VS remote:{ep_fsize})", fg='yellow')
            download(ep_dlurl, ep_filename)
            is_new = True
        else:
            if DEBUG:
                secho(f"    [EXISTS] {os.path.basename(ep_filename)} ({sz}/{ep_fsize})", fg='yellow')
            else:
                secho(f"    [OK] {os.path.basename(ep_filename)}", fg='green')

    # Episode Image
    epimg_filename = f'{outdir}/img/ep{ep_fmt}_image.jpg'
    files.img.append(epimg_filename)
    if img_dlurl:
        if not os.path.isfile(epimg_filename):
            download(img_dlurl, epimg_filename)
        else:
            if DEBUG:
                secho(f'    [EXISTS] {os.path.basename(epimg_filename)}', fg='yellow')
            else:
                secho(f'    [OK] {os.path.basename(epimg_filename)}', fg='green')
    else:
        print(f"[x] No image for episode: {ep_fmt}")
    
    # Episode Description
    epdesc_filename = f'{outdir}/txt/ep{ep_fmt}_description.txt'
    files.txt.append(epdesc_filename)
    desc = f'Title: {ep_title}\nAuthor: {ep_author}\n'''
    desc += f'Remote mp3: {ep_dlurl}\n'
    if img_dlurl:
        desc += f'Remote image: {img_dlurl}\nImage: {epimg_filename}\n'
    desc += f'Audio: {ep_filename}\n'
    desc += f'Duration: {minutes(ep_duration)}\nDate: {ep_date}\n'
    desc += f'Description: \n\n{ep_desc}\n'
    if not os.path.isfile(epdesc_filename):
        with open(epdesc_filename, 'w') as fp:
            fp.write(desc)
        secho(f'    [DONE] {os.path.basename(epdesc_filename)}', fg='green')
    else:
        secho(f'    [OK] {os.path.basename(epdesc_filename)}', fg='green')

    # Tag mp3 audio
    if is_new:
        tagmp3(ep_filename, title=ep_title, front_img=img_main, track_id=ep_index, cmt=ep_desc)

    i += 1
    if DEBUG:
        if i==4:
            break
# EOF
