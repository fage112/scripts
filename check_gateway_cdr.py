#!/bin/env python
#coding: utf-8
#python serion 2.6
import os,MySQLdb,time,ConfigParser
User='****'
Passwd='*****'
long=90             #查询时长
DJ_before={}        #三个内有通话的对接
DJ_current={}       #vos目前所有的对接
LD_before={}        #三个内有通话的落地
LD_current={}       #vos目前所有的落地
S_list=['DJ_before','DJ_current','LD_before','LD_current']  #需要查询数据的列表
os.chdir('*****')
def read_config():
    """读取配置文件"""
    config_file='config'
    c=ConfigParser.ConfigParser()
    c.read(config_file)
    host=c.get('HOST','host').split(',')
    return host
def write_sql(long,Data):
    """自动写sql语句，long变量为统计多久以内话单的数据，Data为要
    查询的字段，如统计3个月有话单的对接"""
    Now=int(time.time())
    Sql=[]
    Sql.append('SELECT '+Data+' FROM e_cdr_'+time.strftime("%Y%m%d",time.gmtime(Now))+' GROUP BY '+Data+' UNION ')
    for i in range(long):
        Date=time.strftime("%Y%m%d",time.gmtime(Now-i*84600))
        sql='SELECT '+Data+' FROM e_cdr_'+Date+' GROUP BY '+Data+' UNION '
        Sql[0]=Sql[0]+sql
    return Sql[0].strip(' UNION')+';'
def get_value(host,sql,op):
    """连接数据库，获取数据，sql为sql查询语句，op为要查询的字段，如统计3个月有话单的对接"""
    try:
        conn=MySQLdb.connect(host,User,Passwd,'test',3306,charset="utf8")
        cur=conn.cursor()
        cur.execute(sql)
        Result=cur.fetchall()
        cur.close()
    except MySQLdb.Error,e:
        print e
    names=globals()
    if op=='DJ_before':
        names['DJ_before']['%s' %host]=Result
    elif op=='DJ_current':
        names['DJ_current']['%s' %host]=Result
    elif op=='LD_before':
        names['LD_before']['%s' %host]=Result
    else:
        names['LD_current']['%s' %host]=Result
def compare(before,current):
    '''计算两个数据的差集'''
        return list(current-before)
def run():
    '''程序运行主函数'''
    host=read_config()
    names=globals()
    for s in host:
        for l in S_list:
            if l=='DJ_before':
                Sql=write_sql(long,'callergatewayid')
            elif l=='DJ_current':
                Sql='SELECT name FROM e_gatewaymapping'
            elif l=='LD_before':
                Sql=write_sql(long,'calleegatewayid')
            else:
                Sql='SELECT name FROM e_gatewayrouting'
            get_value(s,Sql,l)
            names['%s_%s' %(s,l)]=set(names['%s' % l][s])
        names['%s_dj' % s]=compare(names['%s_DJ_before' % s],names['%s_DJ_current' % s])
        names['%s_ld' % s]=compare(names['%s_LD_before' % s],names['%s_LD_current' % s])
        print str(names['%s_dj' % s])
        for a in range(len(names['%s_dj' % s])):
            f=open('data/'+s,'a')
            if a<len(names['%s_dj' % s])-1:
                f.write(str(names['%s_dj' % s][a]).replace('u\'','\'').decode('unicode-escape').encode('utf-8'))
            else:
                f.write(str(names['%s_dj' % s][a]).replace('u\'','\'').decode('unicode-escape').encode('utf-8')+'\n')
        f.close()
        print str(names['%s_ld' % s])
        for a in range(len(names['%s_ld' % s])):
            f=open('data/'+s,'a')
            if a<len(names['%s_ld' % s])-1:
                f.write(str(names['%s_ld' % s][a]).replace('u\'','\'').decode('unicode-escape').encode('utf-8'))
            else:
                f.write(str(names['%s_ld' % s][a]).replace('u\'','\'').decode('unicode-escape').encode('utf-8')+'\n')
        f.close()
if __name__=="__main__":
    run()