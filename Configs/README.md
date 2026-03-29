# Configs 目录说明

此目录存放 `WRT-CONTAINER.yml` 工作流的编译配置文件。每个配置对应一个独立的 YAML 文件，所有构建信息（仓库、分支、.config 内容、feeds、钩子命令）全部存储在单一文件内。

## 目录结构

```
Configs/
  <配置名>.yml    # 单一配置文件，存储所有构建信息
  wrt_cfg.py     # YAML 解析辅助脚本（工作流内部使用）
  README.md
```

示例文件 `x86_example.yml` 包含所有可用字段的说明，可直接复制作为新配置的起点。

## 配置文件格式

```yaml
# 源码仓库（必填）
repo: "immortalwrt/immortalwrt"

# 源码分支（必填）
branch: "openwrt-24.10"

# .config 内容（可选）
# 直接粘贴 .config 文件的内容，或只写需要覆盖的选项行
# 留空时自动回退到 Simple/Config/<配置名>.txt
config: |
  CONFIG_TARGET_x86=y
  CONFIG_TARGET_x86_64=y
  CONFIG_TARGET_x86_64_DEVICE_generic=y

# 追加到 feeds.conf.default 的自定义 Feed 源（可选）
# 留空时自动回退到 Simple/Feeds/<配置名>.txt
feeds: |
  src-git passwall2 https://github.com/xiaorouji/openwrt-passwall2

# 构建生命周期钩子（shell 命令文本，留空或省略则跳过）
hooks:
  after_clone: ""                    # 代码克隆后
  before_feeds_update: ""            # feeds update 前
  after_feeds_update: ""             # feeds update 后、install 前
  after_feeds_install: |             # feeds install 后
    git clone --depth 1 https://github.com/example/luci-app-foo
  before_compile: |                  # 开始编译前
    sed -i 's/DISTRIB_DESCRIPTION.*/DISTRIB_DESCRIPTION="MyBuild"/g' \
      package/base-files/files/etc/openwrt_release
```

## 字段说明

| 字段                        | 类型 | 说明                                                                                 |
|-----------------------------|------|--------------------------------------------------------------------------------------|
| `repo`                      | 必填 | 源码仓库，格式为 `owner/repo`                                                        |
| `branch`                    | 必填 | 源码分支                                                                             |
| `config`                    | 可选 | 直接内嵌的 `.config` 文本。留空则回退到 `Simple/Config/<配置名>.txt`                |
| `feeds`                     | 可选 | 追加到 `feeds.conf.default` 的 feed 源文本。留空则回退到 `Simple/Feeds/<配置名>.txt`|
| `hooks.after_clone`         | 可选 | 代码克隆后执行，工作目录: `$PATH_SRC`                                                |
| `hooks.before_feeds_update` | 可选 | `feeds update` 前执行，工作目录: `$PATH_SRC`                                         |
| `hooks.after_feeds_update`  | 可选 | `feeds update` 后、`install` 前，工作目录: `$PATH_SRC`                               |
| `hooks.after_feeds_install` | 可选 | `feeds install` 后执行，工作目录: `$PATH_SRC`                                        |
| `hooks.before_compile`      | 可选 | `defconfig` 后、编译前执行，工作目录: `$PATH_SRC`                                    |

钩子脚本中可使用的环境变量：`$PATH_WORKDIR`、`$PATH_CI`、`$PATH_SRC`、`$WRT_CONF`、`$WRT_REPO`、`$WRT_BRANCH`、`$WRT_TAG`、`$WRT_VER`、`$F_DATE`

## 使用方式

### 仅填写配置名启动编译

在 `WRT-CONTAINER.yml` 的 `workflow_dispatch` 中，`WRT_CONF` 填写配置文件名（不含 `.yml` 后缀），其余参数留空：

- `WRT_CONF` = `x86_example`
- `WRT_REPO` = （留空，从 yml 加载）
- `WRT_BRANCH` = （留空，从 yml 加载）

### 手动覆盖参数

在 `workflow_dispatch` 中填写 `WRT_REPO` 和/或 `WRT_BRANCH`，可覆盖配置文件中的值，方便临时切换仓库或分支测试。

### 在 workflow_call 中不使用配置文件（向后兼容）

`WRT_REPO` 和 `WRT_BRANCH` 直接通过 `with:` 传入，`Configs/<配置名>.yml` 可以不存在；钩子和 feeds 会被跳过，`.config` 从 `Simple/Config/<名称>.txt` 加载：

```yaml
build_x86:
  uses: ./.github/workflows/WRT-CONTAINER.yml
  with:
    WRT_REPO: 'immortalwrt/immortalwrt'
    WRT_BRANCH: 'openwrt-24.10'
    WRT_CONF: 'x86'
```

## 添加新配置

```bash
cp Configs/x86_example.yml Configs/my_config.yml
# 编辑 my_config.yml：修改 repo、branch，粘贴 .config 内容，填写 feeds 和钩子命令
```

然后在 `workflow_dispatch` 中将 `WRT_CONF` 填写为 `my_config` 即可。
