#!/usr/bin/env python
# encoding: utf-8
"""
Created by Neal Caren on 2012-05-14.
neal.caren@unc.edu

Edited by Alex Hanna to make this into a module and handle several different news sources.
alex.hanna@gmail.com

Takes a downloaded plain text LexisNexis file and returns list of documents.
"""

import os
import re
import sys
from datetime import datetime

def isMonth(x):
    isMonth = True
    try:
        datetime.strptime(x, "%B")
    except ValueError:
        isMonth = False

    if isMonth:
        return isMonth

    try:
        datetime.strptime(x, "%b")
    except ValueError:
        isMonth = False

    return isMonth

def isInt(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def parseLexisNexis(filename, output = "."):
    abstracts = []
    text = open(filename, 'r').read()

    # Figure out what metadata is being reported
    meta_list = list(set(re.findall('\\n([A-Z][A-Z-]*?):', text))) 

    ## set permanent columns
    header    = ['INTERNAL_ID', 'PUBLICATION', 'DATE', 'TITLE', 'EDITION']
    today_str = datetime.today().strftime('%Y-%m-%d')

    ## silly hack to find the end of the documents
    ## TK: This will break on abstracts
    # text = re.sub('                Copyright .*?\\r\\n','ENDOFILE', text)

    # clean up crud at the beginning of the file
    text = text.replace('\xef\xbb\xbf\r\n','')

    ## other crud
    text = text.replace('\\xa0', '')

    ## warning strings break date parsing, remove them
    warnings = [r'This content, including derivations, may not be stored or distributed in any\s+manner, disseminated, published, broadcast, rewritten\s+or reproduced without\s+express, written consent from STPNS\s+',
    r'No City News Service material may be republished without the express written\s+permission of the City News Service(,)* Inc\.\s+',
    r'Distributed by McClatchy\-Tribune Business News\s+',
    r'Distributed by Tribune Content Agency\s+',
    r'This content is provided to LexisNexis by Comtex News Network(,)* Inc\.\s+']

    for w in warnings:
        text = re.sub(w, '', text)

    ## Split by LN header
    ## odd numbers are search_id, evens are the documents
    docs = []
    ids  = []
    for i, d in enumerate(re.split(r'\s+(\d+) of \d+ DOCUMENTS', text)):
        if i == 0:
            pass
        elif i % 2 == 0:
            docs.append(d)
        else:
            ids.append(d)

    # remove blank rows in Python 2
    if (sys.version_info < (3, 0)):
        docs = [f for f in docs if len(re.split(r'\r\n\r\n', f)) > 2]

    # Keep only the commonly occuring metadata
    meta_list = [m for m in meta_list if float(text.count(m)) / len(docs) > 0.20] 

    articles = []
    ## Begin loop over each article
    for i, f in enumerate(docs):
        # Split into lines, and clean up the hard returns at the end of each line

        if (sys.version_info < (3, 0)):
            lines = [row.replace('\r\n', ' ').strip() for row in f.split('\r\n\r\n') if len(row) > 0]
        else:
            lines = [row.replace('\n', ' ').strip() for row in f.split('\n\n') if len(row) > 0]

        ## With an abstract, this is the format:
        # Copyright 1990 The New York Times Company: Abstracts
        #                  WALL STREET JOURNAL

        ## Skip the whole article if it's an abstract
        if 'Abstracts' in lines[0]:
            abstracts.append(lines[0])
            continue

        ## remove copyright
        lines = [row for row in lines if not re.match("^Copyright \d+.*$", row) and 'All Rights Reserved' not in row]

        ## make metadata dict
        meta_dict  = {k : '' for k in header}

        # doc_id  = lines[0].strip().split(' ')[0]
        pub     = lines[0].strip()
        date_ed = lines[1].strip()
        title   = lines[2].strip()

        ## format date into YYYY-MM-DD
        ## NYT:      July 27 2008 Sunday                               Late Edition - Final
        ## USATODAY: April 7, 1997, Monday, FINAL EDITION
        ## WaPo:     June 06, 1996, Thursday, Final Edition
        ## Corporate Counsel: June 2014
        ## 04/30/2014

        date_ed = date_ed.replace(',', '')
        da      = re.split('\s+', date_ed)
        da2     = re.split('/', date_ed)

        if len(da) >= 3 and isInt(da[1]) and isInt(da[2]):
            ## NYT, USA, WaPo
            date = datetime.strptime(" ".join(da[0:3]), "%B %d %Y")
        elif len(da) >= 2 and isInt(da[1]) and isMonth(da[0]):
            ## Corporate Counsel: June 2014 Northeast
            date = datetime.strptime(" ".join(da[0:2]), "%B %Y")
        elif len(da2) > 2:
            date = datetime.strptime(" ".join(da2[0:3]), "%m %d %Y")
        else:
            print("WARNING: Not a date: %s" % " ".join(da))
            continue

        date = date.strftime("%Y-%m-%d")
        ed   = " ".join( map(lambda x: x.strip(), da[4:]) )

        ## if edition is a time or day, skip it      
        if 'GMT' in ed or 'day' in ed:
            ed = ''
        
        ## Edit the text and other information
        paragraphs = []
        for line in lines[3:]:
            ## find out if this line is part of the main text
            if len(line) > 0 and line[:2] != '  ' and line != line.upper() and len(re.findall('^[A-Z][A-Z-]*?:',line)) == 0 and title not in line:
                ## remove new lines
                line = re.sub(r'\s+', ' ', line)
                line = line.replace('","','" , "')

                ## add to paragraph array
                paragraphs.append(line)
            else:
                metacheck = re.findall('^([A-Z][A-Z-]*?):', line)
                if len(metacheck) > 0:
                    if metacheck[0] in meta_list:
                       meta_dict[metacheck[0]] = line.replace(metacheck[0] + ': ','')  

        ## put everything in the metadata dictionary
        meta_dict['PUBLICATION'] = pub
        meta_dict['DATE']        = date
        meta_dict['TITLE']       = title
        meta_dict['EDITION']     = ed

        ## since JSON won't preserve escaped newlines
        meta_dict['TEXT']        = "<br/>".join(paragraphs)
        meta_dict['INTERNAL_ID'] = "%s_%s_%s" % (pub, date, ids[i])

        articles.append(meta_dict)

    print("\tAdded %d articles, skipped %d abstracts" % (len(articles), len(abstracts)))
    return articles


