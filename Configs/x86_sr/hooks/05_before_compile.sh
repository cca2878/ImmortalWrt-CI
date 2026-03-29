#!/bin/bash
# 钩子：开始编译前 (Before compilation starts)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
#
# 此钩子在 .config 应用、make defconfig 完成后，make download 和编译前运行。
# 可用于最终调整配置、修改源码、添加版本标识等操作。
#
# 可用环境变量:
#   $PATH_WORKDIR   — 工作目录根路径
#   $PATH_CI        — CI 代码目录名
#   $PATH_SRC       — 源码目录名
#   $WRT_CONF       — 当前配置名
#   $WRT_TAG        — 构建 Tag
#   $WRT_VER        — 版本字符串
#   $F_DATE         — 构建日期

# 调用共享的设置脚本（如需要）
bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Settings.sh"
