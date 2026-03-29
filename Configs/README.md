# Configs 目录说明

此目录存放 `WRT-CONTAINER.yml` 工作流的结构化编译配置。每个子目录代表一个独立的编译配置（config），包含该配置的所有信息。

## 目录结构

```
Configs/
  <配置名>/
    build.env                    # 源码仓库与分支的默认值
    config.txt                   # 固件 .config 内容（可选，留空则回退到 Simple/Config/<配置名>.txt）
    feeds.txt                    # 自定义 feeds 源（可选）
    hooks/
      01_after_clone.sh          # 钩子：代码克隆后
      02_before_feeds_update.sh  # 钩子：添加 feeds 后、update 前
      03_after_feeds_update.sh   # 钩子：feeds update 后、install 前
      04_after_feeds_install.sh  # 钩子：feeds install 后
      05_before_compile.sh       # 钩子：开始编译前
```

## build.env 格式

```bash
WRT_REPO=immortalwrt/immortalwrt
WRT_BRANCH=openwrt-24.10
```

| 键           | 说明                                     |
|--------------|------------------------------------------|
| `WRT_REPO`   | GitHub 仓库，格式为 `owner/repo`         |
| `WRT_BRANCH` | 分支名                                   |

## 文件说明

| 文件                | 说明                                                                 |
|---------------------|----------------------------------------------------------------------|
| `build.env`         | 设置该配置的默认源码仓库和分支。若工作流启动时手动填写了相应参数，则优先使用手动填写的值（override）。 |
| `config.txt`        | 固件编译配置（即 `.config` 内容）。若此文件不存在，工作流会回退到 `Simple/Config/<配置名>.txt`。 |
| `feeds.txt`         | 追加到 `feeds.conf.default` 的自定义 feed 源。若不存在，回退到 `Simple/Feeds/<配置名>.txt`。 |
| `hooks/*.sh`        | 各生命周期钩子脚本。不存在则跳过。                                    |

## 钩子脚本说明

所有钩子脚本均可访问以下环境变量：

- `$PATH_WORKDIR` — 工作目录根路径
- `$PATH_CI` — CI 代码目录名（相对于 `$PATH_WORKDIR`）
- `$PATH_SRC` — 源码目录名（相对于 `$PATH_WORKDIR`）
- `$WRT_CONF` — 当前配置名
- `$WRT_REPO` — 实际使用的源码仓库
- `$WRT_BRANCH` — 实际使用的分支
- `$WRT_TAG` — 构建 Tag
- `$WRT_VER` — 版本字符串
- `$F_DATE` — 构建日期

各钩子的工作目录：

| 钩子                      | 工作目录                          |
|---------------------------|-----------------------------------|
| `01_after_clone.sh`       | `$PATH_WORKDIR/$PATH_SRC`         |
| `02_before_feeds_update.sh` | `$PATH_WORKDIR/$PATH_SRC`       |
| `03_after_feeds_update.sh` | `$PATH_WORKDIR/$PATH_SRC`        |
| `04_after_feeds_install.sh` | `$PATH_WORKDIR/$PATH_SRC/package/` |
| `05_before_compile.sh`    | `$PATH_WORKDIR/$PATH_SRC`         |

## 使用方式

### 仅填写配置名启动编译

在 `WRT-CONTAINER.yml` 的 `workflow_dispatch` 中，只需填写 `WRT_CONF`，其余参数留空，工作流将自动从 `Configs/<WRT_CONF>/build.env` 加载仓库和分支信息。

### 手动覆盖参数

在 `workflow_dispatch` 中填写 `WRT_REPO` 和/或 `WRT_BRANCH`，可覆盖 `build.env` 中的默认值，方便临时切换仓库或分支测试。

## 添加新配置

```bash
mkdir -p Configs/my_new_config/hooks

# 创建 build.env
cat > Configs/my_new_config/build.env <<EOF
WRT_REPO=immortalwrt/immortalwrt
WRT_BRANCH=openwrt-24.10
EOF

# 创建 feeds.txt（可选）
touch Configs/my_new_config/feeds.txt

# 创建 config.txt（可选，否则从 Simple/Config/my_new_config.txt 加载）
# cp Simple/Config/x86.txt Configs/my_new_config/config.txt

# 创建钩子脚本（可选）
cp Configs/x86/hooks/*.sh Configs/my_new_config/hooks/
```
