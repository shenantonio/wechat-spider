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
