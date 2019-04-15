# -*- coding: utf-8 -*-
__author__ = 'antonio.shen'

from kafka import KafkaProducer

from django.conf import settings
from django.forms.models import model_to_dict
from .models import Topic,Wechat
import logging
import json
import base64
import datetime

class TopicKafka:

    producer = None
    KAFKA_CONF = settings.KAFKA_CONFIG

    def __init__(self):
        if not settings.KAFKA_ENABLE:
            return
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_CONF['bootstrap_servers'])

    def get_producer(self):
        return self.producer


logger = logging.getLogger()

KAFKA_CONF = settings.KAFKA_CONFIG

topic_kafka = TopicKafka()

def public_topic(topic_id):

    # 如果没有kafka消息推送，将自动忽略
    if not settings.KAFKA_ENABLE:
        return
    topic_data = get_topic(topic_id)
    if topic_data is None:
        logger.error('主题消息[%s]为空，不能进行分发' % (topic_id))
        return
    logger.info(topic_data)
    producer = topic_kafka.get_producer()
    producer.send(KAFKA_CONF["topic"], json.dumps(topic_data, cls=DateEncoder))
    producer.flush()
    logger.info('topic[%s]发布成功' % (topic_id.encode('utf-8')))
    return

def get_topic(topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic is None:
        logger.error('主题消息[%s]为空，不能进行分发' % (topic_id))
        return
    #获取主题内容信息
    topic_data = model_to_dict(topic)
    wechat = Wechat.objects.get(id=topic.wechat_id)
    if wechat is None:
        logger.error('主题消息[%s],对应的公众号[%s]为空，无法分发公众号信息' % (topic_id, topic.wechat_id))
    else:
        topic_data["wechat_name"] = wechat.name
        topic_data["wechatid"] = wechat.wechatid

    topic_data["source"] = base64.b64encode(topic_data["source"].encode('utf-8'))
    topic_data["content"] = ''
    return topic_data


def props_with_(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            pr[name] = value
    return pr

class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)
