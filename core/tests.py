from django.test import TestCase
from core.views import *

# We could add many more tests here. For example:
# more tests with invalid data (non numeric values for currency, missing values,)
# large files
# tests to check if DB created the expected records
class  TestViews(TestCase):

	# Empty file
	def test_empty_file(self):
		with open('empty.csv') as csvfile:
			results = handle_file(csvfile)
			self.assertEqual(results['error'], "Empty file")

	# Imported file doesn't have the expected number of fields
	def test_incorrect_num_headers(self):
		with open('incorrect_num_headers.csv') as csvfile:
			results = handle_file(csvfile)
			self.assertEqual(results['error'], "Incorrect number of headers")

	# CSV file has negative values
	def test_invalid_values(self):
		with open('invalid_values.csv') as csvfile:
			results = handle_file(csvfile)
			self.assertEqual(results['error'], "Negative tax amounts are not allowed")