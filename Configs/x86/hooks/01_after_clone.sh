#!/bin/bash
# 钩子：代码克隆后 (After source code clone)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
#
# 此钩子在源码克隆完成后、开始配置 feeds 前执行。
# 可用于修改源码、打补丁、添加文件等操作。
#
# 可用环境变量:
#   $PATH_WORKDIR   — 工作目录根路径
#   $PATH_CI        — CI 代码目录名
#   $PATH_SRC       — 源码目录名
#   $WRT_CONF       — 当前配置名
#   $WRT_REPO       — 源码仓库
#   $WRT_BRANCH     — 源码分支
#   $WRT_HASH       — 源码 commit hash

# 示例：打一个补丁
# patch -p1 < "$PATH_WORKDIR/$PATH_CI/Configs/$WRT_CONF/patches/example.patch"
