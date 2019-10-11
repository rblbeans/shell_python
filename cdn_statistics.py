#!/bin/python
# coding=UTF-8
# author=RBLBeans

import datetime
import os
import random
import string
import baidu_cdn_conf 
from baidubce import compat
from baidubce import exception
from baidubce.exception import BceServerError
from baidubce.services.cdn.cdn_client import CdnClient
from baidubce.services.cdn.cdn_stats_param import CdnStatsParam
import xlsxwriter
import json
import imp
import sys
import time
from datetime import date
import hashlib
import requests
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

domain = [
    "cachebd.cdn.cibn.cc",
    "cachews.cdn.cibn.cc",
    "cachemmy.cdn.cibn.cc",
    "bd.hls.ott.cibntv.net",
    "ws.hls.ott.cibntv.net",
    "mmy.hls.ott.cibntv.net",
    ]

### compare ###
def compare(a,b):
    if a > b:   
        c = a
    else: 
        c = b
    return(c)
### compare end ###

### get yesterday ###
def yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    yesterday_start = datetime.datetime.strptime(str(yesterday)+"00:00:00", '%Y-%m-%d%H:%M:%S')
    yesterday_end = datetime.datetime.strptime(str(yesterday)+"23:55:00", '%Y-%m-%d%H:%M:%S')
    return(yesterday_start, yesterday_end)
### end get ###

### change str to flow in list(dict) ###
def dict_change_type(a=[]):
    b = []
    for i in range(0, len(a)):
        bps = a[i]["value"]
        timestamp = a[i]["time"]
        dic = {"value":float(bps), "timestamp":timestamp}
        b.append(dic)
    rs = sorted(b, key = lambda x:x["value"],reverse = True)
    return rs
### end change ###

### handle the ws data ###
def ws_hls_bandiwdth(domain):
    ws_hls = os.path.exists("/root/auto_cdn_statistics/ws.hls.ott.cibntv.net")
    ws_cache = os.path.exists("/root/auto_cdn_statistics/cache.cdn.cibn.cc")
    ws_flow = os.path.exists("/root/auto_cdn_statistics/total_hls_flow_ws")
    ws_total_flow = os.path.exists("/root/auto_cdn_statistics/total_flow_ws")
    ws_total_band = os.path.exists("/root/auto_cdn_statistics/total_bandwidth_ws")
    #if (ws_hls, ws_cache, ws_flow) == (False,False,False):
    #os.system('sh ws_domain.sh')
    f = open(domain, "r")
    load_dict = json.load(f)
    resault = 0
    a = []
    for i in range(0,len(load_dict)):
        bandwidth = load_dict[i]["bandwidth"]
        datetime = load_dict[i]["timestamp"]
        dic = {"bandwidth":float(bandwidth), "timestamp":datetime}
        a.append(dic)
    res_band = sorted(a, key = lambda x:x["bandwidth"],reverse = True)
    res_time = str(res_band[0]["timestamp"])
    res_band = res_band[0]["bandwidth"]
    return(res_band, res_time)

def ws_hls_flow():
    f = open("total_hls_flow_ws", "r")
    load_dict = json.load(f)
    resault = float(load_dict["flow-summary"])
    return(resault)

def ws_total_flow():
    f = open("total_flow_ws", "r")
    load_dict = json.load(f)
    resault = float(load_dict["flow-summary"])
    return(resault)

def ws_total_bandwidth():
    f = open("total_bandwidth_ws", "r")
    load_dict = json.load(f)
    resault = 0
    a = []
    for i in range(0,len(load_dict)):
        bandwidth = load_dict[i]["bandwidth"]
        datetime = load_dict[i]["timestamp"]
        dic = {"bandwidth":float(bandwidth), "timestamp":datetime}
        a.append(dic)
    res_band = sorted(a, key = lambda x:x["bandwidth"],reverse = True)
    res_band = res_band[0]["bandwidth"]
    return(res_band)

def ws_live_bandwidth():
    live_bandwidth = os.path.exists("/data/cdn/total_bandwidth_all")
    live_flow = os.path.exists("/data/cdn/total_flow_all")
    #if (live_bandwidth, live_flow) == (False,False):
    #    os.system('sh /data/cdn/ws_domain.sh')
    f = open("live", "r")
    load_dict = json.load(f)
    resault = 0
    a = []
    for i in range(0,len(load_dict)):
        bandwidth = load_dict[i]["bandwidth"]
        datetime = load_dict[i]["timestamp"]
        dic = {"bandwidth":float(bandwidth), "timestamp":datetime}
        a.append(dic)
    res_band = sorted(a, key = lambda x:x["bandwidth"],reverse = True)
    res_time = str(res_band[0]["timestamp"])
    res_band = res_band[0]["bandwidth"]
    return(res_band)

def ws_live_flow():
    f = open("live_flow", "r")
    dict_ws = float(json.load(f)["flow-summary"])
    return(dict_ws)

def ws_handle():
    cachews = '%.2f' % (float(ws_hls_bandiwdth(domain[1])[0])/1000)
    ws_peaktime = ws_hls_bandiwdth(domain[1])[1].split()[1]
    hlsws = '%.2f' % (float(ws_hls_bandiwdth(domain[4])[0])/1000)
    total_hls_ws = '%.2f' % (float(cachews) + float(hlsws))
    total_bandwidth_ws = '%.2f' % (float(ws_total_bandwidth()/1000))
    total_flow_ws = '%.2f' % (float(ws_total_flow()/1000))
    wsflow = 0.0
    wsflow = '%.2f' % (ws_hls_flow()/1000)
    ws_live_band = '%.2f' % (ws_live_bandwidth()/1000)
    ws_live_fl = '%.2f' % (ws_live_flow()/1000)
    ws_room = [
        total_hls_ws,
        wsflow,
        cachews,
        hlsws,
        ws_peaktime,
    ]
    return(ws_room, total_bandwidth_ws, total_flow_ws, ws_live_band, ws_live_fl)
    #return(ws_room, total_bandwidth_ws, total_flow_ws)
### ws data end ###

### handle baidu data ###
def bd_stats_flow(c, key):
    a = []
    rs_bps = 0
    rs_flow = 0
    utc = datetime.timedelta(hours=8)
    yesterday_start = yesterday()[0]
    yesterday_end = yesterday()[1]
    yesterday_start = yesterday_start - utc
    yesterday_end = yesterday_end - utc
    start_time = yesterday_start.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
    end_time = yesterday_end.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
    param = CdnStatsParam(start_time=start_time, end_time=end_time, key_type=0,period=300, groupBy="")
    param.key=key
    param.metric = 'flow'
    param.level = 'all'
    response = c.get_domain_stats(param)
    load_list = response.details
    for i in range(0, len(load_list)):
        bps = load_list[i].bps
        flow = load_list[i].flow
        timestamp = load_list[i].timestamp
        timestamp = datetime.datetime.strptime(str(timestamp),'%Y-%m-%d'+"T"+'%H:%M:%S'+"Z") 
        timestamp = timestamp + utc
        timestamp = timestamp.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
        dic = {"bandwidth":float(bps), "timestamp":timestamp}
        a.append(dic)
        rs_flow += flow     
    rs = sorted(a, key = lambda x:x["bandwidth"],reverse = True)
    rs = rs[0] 
    return(rs, rs_flow)

def baidu_list_domains():
    """
    baidu_list_domains
    """
    a = []
    c = CdnClient(baidu_cdn_conf.config)
    load_list = c.list_domains().domains
    for i in range(0, len(load_list)):
        a.append(load_list[i].name)
    return(a)

def bd_total_flow_band(c):
    a = []
    rs_bps = 0
    rs_flow = 0
    utc = datetime.timedelta(hours=8)
    yesterday_start = yesterday()[0]
    yesterday_end = yesterday()[1]
    yesterday_start = yesterday_start - utc
    yesterday_end = yesterday_end - utc
    start_time = yesterday_start.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
    end_time = yesterday_end.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
    key = baidu_list_domains()
    param = CdnStatsParam(start_time=start_time, end_time=end_time, key_type=0,period=300, groupBy="")
    param.key=key
    param.metric = 'flow'
    param.level = 'all'
    response = c.get_domain_stats(param)
    load_list = response.details
    for i in range(0, len(load_list)):
        bps = load_list[i].bps
        flow = load_list[i].flow
        #timestamp = load_list[i].timestamp
        #timestamp = datetime.datetime.strptime(str(timestamp),'%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
        #timestamp = timestamp + utc
        #timestamp = timestamp.strftime('%Y-%m-%d'+"T"+'%H:%M:%S'+"Z")
        #dic = {"bandwidth":float(bps), "timestamp":timestamp}
        a.append(bps)
        rs_flow += flow
    #rs = sorted(a, key = lambda x:x["bandwidth"],reverse = True)
    #rs = a.sort(reverse=True)
    a.sort(reverse=True)
    rs = a[0]
    return(rs, rs_flow)

def bd_handle():
    c = CdnClient(baidu_cdn_conf.config)
    cachebd = '%.2f' % (bd_stats_flow(c, [domain[0]])[0]["bandwidth"]/1000/1000/1000)
    hlsbd = '%.2f' % (bd_stats_flow(c, [domain[3]])[0]["bandwidth"]/1000/1000/1000)
    peak_time = bd_stats_flow(c, [domain[0]])[0]["timestamp"]
    peak_time = str(peak_time).replace("T"," ").strip("Z").split()[1]
    total_hls_bd = '%.2f' % (float(cachebd) + float(hlsbd))
    hls_flow = '%.2f' % (bd_stats_flow(c, [domain[0], domain[3]])[1]/1000/1000/1000)
    total_bandwidth = '%.2f' % (bd_total_flow_band(c)[0]/1000/1000/1000)
    total_flow = '%.2f' % (bd_total_flow_band(c)[1]/1000/1000/1000)
    bd_room = [
        total_hls_bd,
        hls_flow,
        cachebd,
        hlsbd,
        peak_time,
    ]
    return(bd_room, total_bandwidth, total_flow)
### baidu data end ###

### handle mmy data ###
def getToken(username,timestamp,apiKey):
    token = md5(md5(username)+str(timestamp)+apiKey)
    return token

def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    psw = m.hexdigest()
    return psw

def mmy_stats_flow():
    username="cibnmmy"
    apiKey="3h6EL^4Yc3KfioFc"
    t = time.time()
    nowTime = lambda:int(round(t * 1000))
    timestamp=nowTime()
    startTime = yesterday()[0]
    startTime = startTime.strftime('%Y%m%d%H%M')
    endTime = yesterday()[1] 
    endTime = endTime.strftime('%Y%m%d%H%M')
    token = getToken(username, timestamp, apiKey)
    domain_list = "https://api.chinamaincloud.cn/api/public/domain?timestamp="+ str(timestamp) + \
                  "&username=cibnmmy&token="+ str(token) 

    cachemmy = "https://api.chinamaincloud.cn/api/public/bill/bandwidth?timestamp="+ str(timestamp) + \
               "&username=cibnmmy&token="+ str(token) + \
               "&domains=2161&starttime="+ str(startTime) +"&endtime="+ str(endTime)
    #mmyhls = "https://api.chinamaincloud.cn/api/public/bill/bandwidth?timestamp="+ str(timestamp) + \
    #         "&username=cibnmmy&token="+ str(token) + \
    #         "&domains=53&starttime="+ str(startTime) +"&endtime="+ str(endTime)
    flow = "https://api.chinamaincloud.cn/api/public/bill/flow?timestamp="+ str(timestamp) + \
           "&username=cibnmmy&token="+ str(token) + \
           "&domains=2161&starttime="+ str(startTime) +"&endtime="+ str(endTime)
    request_bandwidth = requests.get(cachemmy).text
    request_bandwidth = json.loads(request_bandwidth)["data"]
    request_bandwidth = dict_change_type(request_bandwidth)[0]
    request_flow = requests.get(flow).text
    request_flow = json.loads(request_flow)["data"]
    request_flow = dict_change_type(request_flow)[0]
    request_domain = requests.get(domain_list).text
    request_domain = json.loads(request_domain)["data"]
    a = []
    for i in range(0, len(request_domain)):
        a.append(request_domain[i]["domainId"])
    s = ",".join(str(j) for j in a)
    total_bandwidth = "https://api.chinamaincloud.cn/api/public/bill/bandwidth?timestamp="+ str(timestamp) + \
                          "&username=cibnmmy&token="+ str(token) + \
                          "&domains="+s+"&starttime="+ str(startTime) +"&endtime="+ str(endTime)
    total_flow = "https://api.chinamaincloud.cn/api/public/bill/flow?timestamp="+ str(timestamp) + \
           "&username=cibnmmy&token="+ str(token) + \
           "&domains="+s+"&starttime="+ str(startTime) +"&endtime="+ str(endTime)

    request_total_band = requests.get(total_bandwidth).text
    request_total_band = json.loads(request_total_band)["data"]
    request_total_band = dict_change_type(request_total_band)[0]
    request_total_flow = requests.get(total_flow).text
    request_total_flow = json.loads(request_total_flow)["data"]
    request_total_flow = dict_change_type(request_total_flow)[0]
    return(request_bandwidth, request_flow,request_total_band,request_total_flow)

def mmy_handle():
    cachemmy = '%.2f' % (mmy_stats_flow()[0]["value"]/1000/1000/1000)
    hlsmmy = 0
    peak_time = mmy_stats_flow()[0]["timestamp"]
    peak_time = str(peak_time[-4:-2])+":"+str(peak_time[-2:])+":00"
    total_hls_flow = '%.2f' % (mmy_stats_flow()[1]["value"]/1000/1000/1000)
    total_hls_band = float(cachemmy) + float(hlsmmy)
    total_band = '%.2f' % (mmy_stats_flow()[2]["value"]/1000/1000/1000) 
    total_flow = '%.2f' % (mmy_stats_flow()[3]["value"]/1000/1000/1000)
    mmy_room = [
        total_hls_band,
        total_hls_flow,
        cachemmy,
        hlsmmy,
        peak_time
    ]
    return(mmy_room, total_band, total_flow) 
### mmy data end ###

### handle the excel ###
def handle_excel():
    title_room = [
    u"商业CDN厂商",
    u"当天点播峰值带宽",
    u"当天点播流量总量",
    u"新点播\n当天点播峰值带宽",
    u"旧点播\n当天点播峰值带宽",
    u"当天点播峰值时间",
    u"当天点播合计带宽",
    ]
    live_room = [
    u"直轮播总带宽",
    u"直轮播总流量",
    ]
    total_room = [
    u"总带宽",
    u"总流量",
    u"百度总量",
    u"网宿总量",
    u"蛮蛮云总量",
    ]
    cdn_room = [
    u"百度",
    u"网宿",
    u"蛮蛮云",
    ]
    wbk = xlsxwriter.Workbook(u'每日商业CDN统计情况.xlsx')
    title_format = wbk.add_format({
        'align':'center',
        'valign':'vcenter',
        'font_size':24,
        'border':1

      })
    second_title_format = wbk.add_format({
        'bold': False, #字体加粗
        'border':1,     #单元格边框宽度
        'align':'center', #水平对齐方式
        'valign':'vcenter', #垂直对齐方式
        'font_size':14,  #字体大小
        'text_wrap': True, #是否自动换行
        'fg_color':'#FFFFFF' #单元格背景颜色
      })
    common_format = wbk.add_format({
        'align':'center',
        'valign':'vcenter',
        'font_size':12,
        'border':1
      })
    bd_room = bd_handle()[0]
    ws_room = ws_handle()[0]
    mmy_room = mmy_handle()[0]
    ws_bandwidth = ws_handle()[1]
    ws_flow = ws_handle()[2]
    mmy_bandwidth = mmy_handle()[1]
    mmy_flow = mmy_handle()[2]
    bd_bandwidth = bd_handle()[1]
    bd_flow = bd_handle()[2]
    total_live_band = ws_handle()[3]
    total_live_flow = ws_handle()[4]
    total_hls_band = float(bd_room[0]) + float(ws_room[0]) + float(mmy_room[0])
    total_band = float(ws_bandwidth) + float(mmy_bandwidth) + float(bd_bandwidth)
    total_flow = float(ws_flow) + float(mmy_flow) + float(bd_flow)
    yesterday = date.today()+datetime.timedelta(days=-1)
    sheet = wbk.add_worksheet(u'statistics')
    sheet.set_row(0, 40)
    sheet.set_row(1,20)
    sheet.set_column('A1:G1', 20)
    sheet.set_column('A7:G7', 20)        #设置单元格宽度
    sheet.merge_range('A1:G1', u'每日商业CDN统计情况-'+str(yesterday), title_format)
    sheet.write_row('A2', total_room, second_title_format)
    sheet.merge_range('A3:A5', total_band, common_format)
    sheet.merge_range('B3:B5', total_flow, common_format)
    sheet.merge_range('C3:C5', bd_bandwidth, common_format)
    sheet.merge_range('D3:D5', ws_bandwidth, common_format)
    sheet.merge_range('E3:E5', mmy_bandwidth, common_format)
    sheet.write_row('A7', title_room, second_title_format)
    sheet.write_column('A8',cdn_room,common_format)
    sheet.write_row('B8',bd_room,common_format)
    sheet.write_row('B9',ws_room,common_format)
    sheet.write_row('B10',mmy_room,common_format)
    sheet.merge_range('G8:G10', total_hls_band, common_format)
    sheet.write_row('A12', live_room, second_title_format)
    sheet.merge_range('A13:A15', total_live_band, common_format)
    sheet.merge_range('B13:B15', total_live_flow, common_format)
    sheet.merge_range('A16:B16', u'TIPs:所有数据单位为G')
    wbk.close()
### end handle excel ###

### cpid accurate ###
def cpid_accurate():
    os.system('sh cpid_accurate.sh')
    f = open("total_stream","r")
### end cpid ##

### sendmail ###
def sendmail():
    os.system('sh /root/auto_cdn_statistics/ws_domain.sh')
    handle_excel() 
    # 第三方 SMTP 服务
    mail_host = "mail.cri.cn"      # SMTP服务器
    #mail_pass = "yxHaeSn6Ma"               # 密码
    mail_pass = "Lizh163com"               # 密码
 
    sender = 'liziheng@cri.cn'    # 发件人邮箱
    receivers = [
                 "liziheng@cri.cn","guanyue@cri.cn", "yangqinghai@cri.cn"
                ] # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    cc = [ "yunweijiekou@cri.cn","zunyunlei@cri.cn","kehengzhong@cri.cn" ]
    xlsFile = '每日商业CDN统计情况.xlsx'
    xlsApart = MIMEApplication(open(xlsFile, 'rb').read())
    xlsApart.add_header('Content-Disposition', 'attachment', filename=xlsFile)

    content = '各位好:\n  附件为昨日统计情况'
    title = '每日商业CDN统计情况'  # 邮件主题
    textApart = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    
    m = MIMEMultipart()
    m.attach(textApart)
    m.attach(xlsApart)
    m['Subject'] = title
    m['To'] = ','.join(receivers)
    m['Cc'] = ','.join(cc)
    m['From'] = sender
    try:
        smtpObj = smtplib.SMTP(mail_host)  
        smtpObj.login(sender, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers + cc, m.as_string())  # 发送
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print(e)
    os.system('rm -f cachews.cdn.cibn.cc ws.hls.ott.cibntv.net total_flow_ws total_bandwidth_ws total_hls_flow_ws live live_flow')
### end send ###

### main ###
if __name__ == "__main__":
    os.system('sh /root/auto_cdn_statistics/ws_domain.sh')
    #sendmail()
    handle_excel() 
    os.system('rm -f cachews.cdn.cibn.cc ws.hls.ott.cibntv.net total_flow_ws total_bandwidth_ws total_hls_flow_ws live live_flow')
### END ###
