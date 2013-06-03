from django.utils import unittest
import django.test

from stjornbord.student.parser import InnaParser, InnaParserException
from stjornbord.student.models import Student, Klass, LegalGuardian

class InnaParserTest(django.test.TestCase):
	def testParserValid(self):
		self.assertEqual(Student.objects.count(), 0)
		self.assertEqual(Klass.objects.count(), 0)
		self.assertEqual(LegalGuardian.objects.count(), 0)

		# Import year 1
		parser = InnaParser("student/test_files/inna_year1.csv", pretend=False)
		parser.update()
		self.assertEqual(parser.stats["create"], 2)
		self.assertEqual(parser.stats["update"], 0)
		self.assertEqual(parser.stats["delete"], 0)

		self.assertEqual(Student.objects.count(), 2)
		self.assertEqual(Klass.objects.count(), 2)
		self.assertEqual(LegalGuardian.objects.count(), 4)

		# Import year 1 again, should update
		parser = InnaParser("student/test_files/inna_year1.csv", pretend=False)
		parser.update()

		self.assertEqual(parser.stats["create"], 0)
		self.assertEqual(parser.stats["update"], 2)
		self.assertEqual(parser.stats["delete"], 0)

		# Import year 2, should remove 1, update 1, delete 1
		parser = InnaParser("student/test_files/inna_year2.csv", pretend=False)
		parser.update()

		self.assertEqual(parser.stats["create"], 1)
		self.assertEqual(parser.stats["update"], 1)
		self.assertEqual(parser.stats["delete"], 1)

		self.assertEqual(Student.objects.count(), 3)
		self.assertEqual(Klass.objects.count(), 4)
		self.assertEqual(LegalGuardian.objects.count(), 6)

		# Import year 2 again, should update
		parser = InnaParser("student/test_files/inna_year2.csv", pretend=False)
		parser.update()

		self.assertEqual(parser.stats["create"], 0)
		self.assertEqual(parser.stats["update"], 2)
		self.assertEqual(parser.stats["delete"], 0)

		# Verify that the prev student has been deactivated
		self.assertEqual(Student.objects.filter(status__active=True).count(), 2)
		self.assertEqual(Student.objects.filter(status__active=False).count(), 1)


	def testParserMissingHeader(self):
		# Import year 1
		parser = InnaParser("student/test_files/inna_invalid_missing_header.csv", pretend=False)
		with self.assertRaises(InnaParserException):
			parser.update()


	def testParserMissingValue(self):
		# Import year 1
		parser = InnaParser("student/test_files/inna_invalid_missing_value.csv", pretend=False)
		with self.assertRaises(InnaParserException):
			parser.update()


	def testParserIncorrectSeparator(self):
		# Import year 1
		parser = InnaParser("student/test_files/inna_invalid_separator.csv", pretend=False)
		with self.assertRaises(InnaParserException):
			parser.update()

