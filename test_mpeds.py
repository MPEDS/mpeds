import unittest
from mpeds.open_ended_coders import *


class TestSizeCoder(unittest.TestCase):

	def setUp(self):
		self.coder = SizeCoder()

	def test_500_protesters(self):
		self.assertEqual(self.coder.getProtestSize('500 protesters', as_str = True), '500')

	def test_two_protesters(self):
		self.assertEqual( self.coder.getProtestSize('two protesters', as_str = True), '2')


class TestLocationCoder(unittest.TestCase):

	def setUp(self):
		self.coder = LocationCoder()

	def test_canada(self):
		self.assertEqual(self.coder.getLocation('across Canada'), 'Canada')



if __name__ == '__main__':
	unittest.main()