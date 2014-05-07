#!/usr/bin/python

# Copyright (c) 2014, MicroStrategy, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import string
import json
import requests
import pickle
import os
import ConfigParser
import getpass
from requests_ntlm import HttpNtlmAuth

def getConfigFilePath():
    return '/tmp/MicroStrategy/TQMS.cfg'

def getCookiesFilePath():
    return '/tmp/MicroStrategy/TQMS.cookies'

def getAuthorizationCookies(username):
    print 'msilldbconfighelpers.py - getAuthorizationCookies'
    password = getpass.getpass('Password for ' + username + ': ')
    login_url = 'https://tech-websrvr.labs.microstrategy.com/Technology/TQMSWeb/login/login.aspx?ReturnUrl=%2fTechnology%2fTQMSWeb%2fviewissue%2fviewissuewindow.aspx%3fid%3d877255%26searchid%3d2746652&id=877255&searchid=2746652'
    response = requests.get(login_url, auth = HttpNtlmAuth(username, password))
    cookies = response.request._cookies
    return cookies

def recordCookies(cookies):
    print 'msilldbconfighelpers.py - recordCookies'
    cookies_path = getCookiesFilePath()
    with open(cookies_path, 'w') as cookie_file:
        pickle.dump(requests.utils.dict_from_cookiejar(cookies), cookie_file)

def getCookies():
    print 'msilldbconfighelpers.py - getCookies'
    # 1.first try to use local cookies
    cookies_path = getCookiesFilePath()
    if os.path.isfile(cookies_path):
        cookie_file = open(cookies_path)
        cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_file))
    else:
        cookies = None

    return cookies

def dumpCookies(cookies):
    try:
        print 'msilldbconfighelpers.py - dumpCookies'
        cookie_dict = requests.utils.dict_from_cookiejar(cookies)
        print cookie_dict
        str = ""
        for key in cookie_dict:
            str += key + '=' + cookie_dict[key] + '; '

        print str
        return str
    except Exception, e:
        print e
        return ""

def combinationRequestHeaders(cookies):
    print 'msilldbconfighelpers.py - combinationRequestHeaders'
    headers = { "Connection": "keep-alive",
                "Content-Length": 20,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": "https://tech-websrvr.labs.microstrategy.com",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
                "Content-Type": "application/json",
                "Referer": "https://tech-websrvr.labs.microstrategy.com/Technology/TQMSWeb/viewissue/viewissuewindow.aspx?id=882018",
                "Accept-Encoding": "gzip,deflate,sdch",
                "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
                "Cookie": cookies}
    return headers

# Find URL string
# 1. Order: comments->full description
# 2. Keywords: mstr://
# 3. We should distinguish iPad and iPhone device config url link
def generateConfigURLLink(comments, full_description):
    try:
        if comments is not None:
            start_index = string.find(comments, 'mstr://')

        if start_index == -1:
            start_index = string.find(full_description, 'mstr://')

        if start_index == -1:
            raise Exception('The full description formatting is wrong, please use "mstr://" as the prefix of mobile config link')
        else:
            substr = full_description[start_index:]

        results = substr.split('\r\n')
        if len(results) == 0:
            raise Exception("Failed to get the end index of config link!")
        else:
            return results[0]
    except Exception, e:
        print e
        return None

# Find Document Path
# 1. We will first try to find string like {% Document Path %}
# 2. We should suggest using '/' or '>' or '->' to split
def generateDocumentPath(comments, full_description):
    try:
        return 'MicroStrategy Tutorial->iPad->CTC->Single Feature->Document Viewer->02 Selector->2.1 Selector Title Bar->2.1.2 Title Bar Format->Font_ListBox'
    except Exception, e:
        print e
        return None

def getTQMSInformationDict(tqms):
    try:
        config_path = getConfigFilePath()
        if os.path.isfile(config_path) == False:
            print 'Please create an file named "config" under ' + config_path + ' ! Format with'
            print '[Login]'
            print 'domain = [the domain]'
            print 'username = [your username]'
            return
        cf = ConfigParser.ConfigParser()
        cf.read(config_path)
        domain = cf.get('Login', 'domain')
        username = cf.get('Login', 'username')

        if domain is None or username is None:
            print 'Please create an file named "config" under ' + config_path + '! Format with\n'
            print '[Login]'
            print 'domain = [the domain]'
            print 'username = [your username]'
            return

        print 'msilldbconfighelpers.py - getMobileConfigLinkForTQMS'
        username = domain + '\\' + username
        # print username
        service_url = 'https://tech-websrvr.labs.microstrategy.com/technology/tqmsservices/issues.asmx/GetAllComunicationsPerType'
        payload = {"IssueId": tqms}
        json_data = json.dumps(payload)

        # 1. Try to use local cookies
        cookies_read_from_file = True
        cookies = getCookies()

        if cookies is None:
            cookies = getAuthorizationCookies(username)
            if cookies is None:
                raise "Failed to get the authorization for username: %s" % username
            recordCookies(cookies)
            cookies_read_from_file = False

        cookies_str = dumpCookies(cookies)

        # 2. get details description response string for tqms
        headers = combinationRequestHeaders(cookies_str)
        response = requests.post(service_url, data=json_data, headers=headers)

        print response.status_code

        if response.status_code != 200 and cookies_read_from_file == True:
            print "Try to relogin with Username!"
            cookies = getAuthorizationCookies(username)
            if cookies is None:
                raise "Failed to get the authorization with Username: %s" % username
            recordCookies(cookies)
            cookies_str = dumpCookies(cookies)
            headers = combinationRequestHeaders(cookies_str)
            response = requests.post(service_url, data=json_data, headers=headers)
            if response.status_code != 200:
                raise "Failed to get the authorization with Username: %s" % username

        if response.status_code != 200:
            raise "Failed to get the authorization with Username!"
        else:
            # 2. parse json string
            issue_infos = json.loads(response.text)['d']
            full_description_u = issue_infos['Description']
            comments_u = issue_infos['Comments']
            full_description = full_description_u.encode("utf-8")
            comments = comments_u.encode("utf-8")
            if full_description is None or full_description == '':
                raise Exception("Failed to get the full description for TQMS: %s" % tqms)
            else:
                # print full_description
                config_url = generateConfigURLLink(comments, full_description)
                document_path = generateDocumentPath(comments, full_description)
                return {"url": config_url, "document": document_path}
                
    except Exception, e:
        print e

# print getTQMSInformationDict('854318')