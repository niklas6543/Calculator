from rechner import Formel, FormelParseException
import unittest



class TestConvert(unittest.TestCase):
	def test_asList(self):
		self.assertEqual(Formel('12+1').asList(), [12, '+', 1])
		self.assertEqual(Formel('12++1').asList(), [12, '+', '+', 1])
		self.assertEqual(Formel('12 + 1').asList(), [12, '+', 1])
		self.assertEqual(Formel('12 + 1 5').asList(), [12, '+', 1, 5])
	
		
	def test_error(self):
		upn = lambda f:Formel(f).asUPN()
		self.assertRaisesRegex(FormelParseException, "right parenthesis found, not left", upn, "3+4)")
		self.assertRaisesRegex(FormelParseException, "syntax error near: *", upn, "7*")
		self.assertRaisesRegex(FormelParseException, "duplicate operator found", upn, "(3*/")
		self.assertRaisesRegex(FormelParseException, "left parenthesis found, not right", upn, "sin(")
		self.assertRaisesRegex(FormelParseException, "only one sign", upn, "1---1")

if __name__ == "__main__":
	unittest.main()
