#!/usr/bin/env python
# -*- coding: utf-8 -*-

# text processing in python
# Bijit Halder
# Merakee LLC.
# Aug 201

import sys
import pydoc
import string 

def output_help_to_file(request):
	filepath  = request + "_package_info.txt"
	f = file(filepath, 'w')
	sys.stdout = f
	pydoc.help(request)
	f.close()
	sys.stdout = sys.__stdout__
	return


# commend line option
if __name__ == '__main__':
	request = raw_input("Enter package name: ")
	output_help_to_file(request)



