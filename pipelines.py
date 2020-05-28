# -*- coding: utf-8 -*-
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ZhaobiaoPipeline(object):

    def __init__(self):
        self.mysql_conn = pymysql.Connection(
            host = 'localhost',
            port = 3306,
            user = 'root',
            password = '',
            database = 'zhaobiao',
            charset = 'utf8',
        )

    def process_item(self, item, spider):
        #创建光标
        cs = self.mysql_conn.cursor()
        #字段  取键
        sql_column = ','.join([key for key in item.keys()])
        #值  取值
        sql_value = ','.join(['"%s"' % item[key] for key in item.keys()])
        sql_str = 'insert into t_zhaobiao (%s) value (%s)' %(sql_column,sql_value)
        print(sql_str)
        cs.execute(sql_str)
        self.mysql_conn.commit()
        return item
