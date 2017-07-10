import unittest
from mpeds.open_ended_coders import *
from mpeds.classify_protest import MPEDS
import pandas as pd


class TestSizeCoder(unittest.TestCase):

	def setUp(self):
		self.coder = SizeCoder()

		# define a number dictionary of sizes to test
		self.number_dictionary = {
			'five thousand': 5000,
			'five hundred': 500,
			'two hundred': 200,
			'two': 2
			}

	def test_protesters(self):
		for key, value in self.number_dictionary.iteritems():
			self.assertEqual(
				self.coder.getSize(key + ' protesters', as_str = True),
				str(value)
				)

	def test_crowd_of(self):
		for key, value in self.number_dictionary.iteritems():
			self.assertEqual(
				self.coder.getSize('a crowd of ' + key, as_str = True),
				str(value)
				)

class TestLocationCoder(unittest.TestCase):

	def setUp(self):
		self.coder = LocationCoder()

		self.locations = {
			'Canada': 'Canada, 60.10867, -113.64258',
			'the United States': 'United States, 39.76, -98.5',
			'London': 'London, England, United Kingdom of Great Britain and Northern Ireland, 51.50853, -0.12574',
			'Moscow': 'Moscow, Moskva, Russian Federation, 55.75222, 37.61556',
			'London, Ontario': 'London, Ontario, Canada, 42.98339, -81.23304',
			'Quito': 'Quito, Provincia de Pichincha, Republic of Ecuador, -0.22985, -78.52495',
			'New York City': 'New York City, New York, United States, 40.71427, -74.00597'
			}


	def test_across(self):
		for key, value in self.locations.iteritems():
			self.assertEqual(
				self.coder.getLocation('across ' + key, as_str = True),
				value
				)

class TestHaystack(unittest.TestCase):

	def setUp(self):

		self.mpeds_object = MPEDS()

	def test_negative(self):
		# run tests of strings that should not contain protests

		negative_strings = [
			'',
			'five geese attacked an elderly nun',
			'I ate fifty avocados'
			]

		for i in range(len(negative_strings)):

			self.assertEqual(
				self.mpeds_object.haystack(negative_strings[i])[0],
				0
				)

	def test_positive(self):
		positive_strings = [
			"500 protesters gathered outside of the senator's office to object against the proposed cuts"
			]

		for i in range(len(positive_strings)):

			self.assertEqual(
				self.mpeds_object.haystack(positive_strings[i])[0],
				1
				)



if __name__ == '__main__':
	unittest.main()
