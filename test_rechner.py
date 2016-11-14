from rechner import *
import unittest



class TestConvert(unittest.TestCase):
	def test_asList(self):
		self.assertEqual(Formel('12+1').asList(), [12, '+', 1])
		self.assertEqual(Formel('12++1').asList(), [12, '+', '+', 1])
		self.assertEqual(Formel('12 + 1').asList(), [12, '+', 1])
		self.assertEqual(Formel('12 + 1 5').asList(), [12, '+', 1, 5])

	def test_asUPN(self):
		self.assertEqual(Formel('3+4 * 5+8').asUPN(), [3.0, 4.0, 5.0, '*', 8.0, '+', '+'])
		self.assertEqual(Formel('(log(5,3)-6)+(sin(3)/(5-2))').asUPN(),  [5.0, 3.0, 'log', 6.0, '-', 3.0, 'sin', 5.0, 2.0, '-', '/', '+'])
		self.assertEqual(Formel('4+-5*6').asUPN(),  [4, -5,  6, '*', '+'])
		self.assertEqual(Formel('-4+5').asUPN(),  [-4, 5, '+'])
		self.assertEqual(Formel('10*a-x245').asUPN(), [10.0, Variable('a'), '*', Variable('x245'), '-'])
		self.assertEqual(Formel('10*a-x245sin').asUPN(), [10.0, Variable('a'), '*', Variable('x245sin'), '-'])
		self.assertEqual(Formel('10a^2-2').asUPN(), [10.0, Variable('a'), 2.0, '^', '*', 2.0, '-'])
		self.assertEqual(Formel('10a-2').asUPN(), [10.0, Variable('a'), '*', 2.0, '-'])

	def test_calaculate(self):
		self.assertEqual(Formel('4^2').calculate(),  16)
		self.assertEqual(Formel('16^(1/2)').calculate(),  4)
		self.assertEqual(Formel('-10^(-1)').calculate(),  -0.1)
		self.assertEqual(Formel('-10^-1').calculate(),  -0.1)
		self.assertEqual(Formel('10*a-x24x+1').calculate(a = 2, x24x = 1), 18)

		
	def test_error(self):
		upn = lambda f:Formel(f).asUPN()
		calc = lambda f:Formel(f).calculate(a = 42)
		self.assertRaisesRegex(FormelParseException, "right parenthesis found, not left", upn, "3+4)")
		self.assertRaisesRegex(FormelParseException, "syntax error near: *", upn, "7*")
#		self.assertRaisesRegex(FormelParseException, "duplicate operator found", upn, "(3*/")
		self.assertRaisesRegex(FormelParseException, "syntax error near: /", upn, "(3*/")
		self.assertRaisesRegex(FormelParseException, "left parenthesis found, not right", upn, "sin(")
		self.assertRaisesRegex(FormelParseException, "right parenthesis found, not left", upn, "cos)")
		self.assertRaisesRegex(FormelParseException, "only one sign", upn, "1---1")
		self.assertRaisesRegex(FormelCalculateException, "square root from negative float", calc, "-10^(1/2)")
		self.assertRaisesRegex(FormelParseException, "'-' <Variable> does not match", calc, "10--a")
		self.assertRaisesRegex(FormelCalculateException, "x is not defined", calc, "10*a-x")
		self.assertRaisesRegex(FormelParseException, "syntax error near: +", upn, "a^2+")
		self.assertRaisesRegex(FormelParseException, "unknown symbol like: \$", upn, "a^2$")

if __name__ == "__main__":
	unittest.main()
