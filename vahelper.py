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


def get_google_content(keyword,urlbase="https://www.google.co.jp/search?"):
    '''
    return the html content in unicode
    '''
    urlbase="https://www.google.co.jp/search?"
    get=urllib.urlencode( { 'q': keyword,
                        'ie' : "utf-8",
                        'oe' : "utf-8",
                        'safe': "off",  #child protect
                        'filter': "1",  #duplicate filter
                        'num': "20"     #count
                       })
    
    headers = { 'User-Agent' : 'Mozilla/5.0' }	# google banned unvalid user-agent.
    html_request = urllib2.Request(urlbase+get, None, headers)
    html_content=urllib2.urlopen(html_request).read()
    return html_content.decode("utf-8")


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
        "(\d+(\.\d*)?|\.\d+) *(gb|mb)", #size in mb or gb
        "発売日","監督","動画","収録時間","利用規約","検索","出演者","画像","時間","予約","商品","詳細",
        "ニュース",#news
        "レーベル",#Label
        "日本語のページを",#A page of Japanese
        "もっとツールを見る",# see more tools
        ]]
    text=re.sub("|".join(replace_text),repl,text)
    return text


def get_vaid(string):
    vaid_match=re.search(r"(\w+[-]?\d+)",string,re.IGNORECASE)
    if vaid_match is not None:
        vaid=vaid_match.group(1)
    else:
        print "Non available vaid for " +string
    return vaid

def get_vaname(query,verbose=False,debug=False):
    html=get_google_content(query)
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
        if count <= 2:
            #del words_count[string]
            pass

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
        
        
def printu(unistr):
    print unistr.encode()


def usage():
    print( 
"""
Usage: 
    -q keyword or --query=keyword :Query kerword
    [-v] [--verbose]              :List all string and it's weight
    [-d] [--debug]                :Dump html and stop
"""
)
    
def main():
    #html=open("out").read().decode("utf=8")
    ## handle parameter
    options,nonoptions = getopt.getopt(sys.argv[1:],"p:q:vdmg",["query=","path=","verbose","debug","move","go"])
    
    query=None
    verbose=False
    debug=False
    path=None
    move=False
    go=False
    for opt,arg in options:
        if opt in ("-q","--query"):
            query=arg.decode()
        if opt in ("-v","--verbose"):
            verbose=True
        if opt in ("-d","--debug"):
            debug=True
        if opt in ("-p","--path"):
            rpath=os.path.normpath(arg.decode(sys.getfilesystemencoding()))
            if os.path.exists(rpath) and (os.path.isdir(rpath) or os.path.isfile(rpath)):
                path=os.path.abspath(rpath)
                vaid=get_vaid(os.path.basename(path))
                query=vaid
            else:
                usage()
                exit(1)
        if opt in ("-m","--move"):
            move=True
        if opt in ("-g","--go"):
            go=True

    if query:
        vaname=get_vaname(query,verbose,debug)
    else:
        usage()
        exit(1)

    #debug mode
    if verbose or debug:
        return
    elif move and path:
        #in move mode,first dry run
        dstpath=os.path.join(os.path.dirname(rpath),vaid+"(%s)"%vaname)
        printu("""mv '%s' '%s' """%(rpath,dstpath))
        if go:
            shutil.move(path,dstpath)
    elif vaname:
        #default: just print the vaname
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