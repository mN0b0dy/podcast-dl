import os
import sys
import pycurl
import requests
from tqdm import tqdm

import httpx
import asyncio
import atexit
from pathlib import Path
import click


def make_loop():
    loop = asyncio.get_event_loop()
    atexit.register(loop.close)
    return loop

def make_http(loop):
    http = httpx.AsyncClient(follow_redirects=True)
    atexit.register(lambda: loop.run_until_complete(http.aclose()))
    return http

loop = make_loop()
http = make_http(loop)

def async_download(url, outfile):
    outfile = Path(outfile)
    async def download(http: httpx.AsyncClient):
        #click.secho(f"Getting episode: {str(url)}")
        async with http.stream("GET", url) as response:
            size = int(response.headers.get('content-length', 0)) or None
            dark_green = "\033[1;32;40m"
            bar_format = f"{dark_green}"
            bar_format += '{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{rate_fmt}{postfix}]'
            p_bar = tqdm(total=size, unit='iB', unit_scale=True, bar_format=bar_format)
            await _save_atomic(response, p_bar)
            p_bar.close()
            sys.stdout.write("\033[F") # Cursor up one line
            sys.stdout.write("\033[K")
            sys.stdout.flush()
        click.secho(f"    [DONE] {outfile}", fg="green")

    async def _save_atomic(response, p_bar):
        partial_filename = outfile.with_suffix(".partial")
        with partial_filename.open("wb") as fp:
            async for chunk in response.aiter_bytes():
                p_bar.update(len(chunk))
                fp.write(chunk)
        partial_filename.rename(outfile)
    
    loop.run_until_complete(download(http)) 

def pycurl_download(url, outfile, total_size=0):
    # create a progress bar and update it manually
    if not total_size:
        with open(outfile, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            # follow redirects:
            c.setopt(c.FOLLOWLOCATION, True)
            # custom progress bar
            c.setopt(c.NOPROGRESS, False)
            c.perform()
            c.close()
    else:
        with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
            # store dotal dl's in an array (arrays work by reference)
            total_dl_d = [0]
            def status(download_t, download_d, upload_t, upload_d, total=total_dl_d):
                # increment the progress bar
                pbar.update(download_d - total[0])
                # update the total dl'd amount
                total[0] = download_d

            # download file using pycurl
            with open(outfile, 'wb') as f:
                c = pycurl.Curl()
                c.setopt(c.URL, url)
                c.setopt(c.WRITEDATA, f)
                # follow redirects:
                c.setopt(c.FOLLOWLOCATION, True)
                # custom progress bar
                c.setopt(c.NOPROGRESS, False)
                c.setopt(c.XFERINFOFUNCTION, status)
                c.perform()
                c.close()

