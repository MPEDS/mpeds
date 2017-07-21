# -*- coding: utf-8 -*-
import json
import urllib
import urllib2

class Solr:

    def __init__(self):        
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


    def makeSolrRequest(self, q, fq = None, protest = False):
        """ makes Solr requests to get article texts """

        data = {
            'q':     q,
            'start': 0,
            'rows':  10,
            'wt':    'json'
        }

        ## put protest string into fq field
        if protest:
            data['fq'] = self.search_str

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

        if fq and not protest:
            data['fq'] = fq

        articles = []
        for i in range(0, numFound, interval):
            data = {
                'q': q,
                'rows': interval,
                'start': prev,
                'wt': 'json'
            }

            data = urllib.urlencode(data)
            req  = urllib2.Request(self.solr_url, data)
            res  = urllib2.urlopen(req)
            res  = json.loads(res.read())

            articles.extend(res['response']['docs'])

            if i % 1000 == 0:
                print('%d documents collected.' % i)

            prev = i

        return articles