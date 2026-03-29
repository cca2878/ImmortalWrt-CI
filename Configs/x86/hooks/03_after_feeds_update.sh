#!/bin/bash
# 钩子：feeds update 后、feeds install 前 (After feeds update, before feeds install)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
#
# 此钩子在 feeds update -a 完成后、执行 feeds install 前运行。
# 可用于修改已下载的 feed 内容、替换 feed 中的包版本等操作。
#
# 可用环境变量:
#   $PATH_WORKDIR   — 工作目录根路径
#   $PATH_CI        — CI 代码目录名
#   $PATH_SRC       — 源码目录名
#   $WRT_CONF       — 当前配置名

# 示例：修改某个 feed 中包的版本
# sed -i 's/PKG_VERSION:=.*/PKG_VERSION:=1.2.3/' ./feeds/packages/net/my-package/Makefile
