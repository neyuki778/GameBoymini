"""
扑克牌模块
定义单张扑克牌的基本属性和操作
"""

from enum import Enum
from typing import Union


class Suit(Enum):
    """扑克牌花色枚举"""
    HEARTS = "hearts"      # 红桃
    DIAMONDS = "diamonds"  # 方块  
    CLUBS = "clubs"        # 梅花
    SPADES = "spades"      # 黑桃

    def __str__(self):
        suit_symbols = {
            "hearts": "♥",
            "diamonds": "♦", 
            "clubs": "♣",
            "spades": "♠"
        }
        return suit_symbols[self.value]


class Rank(Enum):
    """扑克牌点数枚举"""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self):
        face_cards = {
            11: "J",
            12: "Q", 
            13: "K",
            14: "A"
        }
        return face_cards.get(self.value, str(self.value))


class Card:
    """扑克牌类"""
    
    def __init__(self, suit: Suit, rank: Rank):
        """
        初始化扑克牌
        
        Args:
            suit: 花色
            rank: 点数
        """
        self.suit = suit
        self.rank = rank
    
    def __str__(self) -> str:
        """返回扑克牌的字符串表示"""
        return f"{self.rank}{self.suit}"
    
    def __repr__(self) -> str:
        """返回扑克牌的调试字符串表示"""
        return f"Card({self.suit.name}, {self.rank.name})"
    
    def __eq__(self, other) -> bool:
        """比较两张牌是否相等"""
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self) -> int:
        """让Card对象可以作为字典键或集合元素"""
        return hash((self.suit, self.rank))
    
    def __lt__(self, other) -> bool:
        """比较牌的大小，先比较点数，再比较花色"""
        if not isinstance(other, Card):
            return NotImplemented
        if self.rank.value != other.rank.value:
            return self.rank.value < other.rank.value
        # 花色顺序：梅花 < 方块 < 红桃 < 黑桃
        suit_order = {Suit.CLUBS: 1, Suit.DIAMONDS: 2, Suit.HEARTS: 3, Suit.SPADES: 4}
        return suit_order[self.suit] < suit_order[other.suit]
    
    def get_value(self) -> int:
        """获取牌的点数值"""
        return self.rank.value
    
    def is_red(self) -> bool:
        """判断是否为红色牌(红桃或方块)"""
        return self.suit in [Suit.HEARTS, Suit.DIAMONDS]
    
    def is_black(self) -> bool:
        """判断是否为黑色牌(梅花或黑桃)"""
        return self.suit in [Suit.CLUBS, Suit.SPADES]
    
    def is_face_card(self) -> bool:
        """判断是否为人头牌(J, Q, K)"""
        return self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]
    
    def is_ace(self) -> bool:
        """判断是否为A"""
        return self.rank == Rank.ACE