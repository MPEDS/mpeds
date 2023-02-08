
import pandas as pd
import numpy as np

from sklearn.externals import joblib
from mpeds.open_ended_coders import *

from pkg_resources import resource_filename

class MPEDS:
    def __init__(self):
        ''' Constructor. '''

        self.hay_clf     = None
        self.hay_vect    = None
        self.form_clf    = None
        self.form_vect   = None
        self.issue_clf   = None
        self.issue_vect  = None
        self.issue_reg = None
        self.target_clf  = None
        self.target_vect = None

        self.size_clf = None
        self.location_clf = None
        self.smo_clf = None


    def loadHaystack(self):
        ''' Load haystack classifiers. '''
        ## load vectorizer
        if not self.hay_vect:
            print('Loading vectorizer...')
            self.hay_vect = joblib.load(resource_filename(__name__, 'classifiers/haystack-vect_all-source_2017-05-24.pkl'))

        if not self.hay_clf:
            print('Loading classifer...')
            self.hay_clf = joblib.load(resource_filename(__name__, 'classifiers/haystack_all-source_2017-05-24.pkl'))


    def getLede(self, text):
        '''
        Get the lede sentence for the text. Splits on <br/>

        :param text: text(s) to extracte lede from
        :type text: string or pandas series of strings

        :return: ledes
        :rtype: pandas series
        '''

        def _first_sentence(text):
            sentences = text.split("<br/>")
            return sentences[0]

        if isinstance(text, basestring):
            text = pd.Series(text)

        sentences = text.apply(_first_sentence)

        return sentences


    def haystack(self, text):
        '''
        Perform haystack classification task.

        :param text: documents to be classified
        :type text: string or pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        if not self.hay_vect and not self.hay_clf:
            self.loadHaystack()

        if isinstance(text, basestring):
            text = pd.Series(text)

        print('Vectorizing...')
        X = self.hay_vect.transform(text)

        print('Predicting...')
        y = self.hay_clf.predict(X)
        return y


    def haystackProbs(self, text):
        """ Returns haystack probabilites for the Logistic Regression classifier,
            rather than predictions. """
        if not self.hay_vect and not self.hay_clf:
            self.loadHaystack()

        print('Vectoring...')
        X = self.hay_vect.transform(text)

        print('Predicting...')
        y = [x[1] for x in self.hay_clf.estimators_[1].predict_proba(X)]

        return y


    def getForm(self, text):
        '''
        Classify protest form.

        :param text: documents to perform classification task on
        :type text: string or pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.form_vect:
            print('Loading form vectorizer...')
            self.form_vect = joblib.load(resource_filename(__name__, 'classifiers/form-vect_2017-05-23.pkl'))

        print('Vectorizing...')
        X = self.form_vect.transform(text)

        ## load classifier
        if not self.form_clf:
            print('Loading form classifier...')
            self.form_clf = joblib.load(resource_filename(__name__, 'classifiers/form_2017-05-23.pkl'))

        print('Predicting...')
        y = self.form_clf.predict(X)

        return y


    def getFormProb(self, text):
        '''
        Get probabilities associated with each form.

        :param text: text(s) to get form probabilities for
        :type text: string or pandas series of strings

        :return: tuple containing probabilities and classes
        :rtype: tuple

        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.form_vect:
            print('Loading form vectorizer...')
            self.form_vect = joblib.load(resource_filename(__name__, 'classifiers/form-vect_2017-05-23.pkl'))

        print('Vectorizing...')
        X = self.form_vect.transform(text)

        ## load classifier
        if not self.form_clf:
            print('Loading form classifier...')
            self.form_clf = joblib.load(resource_filename(__name__, 'classifiers/form_2017-05-23.pkl'))

        print('Predicting form probabilities...')
        probs    = self.form_clf.predict_proba(X)

        return (probs, self.form_clf.classes_)


    def getIssue(self, text):
        '''
        Classify protest issue.

        :param text: documents to perform classification task on
        :type text: string or pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.issue_vect:
            print('Loading issue vectorizer...')
            self.issue_vect = joblib.load(resource_filename(__name__, 'classifiers/issue-vect_2017-05-23.pkl'))

        print('Vectorizing...')
        X = self.issue_vect.transform(text)

        ## load classifier
        if not self.issue_clf:
            print('Loading issue classifier...')
            self.issue_clf = joblib.load(resource_filename(__name__, 'classifiers/issue_2017-05-23.pkl'))

        print('Predicting...')
        y = self.issue_clf.predict(X)

        return y

    def getIssueProb(self, text, scale = True):
        '''
        Get probabilities associated with each issue. Calculated from Platt's method.

        :param text: text(s) to get form probabilities for
        :type text: string or pandas series of strings

        :param scale: logical whether probabilities should be scaled to sum to 1. Defaults to true
        :type scale: boolean

        :return: tuple containing probabilities and classes
        :rtype: tuple

        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        # load vectorizer
        if not self.issue_vect:
            print('Loading issue vectorizer...')
            self.issue_vect = joblib.load(resource_filename(__name__, 'classifiers/issue-vect_2017-05-23.pkl'))

        # load classifier
        if not self.issue_clf:
            print('Loading issue classifier...')
            self.issue_clf = joblib.load(resource_filename(__name__, 'classifiers/issue_2017-05-23.pkl'))

        # load regression models
        if not self.issue_reg:
            print('Loading regression models for estimating issue probabilities')
            self.issue_reg = joblib.load(resource_filename(__name__, 'classifiers/issue_regression_models_2017-07-24.pkl'))


        print('Vectorizing...')
        X = self.issue_vect.transform(text)

        # get SVM margins, and use as input to individual regression models
        svm_margins = pd.DataFrame( self.issue_clf.decision_function(X) )
        svm_margins.columns = self.issue_clf.classes_

        probs = {}

        for category, regression_model in self.issue_reg.iteritems():
            category_probs = regression_model.predict_proba( svm_margins[category].reshape(-1, 1) )

            # function above gets probabilities for both class 0 and class 1 (never mind that they sum to 1...)
            # extract class 1 probabilities
            probs[category] = category_probs[:, 1]

        probs = pd.DataFrame(probs)

        # scale to sum to 1
        if scale:
            probs = probs.div(probs.sum(axis = 1), axis = 0)

        # set data return format to match other probability functions
        return (probs.values, np.array(probs.columns).astype('S32'))


    def getTarget(self, text):
        '''
        Classify protest target.

        :param text: documents to perform classification task on
        :type text: string or pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.target_vect:
            print('Loading target vectorizer...')
            self.target_vect = joblib.load(resource_filename(__name__, 'classifiers/target-vect_2017-06-27.pkl'))

        print('Vectorizing...')
        X = self.target_vect.transform(text)

        ## load classifier
        if not self.target_clf:
            print('Loading target classifier...')
            self.target_clf = joblib.load(resource_filename(__name__, 'classifiers/target_2017-06-27.pkl'))

        print('Predicting...')
        y = self.target_clf.predict(X)

        return y


    def getTargetProb(self, text):
        '''
        Get probabilities associated with each target.

        :param text: text(s) to get target probabilities for
        :type text: string or pandas series of strings

        :return: tuple containing probabilities and classes
        :rtype: tuple

        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.target_vect:
            print('Loading target vectorizer...')
            self.target_vect = joblib.load(resource_filename(__name__, 'classifiers/target-vect_2017-06-27.pkl'))

        print('Vectorizing...')
        X = self.target_vect.transform(text)

        ## load classifier
        if not self.target_clf:
            print('Loading target classifier...')
            self.target_clf = joblib.load(resource_filename(__name__, 'classifiers/target_2017-06-27.pkl'))

        print('Predicting target probabilities...')
        probs    = self.target_clf.predict_proba(X)

        return (probs, self.target_clf.classes_)


    def getSMO(self, text):
        '''
        Extract social movement organizations from text

        :param text: documents to perform coding task on
        :type text: string or pandas series of strings

        :return: extracted SMOs
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.smo_clf:
            self.smo_clf = SMOCoder()

        SMOs = text.apply(self.smo_clf.getSMO, args = [True])

        return SMOs

    def getSize(self, text):
        '''
        Extract protest from text

        :param text: documents to perform coding task on
        :type text: string or pandas series of strings

        :return: extracted sizes
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.size_clf:
            self.size_clf = SizeCoder()

        sizes = text.apply(self.size_clf.getSize, args = [True])

        return sizes

    def getLocation(self, text):
        '''
        Extract locations from text

        :param text: documents to perform coding task on
        :type text: string or pandas series of strings

        :return: extracted locations
        :rtype: pandas series
        '''

        if isinstance(text, basestring):
            text = pd.Series(text)

        if not self.location_clf:
            self.location_clf = LocationCoder()

        locations = text.apply(self.location_clf.getLocation, args = [True])
        # locations = text.apply(self.location_clf.getLocation)

        return locations
