# -*- coding: utf-8 -*-
import sys
import math
import string

numberHead = ["0","1","2","3","4","5","6","7","8","9","-"]
blanks = [" ", "\t", "\n"]

str0 = open("verysimple.lua").read()

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
    former = 0
    is_list = True
    lst = []
    for i in range(len(s)):
        if (s[i] == '{' and not in_quote): #left big bracket
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
            if (value == None): # ignore
                continue
            if (key == None):
                ret[default_idx] = value
                default_idx += 1
            else:
                ret[key] = value
        return ret

def parseItem(s):
    #print("item : " + s)
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
    #print("item : " + s)
    if (s == ""):
        return "", None
    elif (s[0] == "["): # a key
        idx = 0
        in_quote = False
        for i in range(len(s)):
            if (s[i] == "]" and not in_quote):
                idx = i
                break
        if (idx <= 0):
            raise SyntaxError
        else:
            key = s[1:idx]
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
        return s[1:-1]
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

l = parse(str0)
print(l)

#dic = {"object with 1 member":-42}
#str3 = "{'root' : {99 : -43, 'd' : {}}}"
#print(dic)




