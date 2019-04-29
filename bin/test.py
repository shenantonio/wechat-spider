# -*- coding: utf-8 -*-
import urllib
import socket
#from base64 import b64encode
import base64
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka import TopicPartition

def get_ip():
    exip = ''
    ipList = socket.gethostbyname_ex(socket.gethostname())

    for itemList in ipList:
        if isinstance(itemList, list):
                for ip in itemList:
                    print '####:',ip
                    if ip not in ['192.168.11.58']:
                        exip = ip
    return exip


def save_ip(exip):
    if exip:
        params = urllib.urlencode({'host': exip, 'port': 808})
        f = urllib.urlopen("http://wechatspider.0fenbei.com/wechat/proxy/1/edit/", params)
        print f.read()

if __name__ == '__main__':
    # producer = KafkaProducer(bootstrap_servers='localhost:9092')
    #for _ in range(100):
    # producer.send('foobar', b'some_message_bytes')
    # print 'send complete'
    # producer.flush()
    consumer = KafkaConsumer('wechat_topic', bootstrap_servers='localhost:9092',
        group_id='my_favorite_group1', auto_offset_reset='earliest')
    #consumer.subscribe(['foobar'])
    for msg in consumer:
        print msg
