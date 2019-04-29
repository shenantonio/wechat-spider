# -*- coding: utf-8 -*-
import re
import logging
logger = logging.getLogger()



if __name__ == '__main__':
    url='https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPjOjIEA1OjSicXHcia9Mj9RQjt5ShpQk1osU06b4tLD5lryZSy2G54X0NC3y272Pic4b22s7NbZrDDeQ/640??'
    tf = re.match('((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',url)
    logging.info(tf)
    if not tf:
        logging.error('not match')
    else:
        logging.error('match')
