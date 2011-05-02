import sys, os, cgitb; cgitb.enable()

def cgi_decode(s):
    list = s.replace('+', ' ').split('%')
    result = [list.pop(0)]
    for item in list:
        if len(item) >= 2: result.append(chr(int(item[:2], 16)) + item[2:])
        else: result.append('%' + item)
    return ''.join(result)

class Struct:
    def __init__(self, **dict): self.__dict__['dict'] = dict
    def __getattr__(self, name): return self.dict.get(name, '')
    def __setattr__(self, name, value): self.dict[name] = value
    def __getitem__(self, name): return self.dict.get(name, '')
    def __setitem__(self, name, value): self.dict[name] = value
    def __contains__(self, name): return name in self.dict

form = Struct()
files = Struct()

ctype = os.environ.get('CONTENT_TYPE', '')
if ctype.startswith('multipart/'):
    import re
    content = sys.stdin.read()
    boundary = re.search('boundary=([^;]+)', ctype).group(1)
    for part in content.split('\r\n--' + boundary.strip('"')):
        if '\r\n\r\n' in part:
            headers, body = part.split('\r\n\r\n')
            disp = re.search('\ncontent-disposition:(.*)', headers.lower())
            name = re.search('name="([^"]*)"', disp.group(1)).group(1)
            filename = re.search('filename="([^"]*)"', disp.group(1))
            if filename:
                form[name], files[name] = filename.group(1), body
            else:
                form[name] = body
else:
    if os.environ.get('REQUEST_METHOD', '') == 'POST':
        query = sys.stdin.read()
    else:
        query = os.environ.get('QUERY_STRING', '')
    for pair in query.split('&'):
        if '=' in pair:
            name, value = map(cgi_decode, pair.split('=', 1))
            form[name] = value.strip()

server = os.environ.get('SERVER_ADDR', '')
agent = os.environ.get('HTTP_USER_AGENT', '')
request = 'http://' + os.environ.get('SERVER_NAME', '') + \
                      os.environ.get('SCRIPT_NAME', '')
client = os.environ.get('REMOTE_ADDR', '')
