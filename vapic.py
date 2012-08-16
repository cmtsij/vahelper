#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import defaultencoding
import htmltool
import cjk
import urllib,urllib2
import re
import getopt
import shutil
from collections import Counter
import hashlib


def get_web_content_with_cache(url,debug=False):
    cache_hash=hashlib.md5(url).hexdigest()[0:8]
    path="/tmp/vahelper/cache"
    file=os.path.join(path,cache_hash)
    try:
        os.makedirs(path)
    except:
        pass

    #read_cache_content
    if(os.path.isfile(file)):
        with open(file,"rb") as f:
            if debug: 
                printu("read from cache file: "+file)
            return f.read()

    #read from internet
    headers = { 'User-Agent' : 'Mozilla/5.0' }	# google banned unvalid user-agent.
    html_request = urllib2.Request(url, None, headers)
    web_content=urllib2.urlopen(html_request).read()

    #write_cache_content
    with open(file,"wb+") as f:
        f.write(web_content)
    
    return web_content


def get_google_content_pic_search(keyword,urlbase="https://www.google.com/search?",width=800,height=500,debug=False):
    '''
    return the html content in unicode
    '''
    get=urllib.urlencode( { 'q': keyword,
                        'ie' : "utf-8",
                        'oe' : "utf-8",
                        'safe': "off",  #child protect
                        'filter': "1",  #duplicate filter
                        'num': "20",     #count
                        'tbm': "isch",  #image search
                        'biw': "%s"%width,      # image width
                        'bih': "%s"%height,     # image height
                        'sa' : "N",
                        'tab': "wi",
                        'hl' : "zh-TW",
                        'um' : "1",
                       })
    
    html_content=get_web_content_with_cache(urlbase+get,debug);
    html_content=html_content.decode("utf-8")

    return html_content



def get_vaid(string):
    vaid=string
    vaid_match=re.search(r"([a-zA-Z]+[-]?\d+)",string,re.IGNORECASE)
    if vaid_match is not None:
        vaid=vaid_match.group(1)
    return vaid
    

def get_vapic(keyword,path=os.path.abspath(os.path.curdir.decode()),num=3,height=800,width=600,verbose=False,debug=False):
    html=get_google_content_pic_search(keyword,debug=debug)
    #html=html.lower()
    html=htmltool.decode_entity(html)
    html=htmltool.remove_tags(html,repl="||")
    #html=htmltool.clean_tags(html,repl="||")
    if debug:
        printu(html)
    
    imgurls=re.findall("imgurl=([^&]*?.jpg)", html, flags=re.I)
    
    
    
    for url in imgurls:
        if debug:
            printu(url)
        
        content=None
        try:
            content=get_web_content_with_cache(url)
            if not content:
                continue
            filepath=os.path.join(path,os.path.basename(url))
            with open(filepath,"wb+") as f:
                f.write(content)
                printu("[%-32s] <= [%-64s]"%(os.path.relpath(filepath),url))
                num=num-1
                if num == 0:
                    return
        except urllib2.HTTPError as e:
            printu("%s: %s"%(str(e),url))
        except Exception as e:
            printu("Error:%s: %s: %s"%(type(e),str(e),url))
            #printu("un%s: %s"%(e.strerror,url))
        
def printu(unistr):
    print unistr.encode()


def usage():
    printu( 
"""
Usage: 
    -k keyword | --keyword=keyword    # Kerword to query
    -p path    | --path=path          # Path to query
    -n num     | --num=num            # number of image to download
    -h pixel   | --height=pixel       # height pixel of image
    -w pixel   | --width=pixel        # width pixel of image
    -d         | --debug              # Dump html and stop process
    -v         | --verbose            # verbose
"""
)
    
def main():
    #html=open("out").read().decode("utf=8")
    ## handle parameter
    try:
        options,nonoptions = getopt.getopt(sys.argv[1:],"k:p:n:h:w:dv",["keyword=","path=","num=","height=","width=","debug","verbose"])
    except getopt.GetoptError as e:
        # print help information and exit:
        printu("Error: "+str(e)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    opts={  "keyword":None,
            "path":None,
            "num":2, 
            "height":0,
            "width":0,
            "debug":False,
            "verbose":False,
        }
    for opt,arg in options:
        if opt in ("-k","--keyword"):
            opts["keyword"]=arg.decode()
        if opt in ("-p","--path"):
            upath=os.path.normpath(arg.decode(sys.getdefaultencoding()))
            rpath=upath.encode()
            if os.path.exists(rpath) and (os.path.isdir(rpath) or os.path.isfile(rpath)):
                opts["path"]=os.path.abspath(rpath)
            else:
                printu("Error path:"+upath)
                sys.exit(1)
        if opt in ("-n","--num"):
            opts["num"]=int(arg.decode())
        if opt in ("-h","--height"):
            opts["height"]=int(arg.decode())
        if opt in ("-w","--width"):
            opts["width"]=int(arg.decode())
        if opt in ("-d","--debug"):
            opts["debug"]=True
        if opt in ("-v","--verbose"):
            opts["verbose"]=True

    if opts["width"]==0 and opts["height"]==0 :
        opts["width"]=533;
        opts["height"]=800;
    elif opts["width"]==0:
        opts["width"]=opts["height"]*800/533
    elif opts["height"]==0:
        opts["height"]=opts["width"]*533/800
    if opts["path"]:
        vaid=opts["keyword"] if opts["keyword"] else get_vaid(os.path.basename(opts["path"]))
        printu(vaid)
        get_vapic(vaid,path=opts["path"], num=opts["num"], verbose=opts["verbose"], debug=opts["debug"])
    else:
        usage()
        
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
    	pass
    	
'''
def get_match(str1,str2):
    s=difflib.SequenceMatcher(None,str1,str2)
    return s.get_matching_blocks()
'''
