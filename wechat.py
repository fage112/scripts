#!/bin/env python
#encoding: utf-8
#send msg to the wechat app.
#python version 2.6
import json,urllib2,time
class wechat():
    version="1.0.0"
    def __init__(self):
        self.CropID='********'
        self.Secret='**************************'
        self.Gurl="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+ \
        self.CropID+"&corpsecret="+self.Secret
        self.Response=urllib2.urlopen(self.Gurl)
        self.Json_data=json.load(self.Response)
        self.Token=self.Json_data["access_token"]
        self.TimeStamp=int(time.time())
        self.Purl="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" \
        +self.Token
        self.AppID=1
        #Appid 填写企业号中建立的报警APP的ID
        self.UserID="@all"
        #此处填写报警接收用户，全部报警可留空
        self.PartyID=2
        self.TagID=2
        self.AgentID=1
        self.Date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    def Send_msg(self,Title,Msg):
        msg=self.Date+"\n"+Msg
        Data={"touser":self.UserID,"toparty":self.PartyID,"msgtype": "news", \
        "agentid":self.AgentID,"news":{"articles":[{"title":Title,"description" \
        :msg,"url":"","picurl":""}]}}
        data=json.dumps(Data,ensure_ascii=False).encode('utf8')
        request=urllib2.Request(self.Purl,data)
        ResponseData=urllib2.urlopen(request)
        Response_show=json.load(ResponseData)
        if Response_show["errcode"]==0 and Response_show["errmsg"]=='ok':
            print "Send wechat msg sucess"
        else:
            print "Send msg faild!"
if __name__=="__main__":
    Title=u"大家好"
    Msg=u"我又来测试了"
    Run=wechat()
    Run.Send_msg(Title,Msg)