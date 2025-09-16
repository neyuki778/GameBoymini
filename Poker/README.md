# Poker 扑克模块

一个完整的Python扑克系统，包含基础扑克牌功能和德州扑克牌力评估。

## 项目结构

```
Poker/
├── README.md              # 项目说明文档
├── Sheet/                 # 基础扑克牌模块
│   ├── card.py           # 扑克牌类定义
│   ├── deck.py           # 牌组类和管理器
│   ├── README.md         # 模块详细说明
│   └── test/             # 测试文件夹
│       ├── test_poker.py     # 基础模块测试
│       └── example_usage.py  # 使用示例
├── holdem/               # 德州扑克模块
│   ├── texas_holdem_evaluator.py  # 牌力评估器
│   └── test/             # 测试文件夹
│       ├── test_texas_evaluator.py  # 德扑测试
│       ├── debug_evaluator.py      # 调试工具
│       └── debug_pairs.py          # 对子调试
└── PNG/                  # 扑克牌图片资源
    ├── Cards (large)/    # 大尺寸卡牌图片
    ├── Cards (medium)/   # 中尺寸卡牌图片
    └── Cards (small)/    # 小尺寸卡牌图片
```

## 功能模块

### 📇 Sheet - 基础扑克牌模块
- **Card类**: 单张扑克牌，支持4种花色和13种点数
- **Deck类**: 52张牌的牌组，包含洗牌算法
- **DeckManager**: 全局牌组管理器，供其他模块使用

### 🃏 Holdem - 德州扑克模块  
- **TexasHoldemEvaluator**: 6张牌(2底牌+4公共牌)牌力评估
- 支持10种牌型：高牌到皇家同花顺
- 精确的牌力比较和排名算法

### 🖼️ PNG - 扑克牌图片资源
包含完整的52张扑克牌PNG图片，提供三种尺寸规格。

## 快速开始

### 基础用法

```python
# 导入基础模块
from Sheet import deck_manager, Card, Suit, Rank

# 获取洗好的牌
cards = deck_manager.get_cards(5)
print([str(card) for card in cards])

# 创建特定的牌
ace_spades = Card(Suit.SPADES, Rank.ACE)
print(ace_spades)  # A♠
```

### 德州扑克牌力评估

```python
# 导入德扑模块
from holdem import texas_evaluator
from Sheet import Card, Suit, Rank

# 设置底牌和公共牌
hole_cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)]
community_cards = [
    Card(Suit.DIAMONDS, Rank.ACE),
    Card(Suit.CLUBS, Rank.KING), 
    Card(Suit.HEARTS, Rank.QUEEN),
    Card(Suit.SPADES, Rank.JACK)
]

# 评估牌力
result = texas_evaluator.evaluate_6_cards(hole_cards, community_cards)
print(f"最佳牌型: {result.hand_type}")
print(f"使用的牌: {[str(card) for card in result.cards]}")
```

## 运行测试

```bash
# 测试基础扑克牌模块
cd Sheet/test && python3 test_poker.py

# 测试德州扑克模块  
cd holdem/test && python3 test_texas_evaluator.py
```

## 主要特性

- ✅ **完整牌型**: 支持德扑全部10种牌型
- ✅ **Fisher-Yates洗牌**: 公平随机的洗牌算法
- ✅ **6张牌评估**: 从2底牌+4公共牌中选最佳5张
- ✅ **精确比较**: 支持同牌型间的踢脚牌比较
- ✅ **图片资源**: 提供完整的扑克牌PNG图片
- ✅ **测试覆盖**: 全面的单元测试和边界测试

## 技术实现

- **编程语言**: Python 3.7+
- **核心算法**: Fisher-Yates洗牌、组合数学牌力评估
- **设计模式**: 工厂模式、单例模式
- **类型安全**: 使用枚举和类型注解

---

*适用于卡牌游戏开发、算法学习和概率分析*