# -*- coding: utf-8 -*-

from selenium import webdriver
import selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import logging
import re
import time
import random

BASE_URL = 'http://weixin.sogou.com'

UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"


def get_html(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )
    dcap["takesScreenshot"] = (False)
    # t0 = time.time()
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
        driver.set_page_load_timeout(240)
        driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')

        driver.execute('executePhantomScript', {'script': '''
var page = this; // won't work otherwise
page.onResourceRequested = function(requestData, request) {
	if ((/http:\/\/.+?\.css/gi).test(requestData['url']) || requestData['Content-Type'] == 'text/css') {
		console.log('The url of the request is matching. Aborting: ' + requestData['url']);
		request.abort();
	}
}
''', 'args': []})

    except selenium.common.exceptions.WebDriverException:
        return None
    try:
        driver.get(url)
        html = driver.page_source
    except Exception as e:
        html = None
        logging.error(e)
    finally:
        driver.quit()
    return html


def get_html_direct(url, cookies=None):
    if not cookies:
        cookies = update_cookies()
    headers = {"User-Agent": UA}
    r = requests.get(url, headers=headers, cookies=cookies, timeout=20)
    r.encoding = "utf-8"
    return r.text


def _get_account_info(open_id=None, cookies=None):
    url = None
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    # html = get_html(url)
    html = get_html_direct(url, cookies=cookies)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    info_box = soup.select('#weixinname')[0].parent
    account_info = dict()
    account_info['account'] = info_box.select('h4 span')[0].text.split(u'：')[1].strip()
    account_info['name'] = info_box.select('#weixinname')[0].text
    account_info['description'] = info_box.select('.sp-txt')[0].text
    # img_list = soup.select('.pos-ico img')
    extra = soup.select(".img-box img")[0]['extra']
    account_info['logo'] = extra[extra.find(u'&url=') + 5:].strip()
    account_info['qr_code'] = "http://open.weixin.qq.com/qr/code/?username=%s" % account_info['account']
    return account_info


def weixin_search(name, cookies=None):
    url = BASE_URL + '/weixin?query=' + name
    # html = get_html(url)
    html = get_html_direct(url, cookies=cookies)
    soup = BeautifulSoup(html, "html.parser")

    ls = soup.select("._item")
    search_list = []
    for item in ls:
        account_info = dict()
        account_info['account'] = item.select('h4 span')[0].text.split(u'：')[1].strip()
        account_info['open_id'] = item['href'].split('openid=')[1]

        search_list.append(account_info)
    # print(account_info)
    return search_list


def update_cookies():
    s = requests.Session()
    headers = {"User-Agent": UA}
    s.headers.update(headers)
    url = BASE_URL + '/weixin?query=123'
    r = s.get(url)
    if 'SNUID' not in s.cookies:
        p = re.compile(r'(?<=SNUID=)\w+')
        s.cookies['SNUID'] = p.findall(r.text)[0]
        suv = ''.join([str(int(time.time() * 1000000) + random.randint(0, 1000))])
        s.cookies['SUV'] = suv
    return s.cookies


def get_account_info(display_id):
    cookies = update_cookies()
    account = weixin_search(display_id, cookies)

    if account is None or len(account) == 0:
        return None

    if account[0]['account'] != display_id:
        return None

    return _get_account_info(account[0]['open_id'], cookies)


if __name__ == '__main__':
    print(get_account_info('jianshuio'))
