import re
redict_uri = 'redirect_uri="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=ARG5rXcGrb1FB-YaT3qeviuc@qrticket_0&uuid=QYKZ2sJyhw==&lang=zh_CN&scan=1530675611"'
redirect_url = re.findall('redirect_uri="(.*)"',redict_uri)[0]

print(redirect_url)