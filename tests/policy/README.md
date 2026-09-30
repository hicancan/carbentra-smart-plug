# 策略参考测试

仓库根目录运行：

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/policy -v
```

只需 Python 标准库。policy_reference.py 是纯内存、确定性守卫模拟器，不连接 GPIO、继电器、网络、证书或实际计量设备。

- authenticated / authorized 为测试输入桩，不能当成真实认证
- Profile 必须来自经验证配置；示例不具备签名、吊销或换负载检测
- 内存 ledger 不跨掉电持久化，也未限制容量；真实设备须实现持久化、寿命和防回滚策略
- accepted 仅代表策略接受，不能证明接点动作或电气安全
- 故障清除、启动默认、绑定、升级、租户隔离与硬件保护须另行实现验证
- 本地保护分支须在真实系统独立运行，不能依赖遥测或云命令到达

文档与模拟 JSON 在 docs/system/；参数只用于测试，不是额定值或安规承诺。
