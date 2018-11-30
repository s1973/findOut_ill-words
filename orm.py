#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'find out illegal words'
__author__ = 's1973'


import asyncio
import aiomysql
import pymysql
import logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s")


async def create_pool(loop, **kw):
    logging.info('create database connection pool......')
    # 全局__pool用于存储整个连接池
    global __pool
    __pool = await aiomysql.create_pool(
        # **kw参数可以包含所有连接需要用到的关键字参数
        # 默认本机IP
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),  # 注意是utf8
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),

        # 接收一个event_loop实例
        loop=loop
    )


def query(sql, **kw):
    # 打开数据库连接
    db = pymysql.connect(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),  # 注意是utf8
        cursorclass=pymysql.cursors.DictCursor
    )
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    data=[]
    # 使用 execute()  方法执行 SQL 查询
    try:
        cursor.execute(sql)
        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchall()
    finally:
        # 关闭数据库连接
        db.close()
    return data


async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        # DictCursor is a cursor which returns as a dictionary
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                # 替换占位符，执行SQL语句
                await cur.execute(sql.replace('?', '%s'), args or ())
                if size:
                    rs = await cur.fetchmany(size)
                else:
                    rs = await cur.fetchall()
        except BaseException:
            raise
        finally:
            conn.close()
        logging.info('rows returned: %s ' % len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException:
            if not autocommit:
                await conn.rollback()
                raise
        finally:
            conn.close()
        return affected

# 根据参数数量生成SQL占位符'?'列表，


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    # 以', '为分隔符，将列表合成字符串
    return ', '.join(L)


def log(sql, args=()):
    logging.info('SQL: %s' % sql)
