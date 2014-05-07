#!/bin/bash

# Copyright (c) 2014, MicroStrategy, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

echo "------ Start Config Chisel ------"

curPath=`pwd`
echo $curPath
lldbinitFile=".lldbinit"
cd ~
if [[ ! -f "$lldbinitFile" ]]; then
	touch "$lldbinitFile"
else
	rm "$lldbinitFile"
	touch "$lldbinitFile"
fi

#echo "# ~/.lldbinit" >> $lldbinitFile
echo "command script import "$curPath"/fblldb.py" >> $lldbinitFile

cd "$curPath"
echo "Please input the following information:"
echo -n "domain = "
read domain
echo -n "username = "
read username

configPath="/tmp/MicroStrategy"
configFile="/tmp/MicroStrategy/TQMS.cfg"

if [ ! -d "$configPath" ]; then
	mkdir "$configPath"
fi

if [[ ! -f "$configFile" ]]; then
	touch "$configFile"
else
	rm "$configFile"
	touch "$configFile"
fi

echo "[Login]" >> $configFile
echo "domain = "$domain >> $configFile
echo "username = "$username >> $configFile

cd packages/requests
sudo python setup.py install
cd ../requests-ntlm
sudo python setup.py install

echo "------ Config Chisel Finished -------"