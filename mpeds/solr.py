# -*- coding: utf-8 -*-
import json
import urllib
import urllib2

""" 
Helper class for querying an Apache Solr database. 
"""

class Solr:
    def __init__(self):
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


    def getResultsFound(self, q, fq = None):
        """ report the number of results found for any given request. """
        data = {
            'q':     q,
            'start': 0,
            'rows':  10,
            'wt':    'json'
        }

        if fq:
            data['fq'] = fq

        data = urllib.urlencode(data)
        req  = urllib2.Request(self.solr_url, data)
        res  = urllib2.urlopen(req)
        res  = json.loads(res.read())

        return res['response']['numFound']


    def getDocuments(self, q, fq = None):
        """ makes Solr requests to get article texts """

        data = {
            'q':     q,
            'start': 0,
            'rows':  10,
            'wt':    'json',
        }

        if fq:
            data['fq'] = fq

        data = urllib.urlencode(data)
        req  = urllib2.Request(self.solr_url, data)
        res  = urllib2.urlopen(req)
        res  = json.loads(res.read())

        numFound = res['response']['numFound']

        print("%d documents found." % numFound)

        interval = 100

        ## add 100 to get everything for sure
        numFound += interval

        prev = 0
        data = {
            'q': q,
            'rows': interval,
            'start': prev,
            'wt': 'json'
        }

        if fq:
            data['fq'] = fq

        articles = []
        for i in range(0, numFound, interval):
            data = {
                'q': q,
                'rows': interval,
                'start': prev,
                'wt': 'json'
            }

            if fq:
                data['fq'] = fq

            data = urllib.urlencode(data)
            req  = urllib2.Request(self.solr_url, data)
            res  = urllib2.urlopen(req)
            res  = json.loads(res.read())

            articles.extend(res['response']['docs'])

            if i % 1000 == 0:
                print('%d documents collected.' % i)

            prev = i

        return articles