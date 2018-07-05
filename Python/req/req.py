import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.autohome.com.cn/news/')
response.encoding = response.apparent_encoding


soup = BeautifulSoup(response.text,'html.parser')
div = soup.find(name = 'div', id = 'auto-channel-lazyload-article')
ul = div.find(name = 'ul')
li_list = ul.find_all(name = 'li')

for li in li_list:
    a = li.find(name = 'a')
    if not a:
        continue
    p = a.find(name = 'p')
    h3 = a.find(name = 'h3')
    img = a.find(name = 'img')
    src = img.get('src')

    file_name = src.split('__',1)[1]
    ret_img = requests.get(url = "https:" + src)
    with open(file_name,'wb') as f:
        f.write(ret_img.content)

    print(h3.text)
    print(a.get('href'))
    print(p.text)
    print(src)
    print (15*'=')
