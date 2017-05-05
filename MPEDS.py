
import pandas as pd 
import numpy as np

from sklearn.externals import joblib

class MPEDS:
	def __init__(self):
		''' Constructor. '''
		self.vect = joblib.load("../input/haystack-vect_all-source_2016-03-21.pkl")
		self.clf  = joblib.load("../input/haystack_all-source_2016-03-21.pkl")


	def vectorize(self, text):
		''' '''
		return self.vect.transform(text)

	def haystack(self, X):
		''' '''
		return self.clf.predict(X)



