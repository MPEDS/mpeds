
import glob
import sys
import urllib
import urllib2

import json

import pandas as pd 
import numpy as np

from sklearn.externals import joblib

class MPEDS:
    def __init__(self):
        ''' Constructor. '''
        self.vect       = joblib.load("classifiers/haystack-vect_all-source_2016-03-21.pkl")
        self.clf        = joblib.load("classifiers/haystack_all-source_2016-03-21.pkl")
        self.search_str = 'boycott* "press conference" "news conference" (protest* AND NOT protestant*) strik* rally ralli* riot* sit-in occupation mobiliz* blockage demonstrat* marchi* marche*'
        self.solr_url   = None


    def setSolrURL(self, url):
        self.solr_url = url


    def buildSolrQuery(self, q_dict):
        ''' Build a query for a Solr request. '''
        q = []
        for k, v in q_dict.iteritems():
            sub_q = '%s:"%s"' % (k, v)
            q.append(sub_q)

        query = ' AND '.join(q)
        return query


    def makeSolrRequest(self, q, fq, protest = False):
        """ makes Solr requests to get article texts """

        data = {
            'q':     q,
            'start': start,
            'rows':  rows,
            'wt':    'json'
        } 

        ## put protest string into fq field
        if protest:
            data['fq'] = self.search_str

        data = urllib.urlencode(data)
        req  = urllib2.Request(solr_url, data)
        res  = urllib2.urlopen(req)
        res  = json.loads(res.read())

        numFound = res['response']['numFound']

        print("%d documents found." % numFound)

        ## add 100 to get everything for sure
        numFound += 100

        articles = []
        interval = 100
        prev = 0
        for i in range(0, numFound, interval):
            data = {
                'q': q,
                'fq': fq,
                'rows': interval,
                'start': prev,
                'wt': 'json'
            }
            data = urllib.urlencode(data)
            req  = urllib2.Request(url, data_str)
            res  = urllib2.urlopen(req)
            res  = json.loads(res.read())

            articles.extend(res['response']['docs'])

            if i % 1000 == 0:
                print('%d documents collected.' % i)

            prev = i

        return docs


    def getLede(self, text):
        ''' Get the lede sentence for this text. '''
        sentences = text.split("<br/>")
        return sentences[0]


    def vectorize(self, text):
        ''' '''
        return self.vect.transform(text)


    def haystack(self, X):
        ''' '''
        return self.clf.predict(X)


    def getForm(self, X):
        ''' '''
        return self.form_clf.predict(X)


    def getFormProb(self, X):
        ''' '''
        pass


    def getIssue(self, X):
        ''' '''
        return self.issue_clf.predict(X)


    def getIssueProb(self, X):
        ''' '''
        pass


    def getTarget(self, X):
        ''' '''
        return self.target_clf.predict(X)


    def getTargetProb(self, X):
        ''' '''
        pass


    def getLocation(self, document):
        pass


    def getSMO(self, document):
        pass


    def getSize(self, document):
        pass




        







