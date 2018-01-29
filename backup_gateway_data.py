#!/bin/env python
#coding: utf-8
#backup gatewaymapping config
#python version 2.6
import ConfigParser,json,urllib2,os
import send_mail
cfg_file='/home/lichengfa/shell/back_vos_gatewaymapping/config.conf'
def get_gatewaymapping_config(url,gatewayname):
    """通post方法，调用vos的http接口，并返回vos返回的数据"""
    values={"names":[gatewayname]}
    data=json.dumps(values)
    request=urllib2.Request(url,data)
    response=urllib2.urlopen(request).read()
    responseData=json.loads(response)
    return responseData
def run():
    c=ConfigParser.ConfigParser()
    c.read(cfg_file)
    secs=c.sections()
    for host in secs:
        os.chdir('/home/lichengfa/shell/back_vos_gatewaymapping/')
        if os.path.isfile(host+'.txt'):
            os.remove(host+'.txt')
        opts=c.options(host)
        for o in opts:
            if o=="gatewaymapping":
                gatewaymapping=c.get(host,o).split(',')
            elif o=="url":
                URL=c.get(host,o)
            else:
                e_mail=c.get(host,o).split(",")
        for gatewayname in gatewaymapping:
            a=get_gatewaymapping_config(URL,gatewayname)
            if a['retCode']==0:
                msg={}
                msg['calloutCalleePrefixes']=a['infoGatewayMappings'][0]['calloutCalleePrefixes']
                msg['calloutCalleePrefixesAllow']=a['infoGatewayMappings'][0]['calloutCalleePrefixesAllow']
                msg['rewriteRulesOutCallee']=a['infoGatewayMappings'][0]['rewriteRulesOutCallee']
                msg['calloutCallerPrefixesAllow']=a['infoGatewayMappings'][0]['calloutCallerPrefixesAllow']
                msg['rewriteRulesOutCallee']=a['infoGatewayMappings'][0]['rewriteRulesOutCallee']
                f=open(host+'.txt','a')
                f.write(gatewayname+'\n')
                for k,v in msg.items():
                    i=str(k)+':'+str(v)+'\n'
                    f.write(str(i))
                f.write('\n\n')
                f.close()
        From='notice_fage@aliyun.com'
        To=e_mail
        Obj='对接网关备份数据'
        Msg="calloutCallerPrefixesAllow:呼出主叫前缀，False代表禁止， \
        True代表允许\ncalloutCalleePrefixesAllow:呼出被叫前缀，False代表禁止， \
        True代表允许\nrewriteRulesOutCallee: \
        呼出被叫改写规则\ncalloutCalleePrefixes:呼出被叫前缀"
        Path_To_File=[host+'.txt']
        send_mail.send_mail_attachment(From,To,Obj,Msg,Path_To_File)
if __name__=='__main__':
    run()