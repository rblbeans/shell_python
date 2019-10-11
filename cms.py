#encoding=UTF-8
import json
import requests
import os
import urllib
import sys 
reload(sys) 
sys.setdefaultencoding('gb18030')
movie = {}                                                      #初始化
f = open("cmsfid.txt", "r")                                     #打开包含fid或url字段的文件
f2 = open("cmsname.txt", "r")                                   #打开包含节目名称字段的文件
strs = "http://"
cache_url = "http://10.168.200.54:8181"
requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False
for fid_line,name_line in zip(f.readlines(),f2.readlines()):    #并发读取文件内容
    movie["name"] = name_line                                   #将名字加到movie字典中name字段
    data = json.loads(fid_line)
    movie["details"] = data                                     #将fid或url字段加到movie字典detatls字段
    json_dump = json.dumps(movie, ensure_ascii=False)           #字典转换json
    dict_data = json.loads(json_dump)
    details = dict_data["details"]
    name = dict_data["name"]

    """
    获取并更改相对应的m3u8文件地址
    将子节目进行编号
    """

    for i in range(0,len(details)):
        fid_or_url = details[i]
        child_name = str(name.replace("\r\n", "")) + str(i + 1)
        if not os.path.exists(child_name):
	    child_name = child_name.decode('gbk').encode('utf-8')
            os.mkdir(child_name)
        if ("fid" in fid_or_url):
            fid = fid_or_url["fid"]
            http = cache_url+"/m3u8/"+str(fid[0])+".m3u8"
            response = requests.get(http)
            #print(child_name+"  "+str(response.content))
            #print(child_name+"    "+http)
        elif ("url" in fid_or_url):
            url = fid_or_url["url"][0]
            url_format = str(url.replace("hls01.ott.disp.cibntv.net", "10.168.200.152"))
            response = requests.get(url_format)
            #print(str(name.replace("\n", ""))+"  "+str(response.content))
            #print(str(name.replace("\n", ""))+str(i+1)+"    "+url_format)

        if response.status_code != 200:
            print(child_name+"  "+str(response.status_code))
        else:
            #print(child_name+"  "+str(response.content))
            if ("hls01.ott.disp.cibntv.net" in response.text):
                replace = response.text.replace("hls01.ott.disp.cibntv.net", "10.168.200.152")
                #print(child_name+"  "+replace)
            elif ("/segview" in response.text):
                replace = response.text.replace("/segview",cache_url+"/segview")

            #urllib.request.urlretrieve(response.text)
            #print(str(response.text))
        if not os.path.exists(child_name+"/"+child_name+".txt"):
            f3 = open(child_name+"/"+child_name+".txt","a")
            f3.write(replace)
            f3.close()
        print(child_name+"  "+str(replace))
f.close()
f2.close()




