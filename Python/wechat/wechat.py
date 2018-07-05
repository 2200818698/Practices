from  flask import Flask,request,session,render_template,jsonify
from  bs4 import BeautifulSoup
import time
import requests
# 正则表达式
import re
import json
app = Flask(__name__)
app.debug = True
app.secret_key = 'hththt'

def xml_parser(text):
    dic = {}
    soup = BeautifulSoup(text,'html.parser')
    div = soup.find(name='error')
    for item in div.find_all(recursive=False):
        dic[item.name] = item.text
    return dic

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        ctime = str(int(time.time() * 1000))
        qr_url = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}".format(ctime)
        response = requests.get(qr_url)
        qr_img = re.findall('uuid = "(.*)";',response.text)[0]
        session['qr_img'] = qr_img
        return render_template('login.html',qr_img=qr_img)
    else:
        pass
@app.route('/check')
def check():
    response = {'code' : 408}
    qr_img = session['qr_img']
    ctime = str(int(time.time()*1000))
    check_url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=-1036255891&_={1}".format(
        qr_img, ctime)
    # print(check_url)
    ret = requests.get(check_url)
    # print(ret.text)
    if 'code=201' in ret.text:
        # print(ret.text)
        src = re.findall("userAvatar = '(.*)';",ret.text)[0]
        response['code'] = 201
        # print(src)
        response['src'] = src
    elif 'code=200' in ret.text:
        # print('===确认==='*5)
        # print(ret.text)
        session['login_cookie'] = ret.cookies.get_dict()
        redirect_url = re.findall('redirect_uri="(.*)"',ret.text)[0]
        print(redirect_url)
        str_list = [redirect_url, '&fun=new&version=v2']
        a = ''
        url = a.join(str_list)
        # print(url)
        # 现在一请求这个，就会webwxstatreport
        ticket_ret = requests.get(url)
        print('===票据==='*5)
        print(ticket_ret.text)
        ticket_dic = xml_parser(ticket_ret.text)
        session['ticket_dic'] = ticket_dic
        session['ticket_cookie'] = ticket_ret.cookies.get_dict()
        response['code'] = 200
    return  jsonify(response)
@app.route('/userdata')
def userdata():
    # 取pass_ticket字段
    ticket_dic = session.get('ticket_dic')
    init_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-1680000337&lang=zh_CN&pass_ticket={0}".format(
        ticket_dic.get('pass_ticket'))
    # 设备信息、票据
    print(ticket_dic)
    params = {
        "BaseRequest": {
            "DeviceID": "e461326685639889",
            "Sid": ticket_dic.get('wxsid'),
            "Uin": ticket_dic.get('wxuin'),
            "Skey": ticket_dic.get('skey'),
        }
    }
    result = requests.post(
        url=init_url,
        json=params
    )

    result.encoding = 'utf-8'
    userdata = result.json()
    # print('===我的===' * 5)
    # print(userdata)
    session['user'] = userdata['User']
    session['syncKey'] = userdata['SyncKey']
    return render_template('userdata.html',userdata=userdata)

@app.route('/avater')
def avater():
    # 获取session里面得数据
    user = session.get('user')
    ticket_cookie = session.get('ticket_cookie')
    url = "https://wx.qq.com" + user['HeadImgUrl']
    avater = requests.get(url=url,cookies=ticket_cookie,headers={'Content-Type': 'image/jpeg'})
    # print('===图片===' * 5)
    # print(avater.content)
    return avater.content


@app.route('/list')
def list():
    ticket_dic = session.get('ticket_dic')
    ticket_cookie = session.get('ticket_cookie')
    ctime = str(int(time.time() * 1000))
    skey = ticket_dic.get('skey')
    url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&r={0}&seq=0&skey={1}".format(ctime,skey)
    ret = requests.get(url,cookies=ticket_cookie)
    ret.encoding = 'utf-8'
    user = ret.json()
    # print('===好友==='*5)
    # print(user)
    return  render_template('list.html',user=user)

@app.route('/send',methods=['GET','POST'])
def send():
    if request.method == 'GET':
        return render_template('send.html')
    user = session['user']
    ticket_dic = session['ticket_dic']
    sender = user['UserName']
    receiver = request.form.get('receiver')
    message = request.form.get('message')
    ctime = str(time.time() * 1000)
    msg_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={0}".format(
        ticket_dic['pass_ticket'])
    # 伪造数据
    msg_data = {
        'BaseRequest': {
            "DeviceID": "e461326685639889",
            "Sid": ticket_dic.get('wxsid'),
            "Uin": ticket_dic.get('wxuin'),
            "Skey": ticket_dic.get('skey'),
        },
        'Msg': {
            'ClientMsgId': ctime,
            'LocalID': ctime,
            'FromUserName': sender,
            'ToUserName': receiver,
            "Content": message,
            'Type': 1
        },
        'Scene': 0
    }
    ret = requests.post(
        url=msg_url,
        # 处理编码问题
        json=msg_data
    )
    return ret.text

@app.route('/receive')
def receive():
    # 检查是否有新消息到来
    response = {'code': 408}
    sync_url = "https://webpush.weixin.qq.com/cgi-bin/mmwebwx-bin/synccheck"
    ticket_dic = session.get('ticket_dic')
    syncKey = session.get('syncKey')
    login_cookie = session.get('login_cookie')
    ticket_cookie = session.get('ticket_cookie')
    sync_data_list = []
    print('===syncKey==='*5)
    print(syncKey)
    for item in syncKey['List']:
        temp = "%s_%s" % (item['Key'], item['Val'])
        sync_data_list.append(temp)
    sync_data_str = "|".join(sync_data_list)
    nid = int(time.time())
    sync_dict = {
        "r": nid,
        "skey": ticket_dic['skey'],
        "sid": ticket_dic['wxsid'],
        "uin": ticket_dic['wxuin'],
        "deviceid": "e461326685639889",
        "synckey": sync_data_str
    }
    all_cookie = {}
    all_cookie.update(login_cookie)
    all_cookie.update(ticket_cookie)
    response_sync = requests.get(sync_url, params=sync_dict, cookies=all_cookie)
    print(response_sync.text)
    if 'selector:"2"' in response_sync.text:
        fetch_msg_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=%s&skey=%s&lang=zh_CN&pass_ticket=%s" % (
            ticket_dic['wxsid'], ticket_dic['skey'], ticket_dic['pass_ticket'])

        form_data = {
            'BaseRequest': {
                'DeviceID': 'e461326685639889',
                'Sid': ticket_dic['wxsid'],
                'Skey': ticket_dic['skey'],
                'Uin': ticket_dic['wxuin']
            },
            'SyncKey': syncKey,
            'rr': str(time.time())
        }
        response_fetch_msg = requests.post(fetch_msg_url, json=form_data)
        response_fetch_msg.encoding = 'utf-8'
        res_fetch_msg_dict = json.loads(response_fetch_msg.text)
        syncKey = res_fetch_msg_dict['SyncKey']
        for item in res_fetch_msg_dict['AddMsgList']:
            # 查看接受的信息
            print(item['Content'], ":::::", item['FromUserName'], "---->", item['ToUserName'], )
    response['code'] = 200
    return jsonify(response)

if __name__ == '__main__':
    app.run()