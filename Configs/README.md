# Configs 目录说明

此目录存放 `WRT-CONTAINER.yml` 工作流的编译配置文件。每个配置对应一个独立的 `.sh` 文件，包含该配置的全部信息。

## 目录结构

```
Configs/
  <配置名>.sh    # 单一配置文件，包含仓库信息、feeds、钩子脚本等全部内容
  README.md
```

示例文件 `x86_example.sh` 包含所有可用字段的说明，可直接复制作为新配置的起点。

## 配置文件格式

每个配置文件是一个 Bash 脚本，定义以下内容：

| 变量/函数              | 类型     | 说明                                                                          |
|------------------------|----------|-------------------------------------------------------------------------------|
| `WRT_REPO`             | 必填变量 | 源码仓库，格式为 `owner/repo`                                                 |
| `WRT_BRANCH`           | 必填变量 | 源码分支                                                                      |
| `WRT_CONFIG_FILE`      | 可选变量 | `.config` 文件路径（相对于 CI 仓库根目录）。留空则回退到 `Simple/Config/<配置名>.txt` |
| `CUSTOM_FEEDS`         | 可选变量 | 追加到 `feeds.conf.default` 的自定义 feed 源。留空则回退到 `Simple/Feeds/<配置名>.txt` |
| `hook_after_clone()`   | 可选函数 | 代码克隆后执行                                                                |
| `hook_before_feeds_update()` | 可选函数 | 添加 feeds 后、`feeds update` 前执行                                   |
| `hook_after_feeds_update()`  | 可选函数 | `feeds update` 后、`feeds install` 前执行                              |
| `hook_after_feeds_install()` | 可选函数 | `feeds install` 后执行                                                 |
| `hook_before_compile()`      | 可选函数 | `defconfig` 后、编译前执行                                             |

## 使用方式

### 仅填写配置名启动编译

在 `WRT-CONTAINER.yml` 的 `workflow_dispatch` 中，`WRT_CONF` 填写配置文件名（不含 `.sh` 后缀），其余参数留空：

- `WRT_CONF` = `x86_example`
- `WRT_REPO` = （留空，从配置文件加载）
- `WRT_BRANCH` = （留空，从配置文件加载）

### 手动覆盖参数

在 `workflow_dispatch` 中填写 `WRT_REPO` 和/或 `WRT_BRANCH`，可覆盖配置文件中的值，方便临时切换仓库或分支测试。

### 在 workflow_call 中不使用配置文件

`WRT_REPO` 和 `WRT_BRANCH` 直接通过 `with:` 传入时，配置文件不是必须的（向后兼容现有调用）：

```yaml
build_x86:
  uses: ./.github/workflows/WRT-CONTAINER.yml
  with:
    WRT_REPO: 'immortalwrt/immortalwrt'
    WRT_BRANCH: 'openwrt-24.10'
    WRT_CONF: 'x86'
```

若 `Configs/x86.sh` 不存在，钩子和自定义 feeds 将被跳过，`.config` 从 `Simple/Config/x86.txt` 加载。

## 添加新配置

```bash
cp Configs/x86_example.sh Configs/my_new_config.sh
# 编辑 my_new_config.sh，修改 WRT_REPO、WRT_BRANCH、CUSTOM_FEEDS 及钩子函数
```

然后在 `workflow_dispatch` 中将 `WRT_CONF` 填写为 `my_new_config` 即可。
