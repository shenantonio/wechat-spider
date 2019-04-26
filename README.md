# 微信爬虫
爬取微信公众号文章的爬虫
基于https://github.com/bowenpay/wechat-spider.git的开源进行改造，非常感谢！

# 功能介绍


# 界面预览

1） 要爬取的微信公众号列表

2） 要爬取的文章关键字列表

3） 已经爬取的微信文章

4） 查看文章，并进行发布


# 文章发布集成




# 安装

1）python环境, 检查python的版本，是否为2.7.x，如果不是，安装2.7.6。

如果是centos 6.x，升级python2.6到python2.7，参考教程 https://cloud.tencent.com/developer/article/1140994


如果是centos 7.x，默认就是python2.7,不用升级

如果是mac osx，可以使用virtualenv，安装python2.7

2）安装依赖包, clone代码
安装Mysql-python依赖
```
yum install python-devel mysql-devel gcc
```

安装lxml依赖
```
yum install libxslt-devel libxml2-devel
```

安装浏览器环境 selenium依赖.(如果是mac环境，仅需安装firefox， 但确保版本是 firefox 36.0，使用最新的版本会报错)
```
yum install xorg-x11-server-Xvfb
yum upgrade glib2 # 确保glib2版本大于2.42.2，否则firefox启动会报错
yum install firefox # centos下安装最新的firefox版本
```

clone代码,安装依赖python库
```
$ git clone https://github.com/shenantonio/wechat-spider.git
$ cd wechat-spider
$ pip install -r requirements.txt
如果install出现问题，建议执行：
python -m pip install --upgrade --force pip

wget https://bootstrap.pypa.io/ez_setup.py
sudo python ez_setup.py install

如出现
Collecting Django==1.8.1 (from -r requirements.txt (line 1))
/usr/local/lib/python2.7/site-packages/pip/_vendor/urllib3/util/ssl_.py:354: SNIMissingWarning: An HTTPS request has been made, but the SNI (Server Name Indication) extension to TLS is not available on this platform. This may cause the server to present an incorrect TLS certificate, which can cause validation failures. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  SNIMissingWarning

pip install pyopenssl ndg-httpsclient pyasn1
```

3) 创建mysql数据库

创建数据库wechatspider，默认采用utf8编码。（如果系统支持，可以采用utf8mb4，以兼容emoji字符）

```
mysql> CREATE DATABASE `wechatspider` CHARACTER SET utf8;
```

4) 安装和运行Redis

```shell
$ wget http://download.redis.io/releases/redis-2.8.3.tar.gz
$ tar xzvf redis-2.8.3.tar.gz
$ cd redis-2.8.3
$ make
$ make install
$ redis-server
```

5) 更新配置文件local_settings

在 wechatspider 目录下,添加 `local_settings.py` 文件,配置如下:
```
# -*- coding: utf-8 -*-

SECRET_KEY="xxxxxx"

CRAWLER_DEBUG = True

# aliyun oss2, 可以将图片和视频存储到阿里云，也可以选择不存储，爬取速度会更快。 默认不存储。
#OSS2_ENABLE = True
#OSS2_CONFIG = {
#    "ACCESS_KEY_ID": "XXXXXXXXXXXXXX",
#    "ACCESS_KEY_SECRET": "YYYYYYYYYYYYYYYYYYYYYY",
#    "ENDPOINT": "",
#    "BUCKET_DOMAIN": "oss-cn-hangzhou.aliyuncs.com",
#    "BUCKET_NAME": "XXXXX",
#    "IMAGES_PATH": "images/",
#    "VIDEOS_PATH": "videos/",
#    "CDN_DOMAIN": "XXXXXX.oss-cn-hangzhou.aliyuncs.com"
#}
# mysql 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'wechatspider',
        'USER': 'root',
        'PASSWORD': '',
        'OPTIONS':{
            'charset': 'utf8mb4',
        },
    }
}
# redis配置,用于消息队列和k-v存储
REDIS_OPTIONS = {
    'host': 'localhost',
    'port': 6379,
    'password': '',
    'db': 4
}

# 图片下载服务URL
IMAGE_SERVER_URL = 'http://localhost:8001/wechat/image/download/'

# kafka配置
KAFKA_ENABLE = True
KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9092",
    "topic": "wechat_topic",
    "client_id": "wechatspider"
}

```

6) 初始化表
```
$ python manage.py migrate


```


7）启动网站

```
python manage.py runserver 0.0.0.0:8001

如出现：
"Can't initialize character set utf8mb4 (path: /usr/share/mysql/charsets/)")

修改/usr/share/mysql/charsets/Index.xml 把 <charset name="utf8"> 修改为 <charset name="utf8mb4">
```
访问 http://localhost:8001/。


6) 创建超级管理员账号,访问后台，并配置要爬取的公众号和关键字
```
python manage.py createsuperuser
```


8）启动爬虫

```shell
$ python bin/scheduler.py
$ python bin/downloader.py
$ python bin/extractor.py
$ python bin/processor.py
```

以上步骤执行成功，并能爬取文章后。可以参考以下部分配置生产环境。

```

如果服务器没有安装桌面系统，将出现如下错误，请安装geckodriver

Traceback (most recent call last):
  File "bin/downloader.py", line 96, in <module>
    downloader.run()
  File "bin/downloader.py", line 77, in run
    with SeleniumDownloaderBackend(proxy=proxy) as browser:
  File "/home/wechat/wechat-spider/wechat/downloaders.py", line 42, in __enter__
    self.browser = self.get_browser(self.proxy)
  File "/home/wechat/wechat-spider/wechat/downloaders.py", line 96, in get_browser
    browser = webdriver.Firefox(firefox_profile=fp)
  File "/usr/local/lib/python2.7/site-packages/selenium/webdriver/firefox/webdriver.py", line 164, in __init__
    self.service.start()
  File "/usr/local/lib/python2.7/site-packages/selenium/webdriver/common/service.py", line 83, in start
    os.path.basename(self.path), self.start_error_message)
selenium.common.exceptions.WebDriverException: Message: 'geckodriver' executable needs to be in PATH.

Message: 'geckodriver' executable needs to be in PATH.

Traceback (most recent call last):
  File "bin/downloader.py", line 96, in <module>
    downloader.run()
  File "bin/downloader.py", line 77, in run
    with SeleniumDownloaderBackend(proxy=proxy) as browser:
  File "/home/wechat/wechat-spider/wechat/downloaders.py", line 42, in __enter__
    self.browser = self.get_browser(self.proxy)
  File "/home/wechat/wechat-spider/wechat/downloaders.py", line 96, in get_browser
    browser = webdriver.Firefox(firefox_profile=fp)
  File "/usr/local/lib/python2.7/site-packages/selenium/webdriver/firefox/webdriver.py", line 164, in __init__
    self.service.start()
  File "/usr/local/lib/python2.7/site-packages/selenium/webdriver/common/service.py", line 83, in start
    os.path.basename(self.path), self.start_error_message)
selenium.common.exceptions.WebDriverException: Message: 'geckodriver' executable needs to be in PATH.


geckodriver 安装
请选用此版本：https://github.com/mozilla/geckodriver/releases/tag/v0.24.0

https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar xvfz geckodriver-v0.24.0-linux64.tar.gz
cp geckodriver /usr/local/bin/.
ln -s /usr/local/geckodriver /usr/bin/geckodriver
```



### supervisor的安装，可灵活管理进程

> 安装supervisor
>
```
pip install supervisor==3.4.0
```

> 测试安装是否成功

```
echo_supervisord_conf

; Sample supervisor config file.
;
; For more information on the config file, please see:
; http://supervisord.org/configuration.html
;
; Notes:
;  - Shell expansion ("~" or "$HOME") is not supported.  Environment
;    variables can be expanded using this syntax: "%(ENV_HOME)s".
;  - Quotes around values are not supported, except in the case of
;    the environment= options as shown below.
;  - Comments must have a leading space: "a=b ;comment" not "a=b;comment".
;  - Command will be truncated if it looks like a config file comment, e.g.
;    "command=bash -c 'foo ; bar'" will truncate to "command=bash -c 'foo ".
```

> 建立文件夹,把应用的配置文件单独放置
```
mkdir -p /opt/app/supervisor
mkdir -p /opt/app/supervisor/conf.d

```

> 创建默认的配置文件,并修改配置
```
echo_supervisord_conf >/opt/app/supervisor/supervisord.conf

vi /etc/supervisord.conf

[inet_http_server] ; inet (TCP) server disabled by default
port=0.0.0.0:9001 ; (ip_address:port specifier, *:port for all iface)
username=user ; (default is no username (open server))
password=123 ; (default is no password (open server))

[include]
files = ./conf.d/*.conf
```

> 设定supervisor启动文件

```
vi /etc/init.d/supervisord

#! /usr/bin/env bash
# chkconfig: - 85 15

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin

PROGNAME=supervisord

DAEMON=/usr/local/bin/$PROGNAME

CONFIG=/opt/app/supervisor/$PROGNAME.conf

PIDFILE=/tmp/$PROGNAME.pid

DESC="supervisord daemon"

SCRIPTNAME=/etc/init.d/$PROGNAME

# Gracefully exit if the package has been removed.

test -x $DAEMON || exit 0


start()

{

echo -n "Starting $DESC: $PROGNAME"

$DAEMON -c $CONFIG

echo ".............start success"

}

stop()

{

echo "Stopping $DESC: $PROGNAME"

if [ -f "$PIDFILE" ];
then
supervisor_pid=$(cat $PIDFILE)
kill -15 $supervisor_pid
echo "......"
echo "stop success"
else
echo "$DESC: $PROGNAME is not Runing"
echo ".........................stop sucess"
fi
}

status()

{ statusport=`netstat -lntp|grep 9001|awk -F ' ' '{print $4}'|awk -F ':' '{print $2}'`

if [ -f "$PIDFILE" ];
then
supervisor_pid=$(cat $PIDFILE)
echo "$DESC: $PROGNAME is Runing pid=$supervisor_pid"
else
echo "$DESC: $PROGNAME is not Runing"
echo "please use command /etc/init.d/supervisord start Run the service"
fi
}

case "$1" in

start)

start

;;

stop)

stop

;;

restart)

stop

start

;;

status)

status

;;

*)

echo "Usage: $SCRIPTNAME {start|stop|restart}" >&2

exit 1

;;

esac

exit 0

```


> 放入配置文件

```
cp supervisord.conf /opt/app/supervisor/conf.d/.



```
