# 原神抽卡模拟器 Genshin Impact Gacha Simulator

---

带有Qt GUI，目前只有简体中文。 UI currently only in Chinese-Simplified.

### 说明 Notes

- 根据抽卡统计逆向实现，尽量但并不完全与游戏机制一致 Not completely consistent with the game mechanism, but try to implement as close as possible to the statistics
- 因暂缺统计数据，捕获明光机制目前仅以简单方式实现（直接在歪的基础上增加5%的不歪概率），与游戏实际表现存在较大差异，之后可能会修改 Capturing Radiance currently is not accurate and only a simple implementation, given limited statistics


### 运行 Run

1. ```pip install -r requirements.txt```
2. ```python main.py```


### 使用项目 Included

[Apache Echarts](https://github.com/apache/echarts)

### 参考 Reference

[Genshin Impact Wiki](https://genshin-impact.fandom.com/wiki/Wish/Expanded_Wish_Probablities)