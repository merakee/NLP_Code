#!/usr/bin/env python
# -*- coding: utf-8 -*-

class TriangleError(RuntimeError):
    pass

def triangle(a,b,c):
	if (a+b) <= c or (b+c) <= a or (a+c) <= b:
	 	raise TriangleError, "Invalid size" 


	if a==b and b==c:
		return 'equilateral'
	elif a==b or b==c or a==c:
	 	return 'isosceles'
	else:
	 	return 'scalene'

