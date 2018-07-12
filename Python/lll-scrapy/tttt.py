import requests
r = requests.get('http://www.cnblogs.com/post/prevnext?postId=9078770&blogId=133379&dateCreated=2018%2F5%2F23+20%3A28%3A00&postType=1')
print(r.text)