
import glob
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
        self.solr_url   = 'http://sheriff.ssc.wisc.edu:8983/solr/mpeds2/select'
        self.search_str = "boycott* \"press conference\" \"news conference\" (protest* AND NOT protestant*) strik* rally ralli* riot* sit-in occupation mobiliz* blockage demonstrat* marchi* marche*"


    def buildSolrQuery(self, q_dict):
        ''' Build a query for a Solr request. '''
        q = []
        for k, v in q_dict.iteritems():
            if k == 'protest':
                q.append('(%s)' % self.search_str)
            else:
                sub_q = '%s:"%s"' % (k, v)
                q.append(sub_q)

        query = ' AND '.join(q)
        return query


    def makeSolrRequest(self, query):
        """ makes Solr requests to get article texts """

        ## this is a comment
        docs = []
        data = {
            'q':     query,
            'rows':  10000000,
            'wt':    'json'
        } 
        data = urllib.urlencode(data)

        req = urllib2.Request(self.solr_url, data)
        res = urllib2.urlopen(req)
        obj = json.loads(res.read())

        print(obj['response']['numFound'])
        docs.extend(obj['response']['docs'])

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



