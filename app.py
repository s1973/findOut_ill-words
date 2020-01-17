#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'find out illegal words'
__author__ = 's1973'

from config import configs
import os,time,random,re,subprocess,asyncio
import orm
import logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)
from multiprocessing import Pool

db_local = configs.db
db_remote = configs.db2

def addWords(file='asset/illegal_words.txt', override=True):
    if override:
        orm.query(r'delete from `illegal_words`', **db_local)
    with open(file, 'r', encoding='UTF-8') as f:
        line = f.readline().strip()
        illegal_words = line.split(',')
    for v in illegal_words:
        rs = orm.query(r'insert into `illegal_words` (word) values ("'+v+'")', **db_local)
    return rs


def regExpress():
    rs = orm.query(r'select word from illegal_words', **db_local)
    reg = r''
    for w in rs:
        reg += (w['word'] + r'|') if w['word'] != r'*' else ('\\' +w['word'] + r'|')
    reg = reg.strip('|')
    logging.info('re：'+reg)
    return re.compile(reg, re.U)


async def findOut(pattern, string):
    rs = pattern.findall(string)
    if rs:logging.info('结果：'+','.join(rs))
    return rs

def save(data):
    sql = r"insert into `illegal_result` (`keys`,title,postid,parent_id,class_name,t_table,created_at,sitename,domain,en_project,siteid,url) values "
    for site in data:
        for i in site:
            sql += '('
            for v in i.values():
                sql+="'"+str(v)+"',"
            sql=sql.strip(',')
            sql += '),'
    sql = sql.strip(',')
    print(sql)
    orm.query(sql,**db_local)


def fetchSites():
    sites = orm.query(r'select * from site order by id asc limit 10', **db_local)
    return sites


async def init(loop,site,pattern):
    data = []
    db_remote['db'] = site['en_project']
    await orm.create_pool(loop=loop, **db_remote)
    classes = await orm.select("select id,name,t_table from class where t_table REGEXP ?", ['news|product'])
    for c in classes:
        posts = await orm.select("select * from `"+c['t_table']+"`", [])
        for p in posts:
            illegals = await findOut(pattern, p['name']+p['content'])
            if illegals:
                data.append({
                    'keys': ','.join(illegals),
                    'title': p['name'],
                    'postid': p['id'],
                    'parent_id': p['parent_id'],
                    'class_name': c['name'],
                    't_table': c['t_table'],
                    'created_at': int(time.time()),
                    'sitename': site['cn_project'],
                    'domain': site['domain'],
                    'en_project': site['en_project'],
                    'siteid':site['id'],
                    'url':r'http://'+site['domain']+'/view'+str(p['parent_id'])+'-'+str(p['id'])+r'.html'
                })
    return data

def entry(site,pattern,i):
    print('Run task %s (%s)...' % (i, os.getpid()))
    start = time.time()
    loop = asyncio.get_event_loop()
    r = loop.run_until_complete(init(loop,site,pattern))
    end = time.time()
    print('Task %s runs %0.2f seconds.\n' % (i, (end - start)))
    return r

if __name__ == '__main__':
    print('Parent process %s.\n' % os.getpid())
    result = [] 
    p = Pool(10)
    sites = fetchSites()
    # addWords()
    pattern = regExpress()
    for i in range(len(sites)):
        r = p.apply_async(entry, args=(sites[i],pattern, i,))
        if r.get():
            print(r.get())
            result.append(r)
    p.close()
    p.join()
    print('all processes done')
    data = []
    for res in result:
        data.append(res.get())
    if data:save(data)
    with open('asset/'+'result'+time.strftime("%Y-%m-%d", time.localtime())+'.txt', 'w', encoding='UTF-8') as f:
        for line in data:
            f.write('%s\n' % line)
