import ast
str1 = '{"name": "hayubchjd"}'
d = ast.literal_eval(str1)
d['name'] = "abshcbakjn"
c = str(d)
print(str1,type(str1))
print(c,type(d))
