#!/bin/bash
# =============================================================================
# 配置名: x86_example
#
# 使用方式:
#   在 WRT-CONTAINER 的 workflow_dispatch 中，将 WRT_CONF 填写为 "x86_example"
#   即可自动加载此文件中的所有信息，无需手动填写仓库和分支。
#   如需临时切换仓库/分支，可在 workflow_dispatch 中手动填写以覆盖此处的默认值。
# =============================================================================

# === 源码信息（必填）===
WRT_REPO="immortalwrt/immortalwrt"
WRT_BRANCH="openwrt-24.10"

# === .config 文件路径（可选）===
# 相对于 CI 仓库根目录的路径。
# 留空时自动回退到 Simple/Config/<WRT_CONF>.txt（如果存在）。
# 示例: WRT_CONFIG_FILE="Simple/Config/x86.txt"
WRT_CONFIG_FILE=""

# === 自定义 Feeds（可选）===
# 此处内容将追加到 feeds.conf.default。
# 留空时自动回退到 Simple/Feeds/<WRT_CONF>.txt（如果存在）。
CUSTOM_FEEDS="
src-git passwall2 https://github.com/xiaorouji/openwrt-passwall2
src-git mosdns https://github.com/sbwml/luci-app-mosdns
"

# =============================================================================
# 生命周期钩子函数
#
# 所有钩子中可用的环境变量:
#   $PATH_WORKDIR  — 工作目录根路径
#   $PATH_CI       — CI 代码目录名（相对于 $PATH_WORKDIR）
#   $PATH_SRC      — 源码目录名（相对于 $PATH_WORKDIR）
#   $WRT_CONF      — 当前配置名
#   $WRT_REPO      — 实际使用的源码仓库
#   $WRT_BRANCH    — 实际使用的分支
#   $WRT_TAG       — 构建 Tag
#   $WRT_VER       — 版本字符串
#   $F_DATE        — 构建日期
# =============================================================================

# 钩子1：代码克隆后 (After code clone)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
hook_after_clone() {
    : # 在此添加自定义代码，例如打补丁、添加文件等
}

# 钩子2：添加 feeds 后、update 前 (After adding feeds, before feeds update)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
hook_before_feeds_update() {
    : # 在此添加自定义代码，例如修改 feeds.conf.default
}

# 钩子3：update 后、install 前 (After feeds update, before feeds install)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
hook_after_feeds_update() {
    : # 在此添加自定义代码，例如修改已下载的 feed 中的包版本
}

# 钩子4：install 后 (After feeds install)
# 工作目录: $PATH_WORKDIR/$PATH_SRC/package/
hook_after_feeds_install() {
    bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Packages.sh"
    bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Handles.sh"
}

# 钩子5：开始编译前 (Before compilation starts)
# 工作目录: $PATH_WORKDIR/$PATH_SRC
hook_before_compile() {
    bash "$PATH_WORKDIR/$PATH_CI/Simple/Scripts/Settings.sh"
}
