#!/bin/bash
#添加编译日期标识
export WRT_TAG=$WRT_CI'_'$WRT_DATE
echo $WRT_TAG
sed -i "s/(\(luciversion || ''\))/(\1) + (' \/ $WRT_TAG')/g" $(find ./feeds/luci/modules/luci-mod-status/ -type f -name "10_system.js")
