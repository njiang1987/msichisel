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
import fblldbobjecthelpers as objectHelpers

import pdb

def lldbcommands():
  return [
    MsiOpenCommand()
  ]

class MsiOpenCommand(fb.FBCommand):
  def name(self):
    return 'msiopen'

  def description(self):
    return 'msi test command'

  def args(self):
    return [ fb.FBCommandArgument(arg='path', type='(string)', help='path of the file') ]
  
  def options(self):
    return [ fb.FBCommandArgument(short='-s', long='--sep', arg='separator', type='string', default='->', help='separator of folder path') ]

  def run(self, arguments, options):
    
    expr = '[[FolderPathSearcher getInstance] startSearchWithPath:@"'+ arguments[0] +'" Separator:@"'+ options.separator +'"]'
    
    print expr
    
    lldb.debugger.HandleCommand('expression ' + expr)


