import re,json
def parse(s):
 t=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s);stack=[];root=None
 for x in t:
  if x=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif x==')':root=stack.pop()
  else:stack[-1].append(x)
 return root
def ser(v):return '('+' '.join(map(ser,v))+')' if isinstance(v,list) else v
def ch(v,k):return next((x for x in v if isinstance(x,list) and x[0]==k),None)
