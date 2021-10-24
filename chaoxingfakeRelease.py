# coding=utf-8
"""
 create by monkey
 date 2021-9-11

"""
import re
import os
# import sys
import json
import time
import random
import getpass
import traceback

import requests
import warnings
from urllib import parse

warnings.filterwarnings("ignore")
headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; MI 9 Build/NMF26X) com.chaoxing.mobile/ChaoXingStudy_3_4.3.4_android_phone_494_27 (@Kalimdor)_2c658424a763452ebab8ee37ae1e35c3",
    "Accept-Language": "zh_CN", "Content-Type": "application/x-www-form-urlencoded",
    "Host": "passport2-api.chaoxing.com", "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
cookies = {'fid': '1','chaoxinguser':'1'}


class chaoxing:
    __form_to_txt_core__ = lambda a: [f"{key}={parse.quote(a[key])}" for key in a]
    __form_to_txt__ = lambda dic: '&'.join(chaoxing.__form_to_txt_core__(dic))

    def __init__(self):
        self.base_header = self.__init_headers__()
        self.base_cookie = self.__init_cookies__()
        # self.proxy = {
        #     "http": "http://192.168.43.222:8888",
        #     "https": "http://192.168.43.222:8888"
        # }
        self.userName = "user"
        self.course = {}
        self.activity = {}
        self.login_url = 'https://passport2-api.chaoxing.com/v11/loginregister?cx_xxt_passport=json'
        self.login_verify_url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
        self.course_list_url = "https://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&mcode="
        self.get_activity_url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
        self.location_sign_url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"

    def __init_cookies__(self):
        if not os.path.exists("./user_cookies.json"):
            global cookies
            self.update_cookies(dic=cookies)
            return cookies
        with open("./user_cookies.json", "rt") as fp:
            try:
                return json.load(fp)
            except:
                return cookies

    def __init_headers__(self):
        if not os.path.exists("./headers.json"):
            global headers
            self.update_headers(dic=headers)
            return headers
        with open("./headers.json", "rt") as fp:
            try:
                return json.load(fp)
            except Exception as e:
                print(e.args)
                return headers

    def fixed_time(self, t):
        s = t // 1000
        if s // 60 == 0:
            return f"{s}sec."
        m = s // 60
        s = s % 60
        if m // 60 == 0:
            return f"{m}min.{s}sec."
        h = m // 60
        m = m % 60
        return f"{h}hours.{m}min.{s}sec."

    def update_cookies(self, dic=None):
        if not dic:
            dic = self.base_cookie
        with open("./user_cookies.json", "wt") as fp:
            if len(dic.keys()) == 0:
                raise Exception("cookise update err  update content empty")
            else:
                fp.write(json.dumps(dic))

    def update_headers(self, dic=None):
        if not dic:
            dic = self.base_header
        with open("./headers.json", "wt") as fp:
            if len(dic.keys()) == 0:
                raise Exception("headers update err  update content empty ")
            else:
                fp.write(json.dumps(dic))

    def create_headers(self, lis):
        return {i: self.base_header[i].strip() if self.base_header.get(i) else "" for i in lis}

    def set_cookie(self, string):
        lis = re.findall(
            "Domain=[a-z A-Z 0-9 . _\- %]*[\s]*;[\s]*Expires=[a-z \s A-Z 0-9 . , :  _\- %]*;[\s]*Path=[a-z A-Z 0-9 _ \- \/]*[;,][a-z A-Z 0-9 . _\- % , \s = ]*;",
            string)
        example = ['Domain=',
                   'Expires=',
                   'Path=']
        for item in lis:
            temp = [i.strip() for i in re.findall("[a-z A-Z 0-9 _ \- %]*=", item)]

            if len(temp) == 0:
                continue
            field = set(temp).difference(example).pop()
            start = item.index(field) + len(field)
            end = item[start:].index(";")
            self.base_cookie[field[:-1]] = item[start:start + end]

        try:
            start = string.index("JSESSIONID=") + 10
            end = string[start:].index(";")
            self.base_cookie['JSESSIONID'] = item[start:start + end]
        except Exception as e:
            print(e.args)
            print("not have jsessionID")

    def login_verify(self):

        cookies = {
            '_d': self.base_cookie['_d'],
            '_uid': self.base_cookie['_uid'],
            'chaoxinguser': '1',
            'DSSTASH_LOG': self.base_cookie['DSSTASH_LOG'],
            'lv': '0',
            'uf': self.base_cookie['uf'],
            'UID': self.base_cookie['_uid'],
            'uname': "",
            'vc': self.base_cookie['vc'],
            'vc2': self.base_cookie['vc2'],
            'vc3': self.base_cookie['vc3'],
            'xxtenc': self.base_cookie['xxtenc']
        }
        header_fields = [
            "User-Agent",
            "Accept-Language",
            "Host",
            "Connection",
            "Accept-Encoding"
        ]
        headers = self.create_headers(header_fields)
        headers['Host'] = "sso.chaoxing.com"
        res = requests.get(self.login_verify_url, headers=headers, cookies=cookies)#, proxies=self.proxy, verify=False)
        if res.status_code == 200:
            data = json.loads(res.text)
            if data['result'] == 1:
                self.set_cookie(res.headers['Set-Cookie'])
                self.update_cookies()
                self.userName = data['msg']['name']
                return True
        return False

    def user_login(self, number, passwd):
        # uname=&code=&loginType=1&roleSelect=true
        form = {
            'uname': number,
            'code': passwd,
            'loginType': '1',
            'roleSelect': 'true'
        }
        header_fields = [
            "User-Agent",
            "Accept-Language",
            "Content-Type",
            "Host",
            "Connection",
            "Accept-Encoding"
        ]
        headers = self.create_headers(header_fields)
        url = f"{self.login_url}"
        res = requests.post(url, headers=headers, data=form)#, proxies=self.proxy, verify=False)
        if res.status_code == 200:
            message = json.loads(res.text)
            if message['mes'] == "验证通过":
                self.set_cookie(res.headers['Set-Cookie'])
                self.update_cookies()
                if self.login_verify():
                    print(f"[{self.userName}]用户登陆成功！！！！")
                    return True
                else:
                    print("登陆失败")
            else:
                print(f"{message['mes']}")
                self.set_cookie(res.headers['Set-Cookie'])
                self.update_cookies()
        else:
            print(f"response err code[{res.status_code}]")
        return False

    def get_course_list(self):
        cookies = {
            'xxtenc': self.base_cookie['xxtenc'],
            'vc3': self.base_cookie['vc3'],
            'vc2': self.base_cookie['vc2'],
            'vc': self.base_cookie['vc'],
            'uname': "",
            'UID': self.base_cookie['_uid'],
            'uf': self.base_cookie['uf'],
            'sso_puid': self.base_cookie['_uid'],
            'route': self.base_cookie['route'],
            'lv': '0',
            'fidsCount': '1',
            'DSSTASH_LOG': self.base_cookie['DSSTASH_LOG'],
            'chaoxinguser': '1',
            '_uid': self.base_cookie['_uid'],
            '_industry': 'null',
            '_d': self.base_cookie['_d']
        }
        fields = ['User-Agent', 'Accept-Language', 'Host', 'Accept-Encoding', 'Connection']
        headers = self.create_headers(fields)
        headers['Host'] = "mooc1-api.chaoxing.com"
        res = requests.get(self.course_list_url, cookies=cookies, headers=headers)#, proxies=self.proxy, verify=False)
        data = json.loads(res.text)
        if data['msg'] == "获取成功":
            for i in data['channelList']:
                try:
                    dic = {}
                    dic['courseId'] = str(i['content']['course']['data'][0]['id'])
                    dic['classId'] = str(i['key'])
                    dic['class'] = i['content']['name']
                    dic['teacher'] = i['content']['course']['data'][0]['teacherfactor']
                    self.course[i['content']['course']['data'][0]['name']] = dic
                except:
                    continue
            counter = 0
            print(f"{self.userName}的课程列表：")
            for key in self.course:
                print(
                    f"    {counter}.课程:{key} 班级:{self.course[key]['class']} teacher:{self.course[key]['teacher']} classId:{self.course[key]['classId']} courserId:{self.course[key]['courseId']}")
                counter += 1

    def get_course_activity(self, courseId, classId, uid, name):
        cookies = {'lv': '0',
                   'chaoxinguser': self.base_cookie['chaoxinguser'],
                   'uname': '',
                   '_uid': self.base_cookie['_uid'],
                   'UID': self.base_cookie['_uid'],
                   'vc': self.base_cookie['vc'],
                   'xxtenc': self.base_cookie['xxtenc'],
                   '_tid': self.base_cookie['_tid'],
                   'sso_puid': self.base_cookie['_uid'],
                   '_industry': self.base_cookie['_industry'],
                   'fidsCount': self.base_cookie['fidsCount'],
                   'uf': self.base_cookie['uf'],
                   '_d': self.base_cookie['_d'],
                   'vc2': self.base_cookie['vc2'],
                   'vc3': self.base_cookie['vc3'],
                   'DSSTASH_LOG': self.base_cookie['DSSTASH_LOG'],
                   'latotvp': '94',
                   'JSESSIONID': self.base_cookie['JSESSIONID']
                   }
        form = {
            'courseId': courseId,
            'classId': classId,
            'uid': uid,
            '_time': str(int(self.base_cookie['_d']) - int(random.random() * 5000))
        }
        header_field = ['User-Agent', 'Accept-Language', 'Host', 'Accept-Encoding', 'Connection']
        headers = self.create_headers(header_field)
        headers['Host'] = 'mobilelearn.chaoxing.com'
        url = f"{self.get_activity_url}?{chaoxing.__form_to_txt__(form)}"
        res = requests.get(url, headers=headers, cookies=cookies)#, proxies=self.proxy, verify=False)
        if res.status_code == 200:
            data = json.loads(res.text)
            if len(data['activeList']) > 0:
                self.activity[name] = data['activeList']
                ct = round(time.time() * 1000)
                print(f"课程[{name}]发布的活动现在时间{time.ctime(ct // 1000)} :")
                counter = 0
                self.activity[name] = []
                for i in data['activeList']:
                    t = str(time.ctime(i['startTime'] // 1000))
                    started = ct - i['startTime']
                    self.activity[name].append({
                        'name': i['nameOne'],
                        'startTime': t,
                        'ActivityId': str(i['id'])
                    })
                    print(
                        f"   {counter} 名称:{i['nameOne']}  开始时间:{t} 已进行:{self.fixed_time(started)}   ActivityId:{i['id']}")
                    counter += 1

    def location_sign(self, address, activeId, longitude, latitude, courseId, classId):
        form = {
            'address': address,
            'activeId': activeId,
            'uid': self.base_cookie['_uid'],
            'clientip': "",
            'latitude': latitude,
            'longitude': longitude,
            'fid': self.base_cookie['fid'],
            'appType': '15',
            'ifTiJiao': '1'
        }
        cookies = {'lv': '0',
                   'chaoxinguser': self.base_cookie['chaoxinguser'],
                   'uname': '',
                   '_uid': self.base_cookie['_uid'],
                   'UID': self.base_cookie['_uid'],
                   'vc': self.base_cookie['vc'],
                   'xxtenc': self.base_cookie['xxtenc'],
                   '_tid': self.base_cookie['_tid'],
                   'sso_puid': self.base_cookie['_uid'],
                   '_industry': self.base_cookie['_industry'],
                   'fidsCount': self.base_cookie['fidsCount'],
                   'uf': self.base_cookie['uf'],
                   '_d': self.base_cookie['_d'],
                   'vc2': self.base_cookie['vc2'],
                   'vc3': self.base_cookie['vc3'],
                   'DSSTASH_LOG': self.base_cookie['DSSTASH_LOG'],
                   'latotvp': '94',
                   'JSESSIONID': self.base_cookie['JSESSIONID']
                   }
        header_field = ['User-Agent', 'Accept-Encoding', 'Accept-Language']
        headers = self.create_headers(header_field)
        headers['Host'] = 'mobilelearn.chaoxing.com'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers[
            'Referer'] = f"https://mobilelearn.chaoxing.com/newsign/preSign?courseId={courseId}&classId={classId}&activePrimaryId={form['activeId']}&general=1&sys=1&ls=1&appType=15&uid={form['uid']}&isTeacherViewOpen=0"
        url = f"{self.location_sign_url}?{chaoxing.__form_to_txt__(form)}"
        res = requests.get(url, headers=headers, cookies=cookies)#, proxies=self.proxy, verify=False)
        if res.status_code == 200:
            if res.text == "success":
                print(f"{self.userName}签到成功!!! 签到地：{address}")
            else:
                print(f"{self.userName}您已经签过到了!!! msg:{res.text}")

    def location_sign_interface(self, userId, passwd):
        ctry = 0
        ttry = 10
        uid = userId
        psswd = passwd
        while not self.user_login(uid, psswd):
            if ctry > ttry:
                return
            print(f"密码错误 你还有{ttry - ctry}次尝试机会\n")
            ctry += 1
            uid = input("请输入账号:\n")
            psswd = getpass.getpass("请输入密码：\n")
            pass
        try:
            self.get_course_list()
            course = -1
            activity = -1
            key = list(self.course.keys())
            length = len(key)
            while course < 0 or course >= length:
                try:
                    course = int(input("请选择一门课程进行查看:\n"))
                except:
                    continue
            self.get_course_activity(courseId=self.course[key[course]]['courseId'],
                                     classId=self.course[key[course]]['classId'], uid=self.base_cookie['_uid'],
                                     name=key[course])
            length = len(self.activity[key[course]])
            while activity < 0 or activity >= length:
                try:
                    activity = int(input("请选择一个活动进行签到0:\n"))
                except:
                    continue

            self.location_sign("西安邮电大学(长安校区)东区逸夫教学楼", self.activity[key[course]][activity]['ActivityId'], '108.91258',
                               '34.161398', self.course[key[course]]['courseId'], self.course[key[course]]['classId'])
            os.system("pause")

        except Exception as e:
            traceback.print_exc()
            print(e.args)


cx = chaoxing()
userId = input("请输入账号:\n")
passwd = getpass.getpass("请输入密码：\n")
cx.location_sign_interface(userId, passwd)
