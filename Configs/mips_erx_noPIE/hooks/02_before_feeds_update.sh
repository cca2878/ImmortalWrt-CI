#!/bin/bash
# 钩子：添加 feeds 后、feeds update 前 (After adding feeds, before feeds update)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
#
# 此钩子在 feeds.txt 已追加到 feeds.conf.default 后、执行 feeds update 前运行。
# 可用于修改 feeds.conf.default、添加/删除 feed 源等操作。
#
# 可用环境变量:
#   $PATH_WORKDIR   — 工作目录根路径
#   $PATH_CI        — CI 代码目录名
#   $PATH_SRC       — 源码目录名
#   $WRT_CONF       — 当前配置名

# 示例：临时添加一个额外的 feed 源
# echo "src-git my_feed https://github.com/example/my-feed.git" >> feeds.conf.default
