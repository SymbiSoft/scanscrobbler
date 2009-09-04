__doc__='Power Clipboard tool for Pys60 by Atrant'
__name__='Power Clipboard tool for Pys60 by Atrant'

#
# History : works with 1st , 2nd and 3rd S60 devices !
#  4 Oct 2007 : clipboard file can be on other drives (c: , d: or e:)
#   slight changes by Cyke64
#
#

symbian = [0x0090,0x0091,0x0092,0x0093,0x0094,0x0095,0x0081,0x0096,0x0097,0x0098,0x0099,0x009a,0x009b,0x009c,0x009d,0x009e,0x009f,0x00a0,0x00a1,0x00a2,0x00a3,0x00a4,0x00a5,0x00a6,0x00a7,0x00a8,0x00a9,0x00aa,0x00ab,0x00ac,0x00ad,0x00ae,0x00af,0x00b0,0x00b1,0x00b2,0x00b3,0x00b4,0x00b5,0x00d1,0x00b6,0x00b7,0x00b8,0x00b9,0x00ba,0x00bb,0x00bc,0x00bd,0x00be,0x00bf,0x00c0,0x00c1,0x00c2,0x00c3,0x00c4,0x00c5,0x00c6,0x00c7,0x00c8,0x00c9,0x00ca,0x00cb,0x00cc,0x00cd,0x00ce,0x00cf]
symbia2 = [0x00c0,0x00c1,0x00c2,0x00c3,0x00c4,0x00c5,0x00a8,0x00c6,0x00c7,0x00c8,0x00c9,0x00ca,0x00cb,0x00cc,0x00cd,0x00ce,0x00cf,0x00d0,0x00d1,0x00d2,0x00d3,0x00d4,0x00d5,0x00d6,0x00d7,0x00d8,0x00d9,0x00dc,0x00db,0x00da,0x00dd,0x00de,0x00df,0x00e0,0x00e1,0x00e2,0x00e3,0x00e4,0x00e5,0x00b8,0x00e6,0x00e7,0x00e8,0x00e9,0x00ea,0x00eb,0x00ec,0x00ed,0x00ee,0x00ef,0x00f0,0x00f1,0x00f2,0x00f3,0x00f4,0x00f5,0x00f6,0x00f7,0x00f8,0x00f9,0x00fc,0x00fb,0x00fa,0x00fd,0x00fe,0x00ff]
#            e?       e'     e'      e"      e"      eA      e?      eu       e-     e~      e?       es      e>     es       et      ez      ez     e       e?      e?      ee      eA      eN      e|      eO      e?      e?      e?      e"      e?       e-     e?       e?      ez      e?       e?     e?     e'      eu     N'       e?      e?      e?       e?       ez    e"      e?      e?      e?       e'      NE     N?     N,         N?   N"       Na      N?      N?      N^      Ne      NS      N<      Ne       NT      NZ     NZ      
normal =  [0x0410,0x0411,0x0412,0x0413,0x0414,0x0415,0x0401,0x0416,0x0417,0x0418,0x0419,0x041a,0x041b,0x041c,0x041d,0x041e,0x041f,0x0420,0x0421,0x0422,0x0423,0x0424,0x0425,0x0426,0x0427,0x0428,0x0429,0x042a,0x042b,0x042c,0x042d,0x042e,0x042f,0x0430,0x0431,0x0432,0x0433,0x0434,0x0435,0x0451,0x0436,0x0437,0x0438,0x0439,0x043a,0x043b,0x043c,0x043d,0x043e,0x043f,0x0440,0x0441,0x0442,0x0443,0x0444,0x0445,0x0446,0x0447,0x0448,0x0449,0x044a,0x044b,0x044c,0x044d,0x044e,0x044f]

clipboard_name=u"Clpboard.cbd"
clipboard_drive=u""
clipboard_path="\\system\\Data\\"
clipboard_path_name=clipboard_path+clipboard_name
clipbd=u""

import os

if os.path.exists(u"c:"+clipboard_path_name):
  clipbd=u"c:"+clipboard_path_name
elif os.path.exists(u"c:"+clipboard_path_name):
  clipbd=u"d:"+clipboard_path_name
elif os.path.exists(u"e:"+clipboard_path_name):
  clipbd=u"e:"+clipboard_path_name
else:  
  clipbd=u"d:"+clipboard_path_name
      
#print u'clip path is :',clipbd         

def __tosymbian(string):
  res = ""
  i = 0
  while i < len(string):
    char = string[i]
    i+=1
    tmp = ord(char)
    if char == "\n" or tmp == 0x2029: 
      res += chr(0xe) + chr(0x20) + chr(0x29)
      continue
    #if i < 3:
    #  import appuifw
    #  appuifw.note(unicode(hex(tmp)))
    index = -1
    for k in range(len(symbia2)):
      if symbia2[k] == tmp or normal[k] == tmp:
        index = k
        break
    if index == -1:
      #appuifw.note(u"tos: " + unicode(hex(tmp)))
      try: 
        res += char
      except:
        res += char.encode('utf-8')
    else: res += unichr(symbian[index])
  return res

def __tonormal(string):
  res = ""
  for i in range(len(string)):
    char = string[i]
    tmp = ord(char)
    index = -1
    for k in range(len(symbian)):
      if symbian[k] == tmp:
        index = k
        break
    if index == -1:
      res += char
    else: res += unichr(normal[index])
  return res
  
def Get():
  def Read32(f):
    tmp = f.read(4)
    result = ord(tmp[3])*16777216 + ord(tmp[2])*65536 + ord(tmp[1])*256 + ord(tmp[0])
    return result
  try:
    f = open(clipbd,"rb")
    f.seek(0x14)
    length = Read32(f)
    text = ""
    i = 0
    while i < length:
      char = f.read(1)
      if char == chr(0x12) or char == chr(0x3): continue
      elif char == chr(0xe):
          tmp = f.read(2)
          if tmp == chr(0x20) + chr(0x29): 
            char = "\n"
          else:
            f.seek(-2,1)
            continue
      elif char == chr(0x40):
          tmp = f.read(2)
          if tmp == chr(0xa9) + chr(0xa9): 
            char = "\n\n"
            length += 1
          else:
            f.seek(-2,1)
            continue
      elif char == chr(0xa9):
        char = "\n"
        length += 1
      text += char
      i += 1
    return __tonormal(text)
  except: return False

def print_exception():
  import sys
  import traceback
  type, value, tb = sys.exc_info()
  sys.last_type = type
  sys.last_value = value
  sys.last_traceback = tb
  tblist = traceback.extract_tb(tb)
  del tblist[:1]
  list = traceback.format_list(tblist)
  if list:
    list.insert(0, u"Tra"+"ce:\n")
  list[len(list):] = traceback.format_exception_only(type, value)
  tblist = tb = None
  import appuifw
  appuifw.app.body.add( unicode(str(list).replace("\\n","\n")))

def Set(text):
  try:
    try: text = text.decode('utf-8')
    except: pass
    import struct
    header = chr(0x37) + chr(0)*2 + chr(0x10)*2 + chr(0x3a) + chr(0) + chr(0x10) + chr(0)*4 + chr(0x6a) + chr(0xfc) + chr(0x7b) + chr(0x3)
    encstr = chr(0x12) 
    txt = __tosymbian(text)
    strtxt = ""
    for i in range(len(txt)):
      char = txt[i]
      if char == '\n':
        strtxt += chr(0xe) + chr(0x20) + chr(0x29)
        continue
      tmp = ord(char)
      if tmp > 255:
        tmp = ord(u" ")
      strtxt += struct.pack('B',tmp)
    strlength = struct.pack('I',len(strtxt.replace(chr(0xe) + chr(0x20) + chr(0x29)," ")))
    contentend = chr(0) + chr(0x2) + chr(0x1d) + chr(0x3a) + chr(0) + chr(0x10) + chr(0x14) + chr(0)*3
    totallength = 4 + len(header) + len(strlength) + len(encstr) + len(text) + len(contentend) - 9
    totallength = struct.pack('I',0)
    f = open(clipbd,"wb")
    f.write(header + totallength + strlength + encstr)
    f.write(strtxt)
    f.write(contentend)
    f.close()
    
    f = open(clipbd,"a+b")
    pos = f.tell()
    f.seek(0x10)
    f.write(struct.pack('I',pos - 9))
    f.close()
    
  except: 
    #print_exception()
    return False
  return True
