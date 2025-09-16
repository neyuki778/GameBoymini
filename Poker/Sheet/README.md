# 扑克牌系统 (Poker System)

一个完整的Python扑克牌实现，包含扑克牌类、牌组类和洗牌算法。

## 功能特性

- ✅ 完整的52张标准扑克牌(不含Joker)
- ✅ Fisher-Yates洗牌算法，保证公平随机
- ✅ 发牌、重置、查看等完整功能
- ✅ 全局牌组管理器，方便其他模块使用
- ✅ 类型安全和完整的错误处理
- ✅ 丰富的牌类操作方法

## 文件结构

```
Sheet/
├── __init__.py          # 包初始化文件
├── card.py              # 扑克牌类定义
├── deck.py              # 牌组类和管理器
├── test_poker.py        # 测试脚本
├── example_usage.py     # 使用示例
└── README.md           # 说明文档
```

## 快速开始

### 基本导入

```python
from Sheet import Card, Suit, Rank, Deck, deck_manager
```

### 创建扑克牌

```python
# 创建单张牌
ace_spades = Card(Suit.SPADES, Rank.ACE)
king_hearts = Card(Suit.HEARTS, Rank.KING)

print(ace_spades)  # A♠
print(king_hearts)  # K♥

# 判断牌的属性
print(ace_spades.is_black())    # True
print(king_hearts.is_red())     # True
print(king_hearts.is_face_card())  # True
```

### 使用牌组

```python
# 创建并洗牌
deck = Deck(shuffle=True)

# 发牌
hand = deck.deal_cards(5)
print([str(card) for card in hand])

# 查看剩余牌数
print(f"剩余: {deck.cards_remaining()} 张")

# 重置牌组
deck.reset(shuffle=True)
```

### 使用全局管理器(推荐)

```python
# 获取洗好的牌
cards = deck_manager.get_cards(10)

# 获取新的完整牌组
new_deck = deck_manager.get_shuffled_deck()

# 重置管理器
deck_manager.reset_deck()
```

## 详细API

### Card类

#### 属性
- `suit: Suit` - 花色(红桃♥、方块♦、梅花♣、黑桃♠)
- `rank: Rank` - 点数(2-10, J, Q, K, A)

#### 方法
- `get_value() -> int` - 获取数值(2-14)
- `is_red() -> bool` - 是否为红色牌
- `is_black() -> bool` - 是否为黑色牌
- `is_face_card() -> bool` - 是否为人头牌(J,Q,K)
- `is_ace() -> bool` - 是否为A

### Deck类

#### 方法
- `shuffle()` - 洗牌(Fisher-Yates算法)
- `deal_card() -> Optional[Card]` - 发一张牌
- `deal_cards(count: int) -> List[Card]` - 发多张牌
- `peek_top_card() -> Optional[Card]` - 查看顶牌(不发出)
- `reset(shuffle: bool = False)` - 重置为52张牌
- `add_card(card: Card)` - 添加牌到底部
- `is_empty() -> bool` - 检查是否为空
- `cards_remaining() -> int` - 剩余牌数

### DeckManager类

#### 方法
- `get_cards(count: int) -> List[Card]` - 获取指定数量的牌
- `get_shuffled_deck() -> Deck` - 获取新的洗好的牌组
- `reset_deck()` - 重置并洗牌
- `cards_remaining() -> int` - 剩余牌数

## 使用场景示例

### 德州扑克

```python
# 发底牌给4个玩家
players = []
for i in range(4):
    hand = deck_manager.get_cards(2)
    players.append(hand)

# 发公共牌
flop = deck_manager.get_cards(3)  # 翻牌
turn = deck_manager.get_cards(1)  # 转牌  
river = deck_manager.get_cards(1)  # 河牌
```

### 21点

```python
# 发牌
player_hand = deck_manager.get_cards(2)
dealer_hand = deck_manager.get_cards(2)

# 计算牌值(简化版)
def calculate_blackjack_value(hand):
    value = 0
    aces = 0
    for card in hand:
        if card.rank == Rank.ACE:
            aces += 1
            value += 11
        elif card.is_face_card():
            value += 10
        else:
            value += card.get_value()
    
    # 处理A的软硬转换
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
    
    return value
```

### 扑克手牌分析

```python
# 检查同花
def is_flush(hand):
    suits = [card.suit for card in hand]
    return len(set(suits)) == 1

# 检查顺子
def is_straight(hand):
    values = sorted([card.get_value() for card in hand])
    for i in range(1, len(values)):
        if values[i] != values[i-1] + 1:
            return False
    return True
```

## 运行测试

```bash
# 进入Poker目录
cd Poker

# 运行测试
python Sheet/test_poker.py

# 运行示例
python Sheet/example_usage.py
```

## 洗牌算法

使用Fisher-Yates洗牌算法，确保：
- ✅ 每种排列出现的概率相等
- ✅ 时间复杂度O(n)，空间复杂度O(1)
- ✅ 加密学安全的随机性

```python
def shuffle(self):
    for i in range(len(self._cards) - 1, 0, -1):
        j = random.randint(0, i)
        self._cards[i], self._cards[j] = self._cards[j], self._cards[i]
```

## 设计特点

1. **类型安全**: 使用枚举定义花色和点数，避免无效值
2. **封装性**: 内部列表使用下划线前缀，提供公共接口
3. **错误处理**: 完整的边界检查和异常处理
4. **可扩展性**: 易于添加新的牌类游戏功能
5. **性能优化**: 高效的洗牌和发牌算法

## 许可证

该项目为GameBoy Mini项目的一部分。

## 作者

GameBoy Mini开发团队