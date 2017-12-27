完成了所有基本要求
主体代码：PyLuaTblParser.py
测试代码：test.py
测试文件：testcaseraw.lua（群内大佬提供的case）

主体代码说明：
1.解析lua table字符串的辅助函数在
#-- All helpers for parse lua table
#-- END all helpers for parse lua table
之间
lua table = { inner } \parse
	inner = item0, item1, item2...	\parseInner
		itemi = 
			key=value \parseDictItem
				key = ["..."] 
					or [number] 
					or string 
					or nothing(defalut index)
				value = "..." 
					or number 
					or bool 
					or nil 
					or lua table
			or value	\ parseItem
				value = "..." 
					or number 
					or bool 
					or nil 
					or lua table

2.解析字典的辅助函数在
#-- All helpers for parse dictionary
#-- END all helpers for parse dictionary
之间
dict = {key : value} \parseDict
	key = number->[number] 
		or string->["string"]
	value = dict
		or string->"string"
		or number->number
		or bool
		or list (None in here)	\parseList

3.类主体
	见题目要求


测试说明：
运行 test.py
会先读取testcaseraw.lua中的lua并解析成字典
然后将字典解析成lua table字符串并保存
最后将保存的lua table字符串读取后重新解析成字典