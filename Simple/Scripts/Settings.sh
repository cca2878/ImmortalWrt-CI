#!/bin/bash
#添加固件标识
echo $WRT_TAG
wrt_tag=$(printf '%q' "$WRT_TAG")
echo $wrt_tag
sed -i "s/(\(luciversion || ''\))/(\1) + (' \/ $wrt_tag')/g" $(find ./feeds/luci/modules/luci-mod-status/ -type f -name "10_system.js")
