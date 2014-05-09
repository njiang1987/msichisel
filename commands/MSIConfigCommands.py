#!/usr/bin/python

# Copyright (c) 2014, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import lldb
import os
import time
import fblldbbase as fb
from msilldbconfighelpers import getTQMSInformationDict
import objc

def lldbcommands():
    return [
        MSIConfigCommand()
    ]

class MSIConfigCommand(fb.FBCommand):
    def name(self):
        return 'config'

    def description(self):
        return 'Config MSTR Mobile Application with URL/TQMS id.'

    def options(self):
        return [
                fb.FBCommandArgument(short='-u', long='--url', arg='url', type='string', default='', help='Config mobile app with url'),
                fb.FBCommandArgument(short='-d', long='--id', arg='id', type='string', default='880507', help='TQMS ID')
        ]

    def getPureUrlLink(self, dirty_url):
        if dirty_url is None:
            return None

        results = dirty_url.split(' ')
        for str in results:
            if str != '':
                return str

#    def args(self):
#        return [ fb.FBCommandArgument(arg='url', type='string', help='The config url.', default='mstripad://?url=http%3A%2F%2F10.27.16.54%3A80%2FMicroStrategyMobile%2Fasp%2FTaskProc.aspx%3FtaskId%3DgetMobileConfiguration%26taskEnv%3Dxml%26taskContentType%3Dxmlanf%26configurationID%3D9883f5a5-23de-42bc-b9d3-6629cd275343&authMode=1')]

# expr [[[UIApplication sharedApplication] delegate] application:application openURL:url sourceApplication:sourceApplication annotation:annotation]
# application = [UIApplication sharedApplication]
# url = [above]
# sourceApplication = @"com.apple.mobilesafari"
# annotation = NSDictionary
# {
#     ReferrerURL = "http://10.197.34.70/";
# }
    def run(self, args, options):
        print '------ start config ------'

        if options.id == "" and options.url == "":
            print "error, -d or -u missing!"
            return

        # 1. Generate url and document path first
        if options.id is not None and options.id != "":
            tqms_dict = getTQMSInformationDict(options.id)

            for key in tqms_dict:
                if tqms_dict[key] is None or tqms_dict[key] == "":
                    print "Error when get %s for TQMS: %s" % (key, options.id)

            config_url = tqms_dict['url']
            document_path = tqms_dict['document']
            path_separator = "->"

        elif options.url is not None and options.url != "":
            config_url = options.url

        config_url = self.getPureUrlLink(config_url)
        print "config_url = %s" % config_url
        print "document_path = %s" % document_path

        # 2. Config the document path into FolderPathSearcher
        if document_path is not None:
            lldb.debugger.HandleCommand('expression [FolderPathSearcher getInstance]')
            if document_path is not None and document_path != "":
                expr = '[[FolderPathSearcher getInstance] setSearchPath:@"'+ document_path +'" Separator:@"'+ path_separator +'"]'
                lldb.debugger.HandleCommand('expression ' + expr)

        # 3. Apply url link
        if config_url is not None:
            url = fb.evaluateExpression('(NSURL*)[NSURL URLWithString:@"%s"]' % config_url)
            application = fb.evaluateExpression('(UIApplication*)[UIApplication sharedApplication]')
            delegate = fb.evaluateExpression('[(UIApplication*)%s delegate]' % application)
            lldb.debugger.HandleCommand('expr (void)[%s application:%s openURL:%s sourceApplication:nil annotation:nil]' % (delegate, application, url))
#            if document_path is not None and document_path != "":
#                expr = '[[FolderPathSearcher getInstance] startSearchWithPath:@"'+ document_path +'" Separator:@"'+ path_separator +'"]'
#                lldb.debugger.HandleCommand('expression ' + expr)
            print '------ end config ------'
        else:
            print 'Failed to generate the url link, please check your url or TQMS ID is correct!'

        # 4. Continue run our app
        # lldb.debugger.SetAsync(True)
        # lldb.debugger.GetSelectedTarget().GetProcess().Continue()

# the following code is used for testing
# config = MSIConfigCommand()
# config.run(['880507'], config.options())