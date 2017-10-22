
# coding: utf-8

# In[ ]:

import socket, threading
import queue
import time
import re
import urllib.parse
import urllib.request
import requests
from bs4 import BeautifulSoup
from pyfcm import FCMNotification



class TCPServer(threading.Thread):
    def __init__(self, HOST, PORT):
        threading.Thread.__init__(self)
 
        self.HOST = HOST
        self.PORT = PORT
        
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.serverSocket.listen(5)
 
    def run(self):
        try:
            while True:
                print ('tcp server :: server wait...')
                connection, clientAddress = self.serverSocket.accept()
  
                print ("tcp server :: connect :", clientAddress)
    
                subThread = TCPServerThread(connection, clientAddress)
                subThread.start()
        except:
            print ("tcp server :: serverThread error")

class TCPServerThread(threading.Thread):
    def __init__(self,connection, clientAddress):
        threading.Thread.__init__(self)
 
        self.connection = connection
        self.clientAddress = clientAddress
 
    def run(self):
        try:
            data = self.connection.recv(1024).decode()
            if not data:
                print ('tcp server :: exit :',self.connection)
            
            
            userid = data.split()[0]
            password = data.split()[1]
            token = data.split()[2]
            url = "https://info.kw.ac.kr/webnote/login/login_proc.php"
            loginQuery =  {"member_no" : userid,"password" : password,"login_type":"2","redirect_url":"http%3A%2F%2Finfo.kw.ac.kr%2F","layout_opt":"N","gubun_code":"11","p_language":"KOREAN"}
            login_form = urllib.parse.urlencode(loginQuery)
            login_form = login_form.encode('utf-8')
            request = urllib.request.Request(url, login_form)
            request.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
            response = urllib.request.urlopen(request)
            cookie = response.getheader('Set-Cookie').split(", ")
           
            real_cookie = []
            for i in range(6):
                real_cookie.append(cookie[i].split("; ")[0])
            
            cookie_str = "; ".join(real_cookie)
            if bool(re.search("ccmedia",cookie_str)) == True :
                message = "login not success"
                
                self.connection.sendall(message.encode("utf-8"))
                self.connection.close()
                exit(0)
            else :
                message = "login success"
            
                self.connection.sendall(message.encode("utf-8"))
                self.connection.close()
                       
            push_service = FCMNotification(api_key="AIzaSyBZAmA3YdRFpjebLSCC7nzz5MN-DQaZgM8")
            registration_id = token
            count =[]
            count_1 = []
            count_2 = []
            count_3 = []
            count_4 = []
            count_5 = []
            count2 = 0
            while True:
                url2 = "http://info2.kw.ac.kr/servlet/controller.homepage.MainServlet?p_gate=univ&p_process=main&p_page=learning&p_kwLoginType=cookie&gubun_code=11"      
                request2 = urllib.request.Request(url2)
                request2.add_header('Cookie',cookie_str)
                request2.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                response2 = urllib.request.urlopen(request2)
                session = response2.getheader('Set-Cookie').split(", ")
                for i in range(3):
                    if i==0 or i==2:
                        real_cookie.append(session[i].split(";")[0])
            
                cookie_str1 = "; ".join(real_cookie)
                
                url3 ="http://info2.kw.ac.kr/servlet/controller.homepage.KwuMainServlet?p_process=openStu&p_grcode=N000003"
                request2 = urllib.request.Request(url3)
                request2.add_header('Cookie',cookie_str1)
                request2.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                response2 = urllib.request.urlopen(request2)
                
                soup = BeautifulSoup(response2.read(),"lxml")
                sub_table = []
                subseq_table = []
                for table_data in soup.find_all('td', {'class': 'list_txt'}):
                    if bool(re.search("_goEduPage",str(table_data))) == True :
                        subseq = str(table_data)[52:87]
                        subseq_table.append(subseq)
                    if bool(re.search("[학부]",str(table_data))) == True and bool(re.search("href",str(table_data))) == False:
                        sub=table_data.text.lstrip('<td class="list_txt">')
                        sub_table.append(sub)
                    
                
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                
                    url4 ="http://info2.kw.ac.kr/servlet/controller.learn.ContentsLessonServlet?p_process=listPage"
                    sQuery =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class}
                    login_form = urllib.parse.urlencode(sQuery)
                    login_form = login_form.encode('utf-8')
                    request3 = urllib.request.Request(url4,login_form)
                    request3.add_header('Cookie',cookie_str1)
                    request3.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                    response3 = urllib.request.urlopen(request3)
                   
                    soup = BeautifulSoup(response3.read(),"lxml")
                    info = []
                
                    count1 = 0
                    for table_data in soup.find_all('td', {'class': 't_l2'}):
                        if count1 % 2 == 0:
                            sum_sub = table_data.text
                        else:
                            sum_sub = sum_sub +"\n"+ table_data.text
                            info.append(sum_sub)
                        count1 += 1
                     
                
                    if count2 != 0:
                        if count1 > count[i]:
                            if count1 > count[i]:
                                message_title = "새 글이 등록되었습니다."
                                message_body = sub_table[i]+"\n"+"제목: "+info[0]
                                print(registration_id)
                                print(message_title)
                                print(message_body)
                                result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                                print(result)
                            count.pop(i)
                            count.insert(i,count1)
                            
                    else: 
                        count.append(count1)
                
            
                    
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                    j=0
                    info = []
                    count1=0
                    while True :
                        j += 1
                        p_pageno = j
                        url5 = "http://info2.kw.ac.kr/servlet/controller.learn.AssPdsStuServlet?p_process=listPage&p_process=&p_grcode=N000003"
                        s1Query =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class,"p_pageno":p_pageno}
                        login_form = urllib.parse.urlencode(s1Query)
                        login_form = login_form.encode('utf-8')
                        request4 = urllib.request.Request(url5,login_form)
                        request4.add_header('Cookie',cookie_str1)
                        request4.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                        response4 = urllib.request.urlopen(request4)
                        soup = BeautifulSoup(response4.read(),"lxml")
                       
                        if bool(re.search("등록된 내용이 없습니다",str(soup.find_all('td',{'class':'t_cr'})))) == True:
                            break;
                        for table_data in soup.find_all('samp', {'class': 'link_b2'}):
                            info.append(table_data.text.lstrip('\r\n').lstrip().rstrip("\r\n\t\t\t\t\t\n\n"))
                            count1 += 1 
                        
                
                    if count2 != 0:
                        if count1 > count_1[i]:
                            message_title = "새 글이 등록되었습니다."
                            message_body = sub_table[i]+"\n"+"제목: "+info[0]
                            print(registration_id)
                            print(message_title)
                            print(message_body)
                            result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                            print(result)
                        count_1.pop(i)
                        count_1.insert(i,count1)
                    
                    else: 
                        count_1.append(count1)
                
                    
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                    j=0
                    info = []
                    count1=0
                    while True :
                        j += 1
                        p_pageno = j
                        url6 = "http://info2.kw.ac.kr/servlet/controller.learn.NoticeStuServlet?p_process=listPage&p_process=&p_grcode=N000003"
                        s2Query =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class,"p_pageno":p_pageno}
                        login_form = urllib.parse.urlencode(s2Query)
                        login_form = login_form.encode('utf-8')
                        request5 = urllib.request.Request(url6,login_form)
                        request5.add_header('Cookie',cookie_str1)
                        request5.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                        response5 = urllib.request.urlopen(request5)
                        soup = BeautifulSoup(response5.read(),"lxml")
                       
                        if len(soup.find_all('td', {'class': 'tl_c'})) == 0 :
                            break;
                        for table_data in soup.find_all('samp', {'class': 'link_b2'}):
                            info.append(table_data.text.lstrip('\r\n').lstrip().rstrip("\r\n\t\t\t\t\t\n\n"))
                            count1 += 1 
                        
                
                    if count2 != 0:
                        if count1 > count_2[i]:
                            message_title = "새 글이 등록되었습니다."
                            message_body = sub_table[i]+"\n"+"제목: "+info[0]
                            print(registration_id)
                            print(message_title)
                            print(message_body)
                            result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                            print(result)
                        count_2.pop(i)
                        count_2.insert(i,count1)
                    
                    else: 
                        count_2.append(count1)
                        
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                
                    url7 ="http://info2.kw.ac.kr/servlet/controller.learn.ReportStuServlet?p_process=listPage&p_process=&p_grcode=N000003"
                    s3Query =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class}
                    login_form = urllib.parse.urlencode(s3Query)
                    login_form = login_form.encode('utf-8')
                    request5 = urllib.request.Request(url7,login_form)
                    request5.add_header('Cookie',cookie_str1)
                    request5.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                    response5 = urllib.request.urlopen(request5)
  
                    soup = BeautifulSoup(response5.read(),"lxml")
                    info = []
                
                    count1 = 0
                    for table_data in soup.find_all('samp', {'class': 'link_b2'}):
                        info.append(table_data.text)
                        count1 += 1
            
                
                    if count2 != 0:
                        if count1 > count[i]:
                            message_title = "새 글이 등록되었습니다."
                            message_body = sub_table[i]+"\n"+"제목: "+info[0]
                            print(registration_id)
                            print(message_title)
                            print(message_body)
                            result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                            print(result)
                        count_3.pop(i)
                        count_3.insert(i,count1)
                    
                    else: 
                        count_3.append(count1)
               
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                
                    url8 ="http://info2.kw.ac.kr/servlet/controller.learn.ExamAnyPaperStuServlet?p_process=listPage"
                    s4Query =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class}
                    login_form = urllib.parse.urlencode(s4Query)
                    login_form = login_form.encode('utf-8')
                    request6 = urllib.request.Request(url8,login_form)
                    request6.add_header('Cookie',cookie_str1)
                    request6.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                    response6 = urllib.request.urlopen(request6)
                  
                    soup = BeautifulSoup(response6.read(),"lxml")
                    info = []
                
                    count1 = 0
                    for table_data in soup.find_all('td', {'class': 't_l2'}):
                        info.append(table_data.text)
                        count1 += 1
                    
                
                    if count2 != 0:
                        if count1 > count[i]:
                            message_title = "새 글이 등록되었습니다."
                            message_body = sub_table[i]+"\n"+"제목: "+info[0]
                            print(registration_id)
                            print(message_title)
                            print(message_body)
                            result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                            print(result)
                        count_4.pop(i)
                        count_4.insert(i,count1)
                    
                    else: 
                        count_4.append(count1)
                    
                for i in range(len(subseq_table)):
                    _subj = subseq_table[i].split(",")[0]
                    _year = subseq_table[i].split(",")[1]
                    _subjseq = subseq_table[i].split(",")[2]
                    _class = subseq_table[i].split(",")[3]
                
                    p_subj = _subj.lstrip("'").rstrip("'")
                    p_year = _year.lstrip("'").rstrip("'")
                    p_subjseq = _subjseq.lstrip("'").rstrip("'")
                    p_class = _class.lstrip("'").rstrip("'")
                    j=0
                    info = []
                    count1=0
                    while True :
                        j += 1
                        p_pageno = j
                        url9 = "http://info2.kw.ac.kr/servlet/controller.learn.PdsStuServlet?p_process=listPage&p_process=&p_grcode=N000003"
                        s5Query =  {"p_subj":p_subj, "p_year":p_year, "p_subjseq":p_subjseq, "p_class": p_class,"p_pageno":p_pageno}
                        login_form = urllib.parse.urlencode(s5Query)
                        login_form = login_form.encode('utf-8')
                        request7 = urllib.request.Request(url9,login_form)
                        request7.add_header('Cookie',cookie_str1)
                        request7.add_header('User-Agent', "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)")
                        response7 = urllib.request.urlopen(request7)
                        soup = BeautifulSoup(response7.read(),"lxml")
                       
                        if bool(re.search("등록된 내용이 없습니다",str(soup.find_all('td',{'class':'tl_c'})))) == True:
                            break;
                        for table_data in soup.find_all('samp', {'class': 'link_b2'}):
                            info.append(table_data.text.lstrip('\r\n').lstrip().rstrip("\r\n\t\t\t\t\t\n\n"))
                            count1 += 1
                        
                      
                        
                
                    if count2 != 0:
                        
                        if count1 > count_5[i]:
                            message_title = "새 글이 등록되었습니다."
                            message_body = sub_table[i]+"\n"+"제목: "+info[0]
                            print(registration_id)
                            print(message_title)
                            print(message_body)
                            result = push_service.notify_single_device(registration_id=registration_id,data_message={'click_action': 'OPEN_ACTIVITY_1content_a','vailable':'true',"body" : message_body})
                            print(result)
                        count_5.pop(i)
                        count_5.insert(i,count1)
                    
                    else: 
                        count_5.append(count1)
                   
                time.sleep(20)
                count2 = 1
        except:
            self.connection.close()
            exit(0)
            

        
        
andRaspTCP = TCPServer("",7424)
andRaspTCP.start()
 



