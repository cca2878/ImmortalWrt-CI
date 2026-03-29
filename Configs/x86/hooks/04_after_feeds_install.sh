#!/bin/bash
# 钩子：feeds install 后 (After feeds install)
# 工作目录: $PATH_WORKDIR/$PATH_SRC/package/
#
# 此钩子在 feeds install -a 完成后运行。
# 可用于添加/修改/删除自定义软件包，克隆额外的包仓库等操作。
#
# 可用环境变量:
#   $PATH_WORKDIR   — 工作目录根路径
#   $PATH_CI        — CI 代码目录名
#   $PATH_SRC       — 源码目录名
#   $WRT_CONF       — 当前配置名
#   $WRT_REPO       — 源码仓库

# 调用共享的包定制脚本（如需要）
bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Packages.sh"
bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Handles.sh"
