
import re
import requests

def auth_site(email, password, csrf_token):
    url = 'https://www.coursera.org/api/login/v3Ssr'
    params = {
        'csrf3-token': csrf_token
    }
    data = {
        'email': email,
        'password': password,
    }
    headers = {
        'Cookie':'CSRF3-Token={};'.format(csrf_token),
    }
    # proxies = {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}
    proxies = {}
    r = requests.post(url, params=params, data=data, headers=headers, verify=False, proxies=proxies, allow_redirects=False)
    if r.status_code != 303:
        raise Exception('Auth website failed, resonse:', r.status_code, r.text[:512])
    print('Auth website success!')
    set_cookie = r.headers['Set-Cookie']
    matches = re.findall('([^;,\s]+?=[^;,\s]+?;) Max-Age=', set_cookie)
    cookie = ''.join(matches)
    return cookie

def fetchIndex(cookie):
    url = 'https://www.coursera.org'
    headers = {
        'Cookie': cookie
    }
    r = requests.get(url, headers=headers, allow_redirects=False)

    matches = re.search('"csrfToken":"(.+?)"', r.text)
    csrf_token = matches[1]

    if re.search('bullet-description', r.text):
        return False, csrf_token
    else:
        return True, csrf_token

if __name__ == '__main__':
    # cookie = auth_site('wang719695@gmail.com', 'wang719695274')
    # print(cookie)
    cookie = 'CAUTH=FZvQ_xoRTVJBB4o7fQDfOecH77nps0289YTkomcpNYaKew-NxsFWBqHVxf4vXDNGoiW2JTbfiTmx_lhmBPR9Tg.z4KBssMzl2pMN8wao7EyOg.lrYZnaBcXtmHbgL3HwZVT1cJsUFfUT_nKyGjKRVXLDN8jpat5TTOYIY6AogePfHk6_P63HNfUQGm23snayvHqbzx2NZFaP9Eu-8O8dHGB_zDB95xeBpCzWPCCFTA5k0zmr26sqVyQRBSozLg5cnCE-xRp1gBVK5XPNnq5ehZCDtSGxf2-iWd9IoB2ByzJYZ0;maestro_login_flag=1;__204u=9904381123-1542273465330;'
    isAuthed, csrf_token = fetchIndex(cookie)
    print(isAuthed, csrf_token)


'''
猜测token是必要值，且只能使用一次
代价已经够大了，不划算了

GET https://hub.coursera-notebooks.org/hub/coursera_login?token=E5-H3MY_SP6fh9zGP2j-rw&next=%2Fnotebooks%2FWeek+2%2FPython+Basics+with+Numpy%2FPython+Basics+With+Numpy+v3.ipynb HTTP/1.1
Host: hub.coursera-notebooks.org
Connection: keep-alive
Upgrade-Insecure-Requests: 1
DNT: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Referer: https://www.coursera.org/learn/neural-networks-deep-learning/notebook/Zh0CU/python-basics-with-numpy-optional
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: jupyter-hub-token="2|1:0|10:1542243920|17:jupyter-hub-token|44:ZjM2MjRiYzcyMTkyNDAyMWEwZTMyMzA5OGM3MTllYTc=|ec3df9e8e34772c4b8ba13ec040e2c8c2759073e4f7e10720b364305ff063612"; _xsrf=2|8448f35f|939cb795c6d4b6440e3dd0d269470845|1541988505; AWSALB=evu975abnxczMFtiSnONBUUtn4TBKuQLi4OjKTaA8QL3ylNy9FzyyN789X4uCCcecZQSmAgeIhJ1zaSQ+SK/CBKH6kEvnrYf/pQfl65CWIWSFNl9tIT5V/poh4Pe
'''


