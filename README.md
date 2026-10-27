# TrMenu 本人头像直购

本仓维护 TrMenu 原生配置，不再构建独立购买插件。玩家左键点击头像后直接购买一个本人头像，价格为 100 米粒，无二次确认。正常聊天反馈仅为“购买成功”或“余额不足”。

完整最小菜单见 [examples/self-head.yml](examples/self-head.yml)。将文件放入 TrMenu 菜单目录，按所用 TrMenu 版本的菜单加载方式加载。需要已有经济服务及 TrMenu 的经济支持，并能解析 `%player_name%`。米粒是经济货币的显示名称。

余额条件通过后依次执行 `take-money: 100`、本人头像 `give-item`、成功提示；余额不足仅执行拒绝提示。点击音效保留。费用由 TrMenu 负责，不调用独立购买命令，也不添加钱包、退款、确认或恢复实现。

[合并与迁移说明](docs/migration.md)说明如何合入已有菜单、保留旧数据及处理旧命令。[旧入口清单](docs/legacy-entries.json)记录原插件声明，供后端受控兼容绑定使用。

运行静态验证（Python 3 与 PyYAML）：

```sh
python3 tools/verify_config.py
# 对授权的本地候选做只读同一性验证：
python3 tools/verify_config.py --source /path/to/candidate.yml
```

验证覆盖 YAML、H 动作与反馈、候选 SHA 与 H 同一性、旧入口清单及公开文件检查。它不代表真实交易、扣费回执或头像纹理验收通过。`take-money` 与发放不是事务；异常须结合经济流水和库存人工核对。头像按安装版的玩家名称解析路径生成，不承诺完整 profile 复制或换肤立即生效；背包满时须核验安装版 GiveItem 的剩余物品处理。

历史 Java 源码、测试和构建脚本可从 Git 历史追溯，当前版本不产出 JAR。不附加新的自研许可证。
