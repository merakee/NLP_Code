#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	None.some_method_none_does_not_know_about()
except Exception as ex:
	print ex.__class__
	print ex.args[0]
