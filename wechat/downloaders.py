# -*- coding: utf-8 -*-
__author__ = 'yijingping'
import time
import json
import platform
from datetime import datetime, timedelta
from dateutil.parser import parse
from random import sample, randint
from lxml import etree
from io import StringIO
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from wechatspider.util import get_uniqueid, get_redis
from wechat.models import Topic
from wechat.constants import KIND_DETAIL, KIND_KEYWORD, KIND_NORMAL
from django.conf import settings
from .util import stringify_children

import logging
logger = logging.getLogger()

CRAWLER_CONFIG = settings.CRAWLER_CONFIG

BASE_DIR = settings.BASE_DIR


class SeleniumDownloaderBackend(object):
    headers = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
        }
    ]

    def __init__(self, proxy=None):
        # 设置代理
        self.proxy = proxy

    def __enter__(self):
        # 打开界面
        self.display = self.get_display()
        #  打开浏览器
        self.browser = self.get_browser(self.proxy)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭浏览器
        try:
            if self.browser:
                self.browser.delete_all_cookies()
                self.browser.close()
                self.browser.quit()
        except Exception as e:
            logging.exception(e)
        # 关闭界面
        try:
            # 关闭浏览器,关闭窗口
            self.display and self.display.sendstop()
            #self.display and self.display.stop()
        except Exception as e:
            logging.exception(e)

    def get_display(self):
        """ 获取操作系统桌面窗口 """
        if platform.system() != 'Darwin':
            # 不是mac系统, 启动窗口
            display = Display(visible=0, size=(1024, 768))
            display.start()
        else:
            display = None
        return display

    def get_browser(self, proxy):
        """ 启动并返回浏览器，使用firefox """
        fp = webdriver.FirefoxProfile()
        #禁止加载image
        #fp.set_preference('permissions.default.stylesheet', 2)
        # fp.set_preference('permissions.default.image', 2)
        # fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        fp.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")
        if proxy.is_valid():
            logger.info('antonio-97[%s:%s]' % (proxy.host, proxy.port))
            fp.set_preference('network.proxy.type', 1)
            fp.set_preference('network.proxy.http', proxy.host)
            fp.set_preference('network.proxy.http_port', proxy.port)
            fp.set_preference('network.proxy.ssl', proxy.host)
            fp.set_preference('network.proxy.ssl_port', proxy.port)
        else:
            fp.set_preference("network.proxy.type", 0)
        fp.update_preferences()
        browser = webdriver.Firefox(firefox_profile=fp, service_log_path='%s/%s' % (BASE_DIR, 'geckodriver.log') )
        return browser

    def download(self, url):
        pass

    def download_wechat(self, data, process_topic):
        """ 根据微信号最新文章 """
        wechat_id, wechatid = data['wechat_id'], data['wechatid']
        try:
            self.visit_wechat_index(wechatid)
            if self.visit_wechat_topic_list(wechatid):
                self.download_wechat_topics(wechat_id, process_topic)
        except Exception as e:
            logger.exception(e)
            self.log_antispider()
            self.retry_crawl(data)

    def download_wechat_keyword(self, data, process_topic):
        """ 爬取关键词爬取最新文章 """
        word = data['word']
        try:
            self.visit_wechat_index_keyword(word)
            self.download_wechat_keyword_topics(word, process_topic)
        except Exception as e:
            logger.exception(e)
            self.log_antispider()
            self.retry_crawl(data)

    def download_wechat_topic_detail(self, data, process_topic):
        """ 根据url爬取文章的详情页 """
        url = data['url']
        browser = self.browser
        try:
            browser.get(url)
            time.sleep(3)

            if 'antispider' in browser.current_url:
                """被检测出爬虫了"""
                self.log_antispider()
                self.retry_crawl(data)
                time.sleep(randint(1, 5))
            else:
                ##提取title和微信账号
                js = """ return document.documentElement.innerHTML; """
                body = browser.execute_script(js)
                htmlparser = etree.HTMLParser()
                tree = etree.parse(StringIO(body), htmlparser)
                titleelems = [item.strip() for item in tree.xpath("//h2[@class='rich_media_title']/text()") if item.strip()]
                wechatelems = [item.strip() for item in tree.xpath("//span[@class='rich_media_meta rich_media_meta_nickname']/a[@id='js_name']/text()") if item.strip()]
                wechatidelems = [item.strip() for item in tree.xpath("//div[@id='js_profile_qrcode']/div[@class='profile_inner']/p[@class='profile_meta']/span[@class='profile_meta_value']/text()") if item.strip()]

                title = titleelems[0] if len(titleelems)>0 else ''
                wechatid = wechatidelems[0] if len(wechatidelems)>0 else ''
                name = wechatelems[0] if len(wechatelems)>0 else ''

                logger.info(title)
                logger.info(wechatid)
                logger.info(name)
                logger.info('line:147')
                js = """
                    var imgs = document.getElementsByTagName('img');

                    for(var i = 0; i < imgs.length; i++) {
                      var dataSrc = imgs[i].getAttribute('data-src');
                      if (dataSrc){
                        imgs[i].setAttribute('src', dataSrc);
                        imgs[i].removeAttribute('crossorigin');
                      }
                    }
                    var ele = document.getElementById('js_pc_qr_code');
                    if(ele){
                        ele.remove();
                    }
                    var ele2 = document.getElementById('js_profile_qrcode');
                    if(ele2){
                        ele2.remove();
                    }
                    return document.documentElement.innerHTML;
                """
                body = browser.execute_script(js)
                process_topic({
                    'url': browser.current_url,
                    'body': body,
                    'avatar': '',
                    'name': name,
                    'title': title,
                    'wechatid': wechatid,
                    'kind': KIND_DETAIL
                })
                time.sleep(randint(1, 5))

        except Exception as e:
            logger.exception(e)
            self.log_antispider()
            self.retry_crawl(data)

    def visit_wechat_index(self, wechatid):
        """ 访问微信首页，输入微信id，点击搜公众号 """
        browser = self.browser
        browser.get("http://weixin.sogou.com/")
        time.sleep(3)
        # 增加Cookie信息
        # logger.info('antonio add cookie')
        # browser.add_cookie({'name': 'ABTEST', 'value': '4|1555894615|v1'})
        # browser.add_cookie({'name': 'IPLOC', 'value': 'CN3100'})
        # browser.add_cookie({'name': 'SUID', 'value': '5AE9E4744018960A000000005CBD1157'})
        # browser.add_cookie({'name': 'weixinIndexVisited', 'value': '1'})
        # browser.add_cookie({'name': 'SUV', 'value': '00A39A3B74E4E95A5CBD11597C9EF458'})
        # browser.add_cookie({'name': 'SNUID', 'value': '368589186D68EB7F9F331B386D002CE9'})
        logger.info(browser.title)
        element_querybox = browser.find_element_by_name('query')
        element_querybox.send_keys(wechatid, Keys.ARROW_DOWN)
        element_search_btn = browser.find_element_by_xpath("//input[@value='搜公众号']")
        element_search_btn.click()
        time.sleep(3)
        logger.info(browser.title)

    def visit_wechat_index_keyword(self, word):
        """ 访问微信首页，输入关键词，点击搜文章 """
        browser = self.browser
        browser.get("http://weixin.sogou.com/")
        logger.info(browser.title)
        element_querybox = browser.find_element_by_name('query')
        element_querybox.send_keys(word, Keys.ARROW_DOWN)
        element_search_btn = browser.find_element_by_xpath("//input[@value='搜文章']")
        element_search_btn.click()
        time.sleep(3)
        logger.info(browser.title)

    def visit_wechat_topic_list(self, wechatid):
        """ 找到微信号，并点击进入微信号的文章列表页面 """
        browser = self.browser
        # 找到搜索列表第一个微信号, 点击打开新窗口
        element_wechat = browser.find_element_by_xpath("//div[@class='txt-box']/p[@class='info']/label")
        element_wechat_title = browser.find_element_by_xpath("//div[@class='txt-box']/p[@class='tit']/a")
        if element_wechat and element_wechat.text == wechatid:
            element_wechat_title.click()
            time.sleep(3)
            # 切到当前的文章列表页窗口
            new_handler = browser.window_handles[-1]
            browser.switch_to.window(new_handler)
            time.sleep(30)
            return True
        else:
            return False

    def download_wechat_topics(self, wechat_id, process_topic):
        """ 在微信号的文章列表页面，逐一点击打开每一篇文章，并爬取 """
        browser = self.browser
        js = """ return document.documentElement.innerHTML; """
        body = browser.execute_script(js)
        logger.info('antonio-221[%s]' % (body))
        htmlparser = etree.HTMLParser()
        tree = etree.parse(StringIO(body), htmlparser)

        elems = [item.strip() for item in tree.xpath("//h4[@class='weui_media_title']/text()") if item.strip()]
        hrefs = ['http://mp.weixin.qq.com%s' % item for item in tree.xpath("//h4[@class='weui_media_title']/@hrefs")]
        elems_avatars = tree.xpath("//div[@class='weui_media_box appmsg']/span/@style")
        avatars = [item[21:-1] for item in elems_avatars]
        elems_abstracts = tree.xpath("//p[@class='weui_media_desc']")
        abstracts = [item.text.strip() if item.text else '' for item in elems_abstracts]
        links = []
        for idx, item in enumerate(elems[:10]):
            title = item
            logger.info(title)
            if not title:
                continue
            uniqueid = get_uniqueid('%s:%s' % (wechat_id, title))
            try:
                Topic.objects.get(uniqueid=uniqueid)
            except Topic.DoesNotExist:
                #print len(elems), len(hrefs), len(avatars), len(abstracts)
                #print elems, hrefs, avatars, abstracts
                links.append((title, hrefs[idx], avatars[idx], abstracts[idx]))
                logger.debug('文章不存在, title=%s, uniqueid=%s' % (title, uniqueid))
        for title, link, avatar, abstract in reversed(links):
            # 可以访问了
            browser.get(link)
            time.sleep(3)

            if 'antispider' in browser.current_url:
                """被检测出爬虫了"""
                self.log_antispider()
                time.sleep(randint(1, 5))
            else:
                js = """
                    var imgs = document.getElementsByTagName('img');

                    for(var i = 0; i < imgs.length; i++) {
                      var dataSrc = imgs[i].getAttribute('data-src');
                      if (dataSrc){
                        imgs[i].setAttribute('src', dataSrc);
                        imgs[i].removeAttribute('crossorigin');
                      }
                    }
                    var ele = document.getElementById('js_pc_qr_code');
                    if(ele){
                        ele.remove();
                    }
                    var ele2 = document.getElementById('js_profile_qrcode');
                    if(ele2){
                        ele2.remove();
                    }
                    return document.documentElement.innerHTML;
                """
                body = browser.execute_script(js)
                process_topic({
                    'url': browser.current_url,
                    'body': body,
                    'avatar': avatar,
                    'title': title,
                    'abstract': abstract,
                    'kind': KIND_NORMAL
                })
                time.sleep(randint(1, 5))

    def download_wechat_keyword_topics(self, word, process_topic):
        """ 在关键词下的文章列表页面，逐一点击打开每一篇文章，并爬取 """
        browser = self.browser
        js = """ return document.documentElement.innerHTML; """
        body = browser.execute_script(js)

        htmlparser = etree.HTMLParser()
        tree = etree.parse(StringIO(body), htmlparser)

        elems = [stringify_children(item).replace('red_beg', '').replace('red_end', '') for item in tree.xpath("//div[@class='txt-box']/h3/a")]
        hrefs = tree.xpath("//div[@class='txt-box']/h3/a/@href")
        #avatars = tree.xpath("//div[@class='img-box']/a/img/@src")
        #elems_abstracts = tree.xpath("//div[@class='txt-box']/p")
        #abstracts = [item.text.strip() if item.text else '' for item in elems_abstracts]
        avatars = [''] * len(elems)
        abstracts = [''] * len(elems)
        links = []
        for idx, item in enumerate(elems):
            title = item
            logger.info(title)
            if not title:
                continue
            uniqueid = get_uniqueid('%s:%s' % (word, title))
            try:
                Topic.objects.get(uniqueid=uniqueid)
            except Topic.DoesNotExist:
                #print len(elems), len(hrefs), len(avatars), len(abstracts)
                #print elems, hrefs, avatars, abstracts
                links.append((title, hrefs[idx], avatars[idx], abstracts[idx]))
                logger.debug('文章不存在, title=%s, uniqueid=%s' % (title, uniqueid))
        for title, link, avatar, abstract in reversed(links):
            # 可以访问了
            browser.get(link)
            time.sleep(3)

            if 'antispider' in browser.current_url:
                """被检测出爬虫了"""
                self.log_antispider()
                time.sleep(randint(1, 5))
            else:
                js = """
                    var imgs = document.getElementsByTagName('img');

                    for(var i = 0; i < imgs.length; i++) {
                      var dataSrc = imgs[i].getAttribute('data-src');
                      if (dataSrc){
                        imgs[i].setAttribute('src', dataSrc);
                        imgs[i].removeAttribute('crossorigin');
                      }
                    }
                    var ele = document.getElementById('js_pc_qr_code');
                    if(ele){
                        ele.remove();
                    }
                    var ele2 = document.getElementById('js_profile_qrcode');
                    if(ele2){
                        ele2.remove();
                    }
                    return document.documentElement.innerHTML;
                """
                body = browser.execute_script(js)
                process_topic({
                    'url': browser.current_url,
                    'body': body,
                    'avatar': avatar,
                    'title': title,
                    'abstract': abstract,
                    'kind': KIND_KEYWORD
                })
                time.sleep(randint(1, 5))

    def log_antispider(self):
        """ 记录1小时内的被禁爬的数量 """
        r = get_redis()
        if r.incr(CRAWLER_CONFIG['antispider']) <= 1:
            r.expire(CRAWLER_CONFIG['antispider'], 3600)

    def retry_crawl(self, data):
        """ 如果被禁爬，重试 """
        r = get_redis()
        retry = data.get('retry', 0)

        if data.get('kind') == KIND_DETAIL:
            if retry >= 20:
                return
            data = {
                'kind': data['kind'],
                'url': data['url'],
                'retry': retry + 1
            }
        elif data.get('kind') == KIND_KEYWORD:
            if retry >= 3:
                return
            data = {
                'kind': data['kind'],
                'word': data['word'],
                'retry': retry + 1
            }
        else:
            if retry >= 3:
                return
            data = {
                'kind': data['kind'],
                'wechat_id': data['wechat_id'],
                'wechatid': data['wechatid'],
                'retry': retry + 1
            }

        r.lpush(settings.CRAWLER_CONFIG["downloader"], json.dumps(data))
