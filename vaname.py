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


def get_google_content(keyword,urlbase="https://www.google.co.jp/search?",debug=False):
    '''
    return the html content in unicode
    '''
    get=urllib.urlencode( { 'q': keyword,
                        'ie' : "utf-8",
                        'oe' : "utf-8",
                        'safe': "off",  #child protect
                        'filter': "1",  #duplicate filter
                        'num': "20",     #count
                       })
    
    html_content=get_web_content_with_cache(urlbase+get,debug);
    html_content=html_content.decode("utf-8")

    return html_content


def separate(text,repl=""):
    ascii_separator=[
                   ":",",","&",
                   "\[","\]","\|","\"", #special char in regex
                   "(",")",
                    "·","»",#latin-1
                   ]
    text=re.sub("[" + "".join(cjk.get_separator())+ "".join(ascii_separator) +"]",repl,text)
    text=re.sub("\.[ ]+",repl,text)
    return text


def replace(text,repl=""):
    replace_text=[x.decode("utf-8") for x in [
        "-",
        "avi","wmv","release",
        "(\d+(\.\d*)?|\.\d+) *(g[b]?|mb) *", #size in mb or gb
        "発売日","監督","動画","収録時間","利用規約","検索","出演者","画像","時間","予約","商品","詳細","価格",
        "アダルト","dvd","通販",#Adult dvd mail order
        "ニュース",#news
        "レーベル",#Label
        "日本語のページを",#A page of Japanese
        "もっとツールを見る",# see more tools
        "([^\|]*合衆国.*作権法[^\|]*)","[^\|]*chillingeffects.org[^\|]*", #DMCA
        ]]
    text=re.sub("|".join(replace_text),repl,text)
    return text


def get_vaid(string):
    vaid=string
    vaid_match=re.search(r"([a-zA-Z]+[-]?\d+)",string,re.IGNORECASE)
    if vaid_match is not None:
        vaid=vaid_match.group(1)
    return vaid
    

def get_vaname(query,verbose=False,debug=False):
    html=get_google_content(query,debug=debug)
    html=html.lower()
    html=htmltool.decode_entity(html)
    html=htmltool.remove_tags(html,repl="||")
    html=htmltool.clean_tags(html,repl="||")
    if debug:
        printu(html)
    
    html=separate(html,repl="||")
    html=replace(html,"")
    html=cjk.half2full(html)

    strings_list=[content.strip() for content in html.split("||") if len(content.strip()) ]
    strings_count=Counter(strings_list)
    for string,count in strings_count.items():
        if count <= 1:
            pass
            #del strings_count[string]

    l=[(string,count*len(string)*(10 if cjk.contain_cjk(string) else 1)) for string,count in strings_count.items()]
    l.sort(key=lambda t:t[1],reverse=True)  #sort by weight

    
    if verbose:
        #dump (word,weight) list
        for string,weight in sorted(l,key=lambda t:t[1]):
            printu("%-6d:%s"%(weight,string))
    ## max
    maxweight_string=(l[0][0])  #print max weight string
    maxweight_substring=[re.sub("[\w \.]+$","",string) for string,weight in l[0:5] if maxweight_string in string]
    return max(maxweight_substring,key=len)


def filename_strip(name):
    ascii_separator=[ "*",
                      "\\", "\/",
                    ]
    name=re.sub("[" + "".join(ascii_separator) +"]","",name)
    return name

        
def printu(unistr):
    print unistr.encode()


def usage():
    printu( 
"""
Usage: 
    -k keyword | --keyword=keyword    # Kerword to query
    -p path    | --path=path          # Path to query
    -d         | --debug              # Dump html and stop process
    -v         | --verbose            # verbose
    -w         | --weight             # show the weight of all strings
    --mt                              # test move of [src -> dst]
    --mv                              # do move of [src -> dst]
"""
)
    
def main():
    #html=open("out").read().decode("utf=8")
    ## handle parameter
    try:
        options,nonoptions = getopt.getopt(sys.argv[1:],"k:p:dvw",["keyword=","path=","debug","verbose","weight","mt","mv"])
    except getopt.GetoptError, err:
        # print help information and exit:
        printu("Error: "+str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    opts={  "keyword":None,
            "path":None,
            "debug":False,
            "verbose":False,
            "weight":False,
            "mt":False,
            "mv":False,
        }
    for opt,arg in options:
        if opt in ("-k","--keyword"):
            opts["keyword"]=arg.decode()
        if opt in ("-p","--path"):
            upath=os.path.normpath(arg.decode(sys.getdefaultencoding()))
            rpath=upath.encode()
            if os.path.exists(rpath) and (os.path.isdir(rpath) or os.path.isfile(rpath)):
                opts["path"]=os.path.abspath(rpath)
                vaid=get_vaid(os.path.basename(rpath))
            else:
                printu("Error path:"+upath)
                sys.exit(1)
        if opt in ("-d","--debug"):
            opts["debug"]=True
        if opt in ("-v","--verbose"):
            opts["verbose"]=True
        if opt in ("-w","--weight"):
            opts["weight"]=True
        if opt in ("--mt"):
            opts["mt"]=True
        if opt in ("--mv"):
            opts["mv"]=True
    

    if opts["path"] and not opts["keyword"]:
        opts["keyword"]=vaid    #use vaid instead keyword
    if opts["keyword"]:
        vaid=opts["keyword"]    #no matter vaid, use kerword to replace current vaid
        vaname=get_vaname(opts["keyword"],opts["verbose"],opts["debug"])
        if opts["verbose"] or opts["debug"]:    #debug mode
            return
    else:
        printu("No valid keyword")
        usage()
        sys.exit(1)

    if opts["path"]:
        if not opts["mt"] and not opts["mv"]:
            printu(vaname)
            return
        #in move mode
        vaname=filename_strip(vaname)
        dstpath=os.path.join(os.path.dirname(upath),vaid+"(%s)"%vaname)
        if opts["mt"]:
            printu( """mv '%s' '%s' """%(upath.encode(), dstpath.encode()) ) #first dry run
        if opts["mv"]:
            shutil.move(opts["path"],dstpath) # do move!!
    else:
        printu(vaname) 


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
