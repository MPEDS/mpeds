import unittest
from mpeds.open_ended_coders import *


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
					self.coder.getSize('a crowd of' + key, as_str = True),
					str(value)
					)

class TestLocationCoder(unittest.TestCase):

	def setUp(self):
		self.coder = LocationCoder()

	def test_canada(self):
		self.assertEqual(self.coder.getLocation('across Canada'), 'Canada')



if __name__ == '__main__':
	unittest.main()
