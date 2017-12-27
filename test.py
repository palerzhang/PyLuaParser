# -*- coding: utf-8 -*-
import sys
import math
import string
import PyLuaTblParser

# test

p1 = PyLuaTblParser.PyLuaTblParser()
p2 = PyLuaTblParser.PyLuaTblParser()
p3 = PyLuaTblParser.PyLuaTblParser()
p1.loadLuaTable("testcaseraw.lua")
d1 = p1.dumpDict()
p2.loadDict(d1)
p2.dumpLuaTable("testout.lua")
p3.loadLuaTable("testout.lua")
d3 = p3.dumpDict()
print d3
