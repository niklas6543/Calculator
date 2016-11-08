import re, sys
import math, pprint

RE_FLOAT = re.compile('^(-?[0-9]+)(\.[0-9]+)?$')

class FormelParseException(Exception):
	pass

class FormelCalculateException(Exception):
	pass

class Variable:
	def __init__(self, value):
		self.value = value
	
	def __repr__(self):
		return "<Variable %s>" % (self.value,)
	
	def __eq__(self, other):
		if not isinstance(other, Variable):
			return False

		return self.value == other.value
		
class Formel:
	
	FUNCTIONS = {
		'sin': (1, lambda a:math.sin(a)),
		'cos': (1, lambda a:math.cos(a)),
		'tan': (1, lambda a:math.tan(a)),
		'log': (2, lambda a,b:math.log(a,b)),
	}


	OPERATOREN = {
		'+':	lambda a,b:a+b,
		'-':	lambda a,b:a-b,
		'*':	lambda a,b:a*b,
		'/':	lambda a,b:a/b,
		'^':	lambda a,b:a**b,
	}
	


	def __init__(self, formel, debug=False):
		self._formel = formel
		self._debug = debug

	def log(self, message):
		if self._debug:
			sys.stderr.write(pprint.pformat(message, indent=4))
	
	def asList(self):
		"""
		The String will be split in mathematic operators and numbers.
		As a result, the function gives a list of these.

		Invalid input will be raise an ValueError!

		"""
		formel = []
		number = ''
		content = ''
		#the loop collects operators, numbers and spaces
		#here will build the formel list
		for s in self._formel+' ':
			if s.isalpha():
				content+=s
				
			else:
					
				if content != '':
					if content in Formel.FUNCTIONS:
						formel.append(content)
						content = ''
					else:
						if s.isdigit() or s in '.':
							content += s
							s = ' '
						else:
							formel.append(Variable(content))
							content = ''
				
				if s in '+-*/()^,':
					if number != '':
						formel.append(number)
					formel.append(s)
					number = ''
				elif s.isdigit() or s in '.':
					number += s
				elif s.isspace():
					if number != '':
						formel.append(number)
					number = ''

		return [(float(f) if not isinstance(f, Variable) and RE_FLOAT.match(f) else f) for f in formel]

	def asUPN(self):
		"""
		This function changes the formel list into a polish notation structure.
		It returns the result as a new list named output.

		"""
		formel = self.asList()
		number = None 
		op = {'+': 1, '-': 1, '*': 2 , '/': 2, '(': -1, ')': -1, '^': 3}
		output = []
		stack = []
		lastf = None
		sign = None
		func = False

		for f in formel:
			if isinstance(f, str):
				if f in Formel.OPERATOREN:
					if isinstance(lastf, str) and lastf in Formel.OPERATOREN or lastf == '(':
						if f in '+-':
							if not sign is None:
								raise FormelParseException('only one sign')
							sign = f
						else:
							raise FormelParseException('duplicate operator found')
					else:
						#check the stack list of right operators
						while len(stack) > 0 and op[stack[-1]] > op[f]:
							output.append(stack.pop())
						stack.append(f)
				elif f == '(':
					stack.append(f)
				elif f == ')':
					if not '(' in stack :
						raise FormelParseException('right parenthesis found, not left')
					
					while len(stack) > 0:
						p = stack.pop()

						if p == '(':
							break
						
						output.append(p)
					
					if len(stack) > 0 and stack[-1] in Formel.FUNCTIONS:
						output.append(stack.pop())

					func = False
				elif f == ',':
					while len(stack) > 0 and stack[-1] != '(':
						output.append(stack.pop())

				elif f in Formel.FUNCTIONS and func is False:
					stack.append(f)
					func = True
				else:
					raise FormelParseException('syntax error near: '+f)
			else:
				# if the first f is a sign
				if isinstance(lastf, str):
					if lastf in Formel.OPERATOREN and len(output) == 0:
						sign = lastf	
						stack.pop()

				if sign == '-':
					if isinstance(f, Variable):
						raise FormelParseException("'-' <Variable> does not match")
					output.append(-f)
					sign = None
				else:
					output.append(f)

			lastf = f
		
		if not ')' in stack and '(' in stack:
			raise FormelParseException('left parenthesis found, not right')
		# the stack list will be reverse add on the output list
		output.extend(reversed(stack))
		
		if output[-1] in Formel.OPERATOREN and len(output)<3:
			raise FormelParseException('syntax error near: '+output[-1])
		
		self._UPN = output		
		return self._UPN 
		
	def asTree(self):
		self.asUPN()

		stack = []
		for p in self._UPN:
			if isinstance(p, str) and p in Formel.OPERATOREN:
				if len(stack) > 1:
					b = stack.pop()
					a = stack.pop()
	
					stack.append((p, a, b))
				else:
					a = stack.pop()
					stack.append((p, a))
			elif isinstance(p, str) and p in Formel.FUNCTIONS:
				args = []
	
				for i in range(Formel.FUNCTIONS[p][0]):
					args.append(stack.pop())
				args.reverse()
				stack.append(tuple([p]+args))
			else:
				stack.append(p)
		
		return stack[0]
	
	def asGraphViz(self):
		"""
		This function creates code for a tree graphic.
		As content they need the UPN tuple.
	
		"""
		
	#	self.log(stack, self._UPN)	
		
		def _recursegraph(tree, last=0): 
			"""
			The function goes recursive through the UPN tuple.
			"""
			graph = []
		
			if isinstance(tree, float) or isinstance(tree, Variable):
				idx = last
				last+= 1
	
				graph.append('%s [label="%s"];' % (idx, tree))
				
				return (graph, idx, last)
			
			op = tree[0] 
				
			idxOp = last
			last+= 1
			graph.append('%s [label="%s"];' % (idxOp, op))
			
			for (i, t) in enumerate(tree[1:]):
				(childGraph, idx, last) = _recursegraph(t, last)
				graph.extend(childGraph)
	
				graph.append('%s -> %s [label="%i"];' % (idxOp, idx, i+1))
					
			return (graph, idxOp, last)
		
		tree = self.asTree()	
		graph = _recursegraph(tree)[0]
		self.log(graph)
		self.log(tree)
		graphcode = """
digraph formel 
{ 
%s
}
		""" % ('\n'.join(graph))
	
		return graphcode



	def calculate(self, **kwargs):
		"""
		Here will be calculate the result with the right
		operators and functions.
		"""
		self.asUPN()
		stack = []
		
		for p in self._UPN:
			if isinstance(p, str) and p in Formel.OPERATOREN:
				b = stack.pop()
				a = stack.pop()

				if p == '^':
					if b != int(b) and a <= 0:
						raise FormelCalculateException('square root from negative float')
					
				stack.append(Formel.OPERATOREN[p](a,b))
	
			elif isinstance(p, str) and p in Formel.FUNCTIONS:
				(count, calcfunc) = Formel.FUNCTIONS[p]
				
				args = []

				for i in range(count):
					args.append(stack.pop())
				stack.append(calcfunc(*args))

			elif isinstance(p, Variable):
				try:
					stack.append(kwargs[p.value])
				except KeyError:
					raise FormelCalculateException("%s is not defined" % (p.value))
			else:
				stack.append(p)

		if len(stack) > 0:
			return stack[0]
		else:
			raise FormelCalculateException("result is empty")
		

if '--graphviz' in sys.argv[1:]:
	f = Formel('10*a-x24x')
	print(f.asGraphViz())
	sys.exit()




if __name__ == "__main__":

	#print(Formel('sin cos3+4').asUPN())
	#print(Formel('cos3)').asUPN())
	print(Formel('10*a-x24xsin+1').asUPN())
	#calculate(a = 2, x24xsin = 1))
	#calculate(a = 42, x = 1))
	
	for (formel, asList, asUPN, asTree, result) in [
		(
			'3+4 * 5+8',
			[3.0, '+', 4.0, '*', 5.0, '+', 8.0],
			[3.0, 4.0, 5.0, '*', 8.0, '+', '+'],
			('+', 3.0, ('+', ('*', 4.0, 5.0), 8.0)),
			31.0,
		),
		(
			'(log(5,3)-6)+(sin(3)/(5-2))',
			['(', 'log', '(', 5.0, ',', 3.0, ')', '-', 6.0, ')', '+', '(', 'sin', '(', 3.0, ')', '/', '(', 5.0, '-', 2.0, ')', ')'],
			[5.0, 3.0, 'log', 6.0, '-', 3.0, 'sin', 5.0, 2.0, '-', '/', '+'],
			('+', ('-', ('log', 5.0, 3.0), 6.0), ('/', 3.0, ('-', 5.0, 2.0))),
			-4.317393805514015,
		),
		(
			'4+-5*6',
			[4, '+', '-', 5, '*', 6],
			[4, -5,  6, '*', '+'],
			('-', -5, 4),
			-26,
		),
	]:
		f = Formel(formel)
		
		assert f.asList() == asList, f.asList()
		assert f.asUPN() == asUPN, f.asUPN()
		#assert f.asTree() == asTree, print(f.asTree())
		#assert f.calculate() == result, f.calculate()
