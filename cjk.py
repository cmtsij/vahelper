#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

def get_separator():
    #create utf-table
    __separator_utf8__ = [
        "、","・","：","–",
        "「","」",
        "【","】",
        "（","）",
        "«",
        ]
    __separator__ = [ c.decode("utf-8") for c in __separator_utf8__ ] #translate to unicode

    for i in xrange(0x3008,0x3020):
            __separator__.append(unichr(int(i)))

    #unique and sorted
    __separator__=sorted(set(__separator__),key=lambda unichar:ord(unichar))
    return __separator__

__char_plane__ = [[0x2E80, 0x2E99],    # Han # So  [26] CJK RADICAL REPEAT, CJK RADICAL RAP
                 [0x2E9B, 0x2EF3],    # Han # So  [89] CJK RADICAL CHOKE, CJK RADICAL C-SIMPLIFIED TURTLE
                 [0x2F00, 0x2FD5],    # Han # So [214] KANGXI RADICAL ONE, KANGXI RADICAL FLUTE
                 0x3005,              # Han # Lm       IDEOGRAPHIC ITERATION MARK
                 0x3007,              # Han # Nl       IDEOGRAPHIC NUMBER ZERO
                 [0x3021, 0x3029],    # Han # Nl   [9] HANGZHOU NUMERAL ONE, HANGZHOU NUMERAL NINE
                 [0x3038, 0x303A],    # Han # Nl   [3] HANGZHOU NUMERAL TEN, HANGZHOU NUMERAL THIRTY
                 0x303B,              # Han # Lm       VERTICAL IDEOGRAPHIC ITERATION MARK
                 [0x3400, 0x4DB5],    # Han # Lo [6582] CJK UNIFIED IDEOGRAPH-3400, CJK UNIFIED IDEOGRAPH-4DB5
                 [0x4E00, 0x9FC3],    # Han # Lo [20932] CJK UNIFIED IDEOGRAPH-4E00, CJK UNIFIED IDEOGRAPH-9FC3
                 [0xF900, 0xFA2D],    # Han # Lo [302] CJK COMPATIBILITY IDEOGRAPH-F900, CJK COMPATIBILITY IDEOGRAPH-FA2D
                 [0xFA30, 0xFA6A],    # Han # Lo  [59] CJK COMPATIBILITY IDEOGRAPH-FA30, CJK COMPATIBILITY IDEOGRAPH-FA6A
                 [0xFA70, 0xFAD9],    # Han # Lo [106] CJK COMPATIBILITY IDEOGRAPH-FA70, CJK COMPATIBILITY IDEOGRAPH-FAD9
                 [0x20000, 0x2A6D6],  # Han # Lo [42711] CJK UNIFIED IDEOGRAPH-20000, CJK UNIFIED IDEOGRAPH-2A6D6
                 [0x2F800, 0x2FA1D]
                 ]  # Han # Lo [542] CJK COMPATIBILITY IDEOGRAPH-2F800, CJK COMPATIBILITY IDEOGRAPH-2FA1D

def get_plane_list():
    __char_list__ = []
    for char in __char_plane__:
        if isinstance(char,list):
            start, end = char
            for c in xrange(start,end+1):
                __char_list__.append(unichr(c))
        else:
            __char_list__.append(unichr(char))
    return __char_list__
        
def is_cjk_char(chr):
    i=ord(chr[0])
    for char in __char_plane__:
        if isinstance(char,list):
            start, end = char
            if start<=i and i<= end:
                    return True
        else:
            if char == i:
                return True
        pass    
    return False

def contain_cjk(str):
    for c in str:
        if is_cjk_char(c):
            return True
    return False

def half2full(unitext):
    ''' 
    ref: http://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms
    '''
    from_table="!?".decode("utf-8")
    to_table="！？".decode("utf-8")
    tran_stable=dict( (ord(frm),ord(to)) for frm, to in zip(from_table,to_table)  )
    return unitext.translate(tran_stable)


#UNITEST
if __name__ == "__main__":
    c=unichr(0x303B)
    if is_cjk_char(c):
        print (c+" is cjk unicode.").encode("utf-8")
    if c in get_plane_list():
        print (c+" is cjk unicode.").encode("utf-8")

    #dump ckj file
    #open("cjk.txt","wb+").write("".join(get_plane_list()).encode("utf-8"))
