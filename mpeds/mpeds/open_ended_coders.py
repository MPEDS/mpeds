# -*- coding: utf-8 -*-
import numpy as np
import nltk
import re

import urllib
import urllib.parse
import urllib.request
import json

import os

from sklearn.feature_extraction import _stop_words
from nltk.tag import StanfordNERTagger
from nltk.tokenize.stanford import StanfordTokenizer
from pkg_resources import resource_filename

import nltk.data

class SizeCoder:

    def __init__(self):

        self.SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')

        self.NUM_MAP = None
        self.RE = None

        self.S_PREFIX = None
        self.P_SUBJ = None
        self.AGW = None
        self.SWS = None

    def getSize(self, text, as_str = False, verbose = False):
        '''
        Extract protest size from text.

        :param text: text to be processed
        :type text: string

        :param as_str: logical indicating whether protest size should be returned as a string. Defaults to False.
        :type as_str: boolean

        :param verbose: logical indicating whether to print output for debugging, defaults to False
        :type verbose: boolean

        :return: sizes extracted from text
        :rtype: set, or a string if as_str = True

        '''

        # text = text.decode('utf-8')

        if not self.RE:
            self._loadRegexPatterns()

        if not self.S_PREFIX:
            self._loadSpecialWords()

        sizes = []
        sentences = []

        ## tokenize sentences if needed and remove dupes
        sentences = self.SENT_DETECTOR.tokenize(text)
        sentences = np.unique(sentences)

        for s in sentences:

            if verbose:
                print('\nPROCESSING SENTENCE: ' + s)

            ## hack to stop the issue with "tens"
            s = re.sub("tens of thousands", "10,000", s, flags = re.I)

            ## replace 'march' the month with something
            s = re.sub(r'March (\d+)', 'MONTH \1', s)

            tokens = re.split(r'\s+|-', s)
            tokens = [x.lower() for x in tokens]
            tokens = [x.strip('.,') for x in tokens]

            #tokens = list(set(tokens) - set(SWS))

            i_end = len(tokens)
            loc = 0
            for i in range(0, i_end):

                if verbose:
                    print('At token: ' + tokens[i])

                loc += len(tokens[i]) + 1
                size = None


                # skip ahead if not a number
                if not self.RE['DIGITS'].search(tokens[i]) and not self.RE['NUMBERS'].search(tokens[i]):
                    continue

                # skip if immediately followed by percent
                if i_end - i >= 2 and tokens[i + 1] == 'per' and tokens[i + 2] == 'cent':
                    continue

                ## skip years
                if self.RE['YEARS'].search(tokens[i]):
                    continue

                ## look to the right
                r_context = i + 5 if i + 5 <= i_end else i_end
                r_start   = i + 1 if i + 1 <= i_end else i_end
                for j in range(r_start, r_context):

                    if verbose:
                        print('     ' + tokens[j])

                    if self.RE['NUMBERS'].search(tokens[j]) and j - i < 3:
                        ## skip things which will be coded in the next pass
                        ## e.g. tens of thousands or two dozen

                        if verbose:
                            print('     -> Detected number, skipping ahead')

                        break

                    elif not self.RE['NVERBS'].search(' '.join(tokens[i:])):
                        ## filter out all verbs we don't want
                        size = tokens[i]

                        if (self.RE['SUBJ'].search(tokens[j]) or self.RE['ETHNIC'].search(tokens[j])) \
                            and self.RE['VERBS'].search(' '.join(tokens[i:])):
                            ## if not, test for a protest verb

                            size = tokens[i]

                            if verbose:
                                print('     -> Detected protest verb, setting size to ' + size)



                ## look to the left for numbers, crowd words
                l_context = i - 4 if i - 4 >= 0 else 0
                for j in range(l_context, i):

                    if verbose:
                        print('     ' + tokens[j])

                    #if RE_GROUPS.search(tokens[j]) and RE_VERBS.search(' '.join(tokens[i:])) and not size:
                    if not size:

                        if self.RE['GROUPS'].search(tokens[j]) or self.RE['VERBS'].search(' '.join(tokens[i:])):

                            size = tokens[i]

                            if verbose:
                                print('     -> Detected protest group or verb, setting size to ' + size)



                    elif self.RE['NUM_PRE'].search(tokens[j]):

                        size = '-'.join([tokens[j], size])

                        if verbose:
                            print('     -> Detected pre-number, setting size to ' + size)

                        if len(sizes) > 0 and self._strToNum(tokens[j]) == sizes[len(sizes) - 1]:

                            sizes = sizes[1:(len(sizes) - 1)]

                            if verbose:
                                print('-> Pre-number added to sizes at last iteration, removing it')

                if size:
                    ## parse and append
                    if verbose:
                        print('-> Adding ' + str(self._strToNum(size)) + ' to sizes')

                    sizes.append(self._strToNum(size))

        sizes = np.sort(sizes)

        if as_str:
            return '; '.join(map(lambda x: str(x), set(sizes)))
        else:
            return set(sizes)

    def _strToNum(self, s):
        '''
        Convert approximate strings to numbers.

        :param s: text containing approximate number
        :type s: string

        :return: number extracted from text
        :rtype: integer
        '''

        if not self.RE:
            self._loadRegexPatterns()

        num = 1
        strings = s.split('-')
        for i in range(0, len(strings)):
            if self.RE['OVER20'].search(strings[i]):
                ## word number between 20 and 100
                if i + 1 < len(strings):
                    if self.RE['LESS10'].search(strings[i + 1]):
                        ## then we have a string in the form of 'seventy-five'
                        num = self.NUM_MAP[strings[i]] + self.NUM_MAP[strings[i + 1]]
                        return num
                else:
                    num *= self.NUM_MAP[strings[i]]
            elif self.RE['DIGITS'].search(strings[i]):
                ## a number, just remove commas
                num *= int(strings[i].replace(',', ''))
            elif strings[i] in self.NUM_MAP.keys():
                num *= self.NUM_MAP[strings[i]]
            else:
                #print('Numerical token undefined: %s' % strings[i])
                return None

        return num


    def _loadRegexPatterns(self):
        ''' Load regex patterns to be used in size extraction logic '''

        if not self.NUM_MAP:
            self._loadNumberMapping()

        # remove tens, which is almost never used by itself
        number_set = list(self.NUM_MAP.keys())
        number_set.remove('tens')

        S_LESS10  = r'one|two|three|four|five|six|seven|eight|nine'
        S_MIDTEEN = r'ten|eleven|twelve|thirteen|fourteen|fifteen'
        S_OVER20  = r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety'
        S_DIGITS  = r'\d*\,*\d+'
        S_YEARS   = r'(18|19|20)([0-9][1-9]|[1-9][0-9])'

        # need to add ethnicities
        self.RE = {
            'DIGITS': re.compile(r'^(' + S_DIGITS + ')$'),
            'ALL': re.compile(r'^(' + '|'.join([S_DIGITS, S_LESS10, S_MIDTEEN, S_OVER20]) + ')$'),
            'NUM_PRE': re.compile(r'^(' +  S_LESS10 + '|ten|tens|several|' + S_OVER20 + '|hundred|hundreds)$'),
            'LESS10': re.compile(r'^(' + S_LESS10 + ')$'),
            'MIDTEENS': re.compile(r'^(' + S_MIDTEEN + ')$'),
            'OVER20': re.compile(r'^(' + S_OVER20 + ')$'),
            'NUMBERS': re.compile('^(' + '|'.join(number_set) + ')$'),
            'SUBJ': re.compile(r'\w+(ors|ers|ists|ants|ents|ees)|\w*men|people|children|families|children|victims|youths|monks|nuns|prostitutes|pilots|cops|union|nurses|inmates|gays|criminals|slaves|citizens|guild|guards|pilgrims|exiles|fans'),
            'GROUPS': re.compile(r'group(s){0,1}|crowd(s){0,1}|estimate(s){0,1}|number(ing|ed){1}|march|rally|strike'),
            'VERBS': re.compile(r'strik(ing|es|ed)*|struck|demonstrat\w+|protest(?!ant)|march(ed|ing)|to march|rall(y|ied|ies)+|riot(ed|ing)*|picket(ed)*|chant(ed|ing)*|shout(ed|ing)*|(took|take) to the street(s)*|rampage(d)*|ransack(ed)|gather(ed)*|petition|occup(y|ied|ing)+|stay(ed)* home|demand(ed|ing)*|stopped work(ing)*|walk(ed)*\s*out|(holding|held) (up)* signs|held a sleepout|blockaded traffic|rebellion|jamm(ing|ed) the street(s)*|signed a letter|(press|news) conference|boycott(ed|ing)*|vandaliz\w+|burned|camp(ed)|return(ed)* to work|ended their fast|walked off the job|carr(ied|ying) signs|were expected'),
            'NVERBS': re.compile(r'were (hurt|injured|killed|wounded)|died'),
            'ETHNIC': self._getEthnicitiesRegexPattern(),
            'YEARS': re.compile(r'^(' + S_YEARS + ')$')
            }

    def _loadSpecialWords(self):
        ''' Load stop words, number prefixes, news agencies, and protest subject words. '''
        self.S_PREFIX  = ['around', 'up to', 'as many as', 'some', 'many', 'nearly', 'more than', 'about']

        self.P_SUBJ   = {
            'protest': ['protesters', 'protestors', 'students', 'people','demonstrators', 'activists', 'strikers', 'marchers', 'signatures',
            	'counter-demonstrators', 'counter-demonstraters', 'counter-protesters', 'counter-protestors', 'counterprotesters',
            	'counterprotestors']
                }

        self.AGW = ['Agence France-Presse, English Service', 'Associated Press Worldstream, English Service']

        self.SWS = list(_stop_words.ENGLISH_STOP_WORDS)


    def _loadNumberMapping(self):
        ''' Load dictionary mapping number strings to numbers. '''

        self.NUM_MAP = {
            'two' :  2,
            'three': 3,
            'four':  4,
            'five':  5,
            'six':   6,
            'seven': 7,
            'eight': 8,
            'nine':  9,
            'ten':   10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'several': 2,
            'few': 2,
            'tens':  10,
            'dozen': 10,
            'dozens': 10,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
            'sixty': 60,
            'seventy': 70,
            'eighty': 80,
            'ninety': 90,
            'hundred': 100,
            'hundreds': 100,
            'thousand': 1000,
            'thousands': 1000,
            'million': 1000000,
            'millions': 1000000
            }

    def _getEthnicitiesRegexPattern(self):
        '''
        Parse ethnic and nationalist nouns from Wikipedia into a regex pattern
        https://en.wikipedia.org/wiki/List_of_contemporary_ethnic_groups
        https://en.wikipedia.org/wiki/Lists_of_people_by_nationality

        :return: regex patterns of ethnicities_2016-03
        :rtype: regex patterns
        '''
        return re.compile('|'.join(open( resource_filename(__name__, 'input/ethnicities_2016-03-15.csv'), 'r' ).read().split('\n')))

class LocationCoder:
    '''
    Class for getting locations of organizations.

    '''

    def __init__(self, cliff_url = 'cliff:8080/CLIFF-2.3.0'):
        self.cliff_url = cliff_url        
        pass


    def getLocation(self, text, as_str = False):
        '''
        Extract location from a string

        :param text: text from which location should be extracted
        :type text: string

        :param as_str: logical indicating whether results should be returned as a string. Defaults to False.
        :type as_str: boolean

        :return: extracted locations
        :rtype: set, or string if as_str = True
        '''

        cliff_results = self._getCLIFF(text)
        locations = self._CLIFFLocDecision(cliff_results)

        if as_str and locations:
            # do not run this step if locations is None, throws an error

            # first convert each tuple to a string. Unfortunately need to do this in a for loop, due to utf-8 issues
            string_locations = []

            for location in locations:

                tuple_values = [ e if isinstance(e, unicode) else str(e) for e in location  ]
                string_locations.append( ', '.join(tuple_values) )

            return '; '.join(string_locations)

        else:
            return locations

    def _matchGeoName(self, geoname_id, cliff_results, geoname_type = 'state'):
        '''
        Get name of state or country based on GeoName ID by parsing through list of CLIFF results.

        :param geoname_id: GeoName ID to be matched
        :type geoname_id: string

        :param cliff_results: CLIFF results to parse through
        :type cliff_results: json

        :param geoname_type: type of geoname to be matched, 'state' (default) or 'country'
        :type geoname_type: string

        :return: name of country or state, or None if no matching name found
        :rtype: string
        '''

        # INPUT TESTING
        if geoname_type not in ['state', 'country']:
            raise ValueError("geoname_type must be either state or country")

        field = geoname_type + 'GeoNameId'

        for entry in cliff_results:
            if geoname_id == entry[field]:
                return entry['name']

        return None


    def _urlencode_utf8(self, params):
        '''
        Workaround to allow for UTF-8 characters in urlencode
        See http://stackoverflow.com/questions/6480723/urllib-urlencode-doesnt-like-unicode-values-how-about-this-workaround

        :param params: parameters to encode
        :type params: a dictionary or list of tuples containing parameters to be encoded

        :return: utf-8 encoded URL parameters
        :rtype: string
        '''
        if hasattr(params, 'items'):
            params = params.items()
        return '&'.join(
            (urllib.parse.quote_plus(k.encode('utf8'), safe='/') + '=' + urllib.parse.quote_plus(v.encode('utf8'), safe='/')
                for k, v in params) )


    def _getCLIFF(self, text):
        '''
        Retrieve organizations and location via CLIFF.

        :param text: text from which locations should be extracted
        :type text: string

        :return: CLIFF location results
        :rtype: dictionary
        '''

        if text != text:
            return ([],{})

        obj = None
        data = self._urlencode_utf8({ 'q': text })

        while obj is None:
            url = 'http://%s/parse/text' % self.cliff_url
            req = urllib.request.Request(url, data.encode('utf-8'))
            res = urllib.request.urlopen(req)
            obj = json.loads(res.read())

            if obj is not None:
                if obj['status'] == 'error':
                    return ([], {})
                elif obj['status'] != 'ok':
                    obj = None
                    continue

            locs = obj['results']['places']

        return locs

    def _CLIFFLocDecision(self, x):
        '''
        Decision tree on what location to return based on CLIFF results.

        :param x: CLIFF location results
        :type x: dictionary

        :return: final location
        :rtype: string

        '''

        # TO DO: should this have option to return set rather than string, to mimick size behaviour?

        ## skip empties
        if len(x.keys()) == 0:
            return None

        locs = []
        mens = []
        ## if focus exists, return the city first
        if 'focus' in x:
            unit = ''
            cities = x['focus'].get('cities')
            states = x['focus'].get('states')
            countries = x['focus'].get('countries')

            if cities:
                unit = 'cities'
            elif states:
                unit = 'states'
            elif countries:
                unit = 'countries'
            else:
                return None

            for l in x['focus'][unit]:

                if 'countries' == unit:
                    locs.append( (l['name'], l['lat'], l['lon']) )
                elif 'states' == unit:
                    country = self._matchGeoName(l['countryGeoNameId'], x['focus']['countries'], geoname_type = 'country')
                    locs.append( (l['name'], country, l['lat'], l['lon']) )
                elif 'cities' == unit:
                    state = self._matchGeoName(l['stateGeoNameId'], x['focus']['states'], geoname_type = 'state')
                    country = self._matchGeoName(l['countryGeoNameId'], x['focus']['countries'], geoname_type = 'country')

                    locs.append( (l['name'], state, country, l['lat'], l['lon']) )

        elif 'mentions' in x:
            for m in x['mentions']:
                mens.append( (m['source']['string'], m['source']['charIndex']) )

            ## take the top mentioned location
            s_mens = sorted(mens, key = lambda x: x[1])
            locs.append(s_mens[0])

        if locs:
            return set(locs)

        return None

class SMOCoder:

    def __init__(self):

        # set envirinment variable
        # TO DO: update to Docker path
        os.environ['CLASSPATH'] = resource_filename(__name__, 'tokenizers/')

        # load tokenizer and tagger
        # TO DO: again, update to Docker path
        self.STANFORD_TOKENIZER = StanfordTokenizer(resource_filename(__name__, 'tokenizers/stanford-ner-3.6.0.jar'))
        self.SMO_tagger = StanfordNERTagger(resource_filename(__name__, 'classifiers/ner-orgs_2016-03-28_all.ser.gz'))

    def getSMO(self, text, as_str = False):
        '''
        Extract social movement organizations from text using a custom trained Stanford NER tagger.

        :param text: text to extract social movement organizations from
        :type text: string

        :param as_str: logical indicating whether SMOs should be returned as a string. Defaults to False.
        :type as_str: boolean

        :return: SMOs extracted from text
        :rtype: set, or a string if as_str = True
        '''

        # Tokenize. What to do about <br /> ?
        tokens = self.STANFORD_TOKENIZER.tokenize(text)

        # Run tagging. This returns a list of tuples
        # classified as 'ORGANIZATION' if an SMO, 'O' otherwise
        tags = self.SMO_tagger.tag(tokens)

        current_SMO = ''
        all_SMOs = []

        # Note: Stanford NER tagger tags individual words as SMO or non-SMO.
        # For example, Black Lives Matter will be returned as ('Black', 'ORGANIZATION'), ('Lives', 'ORGANIZATION'), ('Matter', 'ORGANIZATION')
        # We want to parse this to a single organization.
        #
        # Non-perfect solution: assume that all consecutive ORGANIZATION tags represent a single SMO
        for tag in tags:

            # if tagged as organization, add to current SMO and skip ahead
            if 'ORGANIZATION' == tag[1]:

                if '' == current_SMO or "'" == tag[0]:
                    current_SMO = current_SMO + tag[0]
                else:
                    current_SMO = current_SMO + ' ' + tag[0]

                continue

            # adding test for unknown label
            if 'O' != tag[1]:
                print('Unknown tag ' + tag[1] + ', skipping ahead. Could be worth investigating further.')

            # add last detected organization to list and reset current_SMO
            if '' != current_SMO:
                all_SMOs.append(current_SMO)
                current_SMO = ''

        # get unique elements
        all_SMOs = set(all_SMOs)

        if as_str:
            return '; '.join(all_SMOs)
        else:
            return all_SMOs
