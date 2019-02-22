#!/usr/bin/python
#-*-coding:utf8-*-


import socket
import fcntl
import time
import struct
import smtplib
import urllib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import re
import urllib2
import json
import sys

reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')

# the e-mail config
# this is just a simple format,this e-mail doesn't exist.
smtpserver = "smtp.163.com"
smtp_port = 25
smtp_ssl_port = 465
username = "xxxx@163.com"
password = "xxxx"
sender = "yyyy@163.com"
receiver = ["1@163.com","2@163.com"]
subject = "Git Push"

smtpserver = "smtp.ym.163.com"
username = "2@163.com"
sender = "1@163.com"

def sendEmail(msghtml):
    '''
    msghtml为拼装的邮件html内容
    '''
    msgRoot = MIMEMultipart('related')
    msgRoot["To"] = ','.join(receiver)
    msgRoot["From"] = sender
    msgRoot['Subject'] =  Header(subject, 'utf-8')
    #msg = MIMEText(u'<a href="www.google.com">abc</a>','html')
    msgText = MIMEText(msghtml,'html','utf-8')
    msgRoot.attach(msgText)
    #smtp = smtplib.SMTP_SSL(smtpserver, smtp_ssl_port)
    smtp = smtplib.SMTP(smtpserver, int(smtp_port))
    #smtp = smtplib.SMTP()
    #smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()

def sendNotify(push_json):
    '''
    push_json为gitbucket的hook webservice推送的json
    '''
    #解析出push的开发者
    js = json.loads(push_json)
    print json.dumps(js, indent=4,ensure_ascii=False)
    #解析出push的差异浏览链接
    compare_url = js["compare"]
    print compare_url
    #解析repository
    repository_url = js["repository"]["url"]
    repository_name = js["repository"]["name"]
    repository_html = '''<a href="%s"> %s </a>'''%(repository_url,repository_name)
    #解析分支名称
    #"ref": "refs/heads/dev_new_ecg_report",
    branch_str = js["ref"]
    branch_name = branch_str.split("/")[2]
    branch_tag = branch_str.split("/")[1]
    branch_url = repository_url + "/tree/" + branch_name
    branch_html = '''<a href="%s"> %s </a>'''%(branch_url,branch_name)

    #dev = js["head_commit"]["committer"]["name"]
    dev = js["pusher"]["name"]

    #解析after和before，判断是否为0000000000000000000000000000000000000000
    after = js["after"]
    before = js["before"]
    
    msg_head = """
        <html>
        <head></head>
        <body>
        <p><b>仓库</b>: %s</p>
        <p><b>提交者</b>: %s</p>"""%(repository_html,dev)
    msg_tail = """
        </body>
        </html>
    """
    msg_body = ""
    msg_format = '''<a href="%s"> <font color="red">%s</font> </a> -  %s <font color="green">(%s)</font> <font color="blue">&lt%s&gt</font>'''
    if(after == "0000000000000000000000000000000000000000"):
        if(branch_tag == "tags"):
            print "del tags " + branch_name
            msg_body = """<p><b>删除标签</b>: %s</p>"""%(branch_html)
        else:
            print "del branch " + branch_name
            msg_body = """<p><b>删除分支</b>: %s</p>"""%(branch_html)        
    elif(before == "0000000000000000000000000000000000000000"):        
        if(branch_tag == "tags"):
            print "add tags " + branch_name
            msg_body = """<p><b>创建标签</b>: %s</p>"""%(branch_html)
        else:
            print "add branch " + branch_name
            msg_body = """<p><b>创建分支</b>: %s</p>"""%(branch_html)
    else:    
        print "add some commit"
        diff_commit_html = ""
        #解析提交内容
        commit_count = len(js['commits'])
        if(1 == commit_count):
            commit_id = js['commits'][0]["id"][:7]
            commit_message = js['commits'][0]["message"].replace(" ","&nbsp")
            commit_date = js['commits'][0]["committer"]["date"].replace("T"," ").replace("Z"," ")
            commit_author = js['commits'][0]["author"]["name"]
            diff_commit_html = msg_format%(compare_url,commit_id,commit_message,commit_date,commit_author)
        else:
            startID = js['commits'][0]["id"][:7]
            endID = js['commits'][-1]["id"][:7]
            diff_commit = startID + "..." + endID
            diff_commit_html = '''<a href="%s"> %s </a>'''%(compare_url,diff_commit)
            #解析所有单个commit
            for commit_context in js['commits']:
                url = commit_context["url"]
                commit_id = url.split("/")[-1][:7]
                commit_date = commit_context["committer"]["date"].replace("T"," ").replace("Z"," ")
                commit_author = commit_context["author"]["name"]
                commit_message = commit_context["message"].replace(" ","&nbsp")
                #45af380 - 修改一键编译错误 (23 hours ago) <quqingyong>
                commit_html = msg_format%(url,commit_id,commit_message,commit_date,commit_author)
                diff_commit_html += "   <li> %s </li>"%(commit_html)        
           
        print diff_commit_html
        msg_body = """
        <p><b>分支</b>: %s</p>
        <p><b>差异</b>: %s</p>"""%(branch_html,diff_commit_html)

    print msg_body
    sendEmail(msg_head + msg_body + msg_tail)

#if __name__ == '__main__':
   #str = "<a href="www.google.com">abc</a>"
   # sendEmail(str)
