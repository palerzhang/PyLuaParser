# -*- coding: utf-8 -*-
import sys
import math
import string

#-- All helpers for parse lua table

numberHead = ["0","1","2","3","4","5","6","7","8","9","-"]
blanks = [" ", "\t", "\n"]
escaped = {
    "t" : "\t",
    "n" : "\n",
    "b" : "\b",
    "f" : "\f",
    "r" : "\r",
    "\\" : "\\",
    "\"" : "\"",
    "\'" : "\'"
}

def parse(s):
    s = s.strip()
    if (s[0] == '{' and s[-1] == '}'):
        inner = s[1:-1].strip()
    else:
        raise SyntaxError
    
    return parseInner(inner)

def parseInner(s):
    cnt_big_bracket = 0
    cnt_mid_bracket = 0
    cnt_double_quote = 0
    cnt_single_quote = 0
    in_quote = False
    in_comment = False
    in_multi_comment = False
    in_escape = False
    former = 0
    is_list = True
    lst = []
    for i in range(len(s)):
        if (in_escape): #skip this char, wait for later parsing
            in_escape = False
            continue
        if (s[i] == "\\"): #escape
            in_escape = True
            continue
        if (in_comment): #if in comment, skip all except \n
            if (s[i] == '\n'):
                former = i+1
                in_comment = False
            continue
        if (in_multi_comment): #if in multi-lines comment, skip all except ]]
            if (s[i] == ']' and i+1 < len(s) and s[i+1] == ']'):
                former = i+1
                in_multi_comment = False
        elif (s[i] == '{' and not in_quote): #left big bracket
            cnt_big_bracket += 1
        elif (s[i] == '}' and not in_quote): #right big bracket
            if (cnt_big_bracket <= 0):
                raise SyntaxError
            cnt_big_bracket -= 1
        elif (s[i] == "\""): #quote, change in_quote
            if (in_quote):
                cnt_double_quote -= 1
            if (not in_quote):
                cnt_double_quote += 1
            in_quote = not in_quote
        elif (s[i] == '=' and not in_quote and cnt_big_bracket == 0 and cnt_mid_bracket == 0):
            is_list = False
        elif (s[i] == ',' and not in_quote and cnt_big_bracket == 0 and cnt_mid_bracket == 0):
            # comma, split
            lst.append(s[former:i])
            former = i+1
        elif (s[i] == '-' and not in_multi_comment and not in_comment and not in_quote and cnt_big_bracket == 0): #maybe a comment
            if (i+1 < len(s) and s[i+1] == '-'): #if another dash and not in quote
                if (i+2 < len(s) and s[i+2] == '[' and i+3 < len(s) and s[i+3] == '['): 
                #if a multi-line token
                    in_multi_comment = True
                    continue
                else:
                # otherwise, simple comment
                    in_comment = True
                    continue #skip those chars

    lst.append(s[former:])
    if (is_list):
        ret = []
        for item in lst:
            value = parseItem(item)
            if (value == ""):
                continue
            ret.append(value)
        return ret
    else:
        ret = {}
        default_idx = 1
        for item in lst:
            key, value = parseDictItem(item)
            if (value == None): # ignore but count plus 1
                default_idx += 1
                continue
            if (key == None):
                ret[default_idx] = value
                default_idx += 1
            else:
                ret[key] = value
        return ret

def parseItem(s):
    s = s.strip()
    if (s == ""):
        return ""
    elif (s[0] == "\""): # string
        return parseString(s)
    elif(s[0] == '{' and s[-1] == '}'): # table or list
        return parseInner(s[1:-1])
    elif(s[0] in numberHead): # number
        return parseNumber(s)
    elif(s[0] == 't' or s[0] == 'f'): # bool
        return parseBool(s)
    elif(s[0] == 'n'): # nil
        return parseNil(s)
    else:
        raise SyntaxError

def parseDictItem(s):
    s = s.strip()
    if (s == ""):
        return "", None
    elif (s[0] == "["): # a key
        idx = 0
        in_quote = False
        in_escape = False
        for i in range(len(s)):
            if (in_escape): #skip this char, wait for later parsing
                in_escape = False
                continue
            if (s[i] == "\\"): #escape
                in_escape = True
                continue
            if (s[i] == "\""):
                in_quote = not in_quote
            elif (s[i] == "]" and not in_quote):
                idx = i
                break
        if (idx <= 0):
            raise SyntaxError
        else:
            key = s[1:idx]
            #print(key)
            if (key[0] == "\""):
                key = parseString(key)
            elif (key[0] in numberHead):
                key = parseNumber(key)
            else:
                raise SyntaxError
            left = s[idx+1:].strip()
            if (left[0] != "="):
                raise SyntaxError
            else:
                left = left[1:].strip()
                return key, parseItem(left)
            
    elif (s[0:3] == "nil"):
        if (len(s) != 3):
            raise SyntaxError
        else:
            return None, parseNil(s)
        
    elif (s[0:4] == "true"):
        if (len(s) != 4):
            raise SyntaxError
        else:
            return None, parseBool(s)
        
    elif (s[0:5] == "false"):
        if (len(s) != 5):
            raise SyntaxError
        else:
            return None, parseBool(s)
            
    elif (s[0].isalpha()): # a string
        idx = 0
        for i in range(len(s)):
            if (s[i].isalpha() or s[i] == "_" or s[i].isdigit()):
                continue
            elif (s[i] == "=" or s[i] in blanks):
                idx = i
                break
            else:
                raise SyntaxError
        if (idx <= 0):
            raise SyntaxError
        else:
            key = s[0:idx].strip()
            left = s[idx:].strip()
            if (left[0] != "="):
                raise SyntaxError
            else:
                left = left[1:].strip()
                return key, parseItem(left)
    else:
        return None, parseItem(s)

def parseString(s):
    s = s.strip()
    if (s[-1] == "\""): # \ then 
        s = s[1:-1]
        ret = ""
        size = len(s)
        in_escape = False
        for i in range(size):
            if (in_escape):
                if (s[i] in escaped):
                    ret += escaped[s[i]]
                else:
                    ret += "\\" + s[i]
                in_escape = False
            else:
                if (s[i] == "\\"): # get a escape
                    in_escape = True
                else:
                    ret += s[i]
        return ret
    else:
        raise SyntaxError

def parseNumber(s):
    s = s.strip()
    count_minus = s.count("-")    
    if (count_minus == 0 or (count_minus == 1 and s[0] == "-")):
        count_dot = s.count(".")
        if (count_dot == 0):
            if (s[:1] == "0x" or s[:2] == "-0x" or s[:2] == "+0x"):
                return int(s,16)
            else:
                return int(s)
        elif (count_dot == 1):
            if (s[:1] == "0x" or s[:2] == "-0x" or s[:2] == "+0x"):
                return float.fromhex(s,16)
            else:
                return float(s)
        else:
            raise SyntaxError
    elif (s.count("e") == 1 or s.count("E") == 1):
        if (s[:1] == "0x" or s[:2] == "-0x" or s[:2] == "+0x"):
            return float.fromhex(s,16)
        else:
            return float(s)
    else:
        raise SyntaxError
                
def parseBool(s):
    s = s.strip()
    if (s == "false"):
        return False
    elif (s == "true"):
        return True
    else:
        raise SyntaxError

def parseNil(s):
    s = s.strip()
    if (s == "nil"):
        return None
    else:
        raise SyntaxError

#-- END all helpers for parse lua table
#-- All helpers for parse dictionary

escapedRev = {
    "\t" : "\\t",
    "\n" : "\\n",
    "\b" : "\\b",
    "\f" : "\\f",
    "\r" : "\\r",
    "\\" : "\\\\",
    "\"" : "\\\"",
    "\'" : "\\\'"
}

def parseStringRev(s):
    ret = ''
    for i in range(len(s)):
        if (s[i] in escapedRev):
            ret += escapedRev[s[i]]
        else:
            ret += s[i]
    return ret

def parseBoolRev(v):
    if (v):
        return "true"
    else:
        return "false"

def parseList(l):
    if (len(l) == 0):
        return "{}"
    s = "{"
    for value in l:
        strinloop = '' # result of a loop
        valuestring = '' # value
        if (type(value) == type({})): #value is a dictionary
            valuestring = parseDict(value)
        elif (type(value) == type(False)): #value is a bool
            valuestring = parseBoolRev(value)
        elif (type(value) == type(0) or type(value) == type(0.1)): #value is a number
            valuestring = str(value)
        elif (type(value) == type("s")): #value is a string
            valuestring = "\"" + parseStringRev(value) + "\""
        elif (type(value) == type([])): #a list !
            valuestring = parseList(value)
        elif (value == None): #None to nil
            valuestring = "nil"
        else: # skip otherwise
            continue
        strinloop = strinloop + valuestring + ","
        s = s + strinloop
    s = s[:-1]
    s += "}"
    return s

def parseDict(d):
    if (len(d) == 0):
        return "{}"
    s = "{"
    for key, value in d.items():
        strinloop = '' # result of a loop
        keystring = '' # key
        if (type(key) == type(0) or type(key) == type(0.1)): #key is a number
            keystring = '[' + str(key) + ']'
        elif (type(key) == type("s")): #key is a string
            keystring = "[\"" + parseStringRev(key) + "\"]"
        else: # skip otherwise
            continue
        strinloop = strinloop + keystring + "="
        valuestring = '' # value
        if (type(value) == type({})): #value is a dictionary
            valuestring = parseDict(value)
        elif (type(value) == type(False)): #value is a bool
            valuestring = parseBoolRev(value)
        elif (type(value) == type(0) or type(value) == type(0.1)): #value is a number
            valuestring = str(value)
        elif (type(value) == type("s")): #value is a string
            valuestring = "\"" + parseStringRev(value) + "\""
        elif (type(value) == type([])): #a list !
            valuestring = parseList(value)
        else: # skip otherwise
            continue
        strinloop = strinloop + valuestring + ","
        s = s + strinloop
    s = s[:-1]
    s += "}"
    return s

#-- END all helpers for parse dictionary

class PyLuaTblParser:

    def __init__(self):
        self.data = {}
        self.lua = ""

    def load(self, s):
        self.lua = s
        self.data = parse(s)

    def dump(self):
        return self.lua

    def loadLuaTable(self, f):
        filedata = open(f).read()
        self.load(filedata)

    def dumpLuaTable(self, f):
        open(f,"w").write(self.lua)

    def loadDict(self, d):
        self.data = d
        self.lua = parseDict(d)

    def dumpDict(self):
        return self.data

