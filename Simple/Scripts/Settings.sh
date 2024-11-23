#!/bin/bash
#添加固件标识
echo $WRT_TAG
sed -i "s/(\(luciversion || ''\))/(\1) + (' \/ $WRT_TAG')/g" $(find ./feeds/luci/modules/luci-mod-status/ -type f -name "10_system.js")
