# -*- coding: utf-8 -*-
import numpy as np
import nltk
import re

from sklearn.feature_extraction import stop_words

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

    def getProtestSize(self, text, as_str = False):
        '''
        Extract protest size from text.

        :param text: text to be processed
        :type text: string

        :param as_str: logical indicating whether protest size should be returned as a string. Defaults to False.
        :type as_str: boolean

        :return: sizes extracted from text
        :rtype: set, or a string if as_str = True

        '''

        text = text.decode('utf-8')

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
                loc += len(tokens[i]) + 1
                size = None
                if not self.RE['DIGITS'].search(tokens[i]) and not self.RE['NUMBERS'].search(tokens[i]):
                    continue

                ## look to the right
                r_context = i + 5 if i + 5 <= i_end else i_end
                r_start   = i + 1 if i + 1 <= i_end else i_end
                for j in range(r_start, r_context):
                    if self.RE['NUMBERS'].search(tokens[j]) and j - i < 3:
                        ## skip things which will be coded in the next pass
                        ## e.g. tens of thousands or two dozen
                        break
                    elif not self.RE['NVERBS'].search(' '.join(tokens[i:])):
                        ## filter out all verbs we don't want
                        if tokens[j] in self.P_SUBJ['protest']:
                            ## if there is a protest subj, use that
                            size = tokens[i]
                        elif (self.RE['SUBJ'].search(tokens[j]) or self.RE['ETHNIC'].search(tokens[j])) \
                            and self.RE['VERBS'].search(' '.join(tokens[i:])):
                            ## if not, test for a protest verb
                            size = tokens[i]

                ## look to the left for numbers, crowd words
                l_context = i - 4 if i - 4 >= 0 else 0
                for j in range(l_context, i):
                    #if RE_GROUPS.search(tokens[j]) and RE_VERBS.search(' '.join(tokens[i:])) and not size:
                    if not size:
                        if self.RE['GROUPS'].search(tokens[j]) or self.RE['VERBS'].search(' '.join(tokens[i:])):
                            size = tokens[i]
                    elif self.RE['NUM_PRE'].search(tokens[j]):
                        size = '-'.join([tokens[j], size])

                if size:
                    ## parse and append
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
            if self.RE['DIGITS'].search(strings[i]):
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
        number_set = self.NUM_MAP.keys()
        number_set.remove('tens')

        S_LESS10  = r'one|two|three|four|five|six|seven|eight|nine'
        S_MIDTEEN = r'ten|eleven|twelve|thirteen|fourteen|fifteen'
        S_OVER20  = r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety'
        S_DIGITS  = r'\d*\,*\d+'

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
            'ETHNIC': self._loadEthnicities()
            }

    def _loadSpecialWords(self):
        self.S_PREFIX  = ['around', 'up to', 'as many as', 'some', 'many', 'nearly', 'more than', 'about']

        self.P_SUBJ   = {
            'protest': ['protesters', 'protestors', 'demonstrators', 'activists', 'strikers', 'marchers', 'signatures',
            	'counter-demonstrators', 'counter-demonstraters', 'counter-protesters', 'counter-protestors', 'counterprotesters',
            	'counterprotestors']
                }

        self.AGW = ['Agence France-Presse, English Service', 'Associated Press Worldstream, English Service']

        self.SWS = list(stop_words.ENGLISH_STOP_WORDS)


    def _loadNumberMapping(self):

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

    def _loadEthnicities(self):
        # should this be named load when the other load functions update self objects rather than return stuff?
        """ Load ethnic and nationalist nouns from Wikipedia:
        https://en.wikipedia.org/wiki/List_of_contemporary_ethnic_groups
        https://en.wikipedia.org/wiki/Lists_of_people_by_nationality
        """
        return re.compile('|'.join(open( 'input/ethnicities_2016-03-15.csv', 'r' ).read().split('\n')))


class OrgLocCoder:
    '''
    Class for getting locations of organizations.

    '''

    def __init__(self):
        pass

    def getOrgLoc(self, text):
        pass

    def _getCLIFF(self, text, as_str = False):
        '''Retrieve organizations and location via CLIFF.'''

        if text != text:
            return ([],{})

        obj = None
        data = urlencode_utf8({ 'q': text.decode('utf-8') })

        while obj is None:
            url = 'http://%s/parse/text' % config['CLIFF_URL']
            req = urllib2.Request(url, data)
            res = urllib2.urlopen(req)
            obj = json.loads(res.read())

            if obj is not None:
                if obj['status'] == 'error':
                    return ([], {})
                elif obj['status'] != 'ok':
                    obj = None
                    continue

            orgs = obj['results']['organizations']
            locs = obj['results']['places']

        return (orgs, locs)
