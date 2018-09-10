import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'}
response = requests.get('chrome://history/', headers=headers)
response.encoding = response.apparent_encoding
print(response.text)

# soup = BeautifulSoup(response.text,'html.parser')
# div = soup.find(name = 'div', id = 'auto-channel-lazyload-article')
# ul = div.find(name = 'ul')
# li_list = ul.find_all(name = 'li')
#
# for li in li_list:
#     a = li.find(name = 'a')
#     if not a:
#         continue
#     p = a.find(name = 'p')
#     h3 = a.find(name = 'h3')
#     img = a.find(name = 'img')
#     src = img.get('src')
#
#     file_name = src.split('__',1)[1]
#     ret_img = requests.get(url = "https:" + src)
#     with open(file_name,'wb') as f:
#         f.write(ret_img.content)
#
#     print(h3.text)
#     print(a.get('href'))
#     print(p.text)
#     print(src)
#     print (15*'=')
