"""
扑克牌组模块
实现一副完整的扑克牌组，包含洗牌、发牌等功能
"""

import random
from typing import List, Optional
from card import Card, Suit, Rank


class Deck:
    """扑克牌组类"""
    
    def __init__(self, shuffle: bool = False):
        """
        初始化牌组
        
        Args:
            shuffle: 是否在初始化时洗牌
        """
        self._cards: List[Card] = []
        self._create_deck()
        if shuffle:
            self.shuffle()
    
    def _create_deck(self):
        """创建一副完整的52张牌(不含joker)"""
        self._cards = []
        for suit in Suit:
            for rank in Rank:
                self._cards.append(Card(suit, rank))
    
    def shuffle(self):
        """
        使用Fisher-Yates洗牌算法洗牌
        这是一个高效且公平的洗牌算法
        """
        for i in range(len(self._cards) - 1, 0, -1):
            j = random.randint(0, i)
            self._cards[i], self._cards[j] = self._cards[j], self._cards[i]
    
    def deal_card(self) -> Optional[Card]:
        """
        发一张牌
        
        Returns:
            Card: 发出的牌，如果牌组为空则返回None
        """
        if self.is_empty():
            return None
        return self._cards.pop()
    
    def deal_cards(self, count: int) -> List[Card]:
        """
        发多张牌
        
        Args:
            count: 要发的牌数
            
        Returns:
            List[Card]: 发出的牌列表
            
        Raises:
            ValueError: 如果要发的牌数超过剩余牌数
        """
        if count > len(self._cards):
            raise ValueError(f"要发的牌数({count})超过剩余牌数({len(self._cards)})")
        
        dealt_cards = []
        for _ in range(count):
            card = self.deal_card()
            if card is not None:
                dealt_cards.append(card)
        
        return dealt_cards
    
    def peek_top_card(self) -> Optional[Card]:
        """
        查看顶部的牌但不发出
        
        Returns:
            Card: 顶部的牌，如果牌组为空则返回None
        """
        if self.is_empty():
            return None
        return self._cards[-1]
    
    def reset(self, shuffle: bool = False):
        """
        重置牌组，恢复到完整的52张牌
        
        Args:
            shuffle: 是否在重置后洗牌
        """
        self._create_deck()
        if shuffle:
            self.shuffle()
    
    def add_card(self, card: Card):
        """
        将一张牌加入牌组底部
        
        Args:
            card: 要加入的牌
        """
        self._cards.insert(0, card)
    
    def add_cards(self, cards: List[Card]):
        """
        将多张牌加入牌组底部
        
        Args:
            cards: 要加入的牌列表
        """
        for card in cards:
            self.add_card(card)
    
    def is_empty(self) -> bool:
        """检查牌组是否为空"""
        return len(self._cards) == 0
    
    def cards_remaining(self) -> int:
        """获取剩余牌数"""
        return len(self._cards)
    
    def get_cards(self) -> List[Card]:
        """
        获取当前所有牌的副本(用于调试或显示)
        
        Returns:
            List[Card]: 牌组中所有牌的副本
        """
        return self._cards.copy()
    
    def __len__(self) -> int:
        """返回牌组中的牌数"""
        return len(self._cards)
    
    def __str__(self) -> str:
        """返回牌组的字符串表示"""
        if self.is_empty():
            return "空牌组"
        return f"牌组({len(self._cards)}张牌)"
    
    def __repr__(self) -> str:
        """返回牌组的调试字符串表示"""
        return f"Deck({len(self._cards)} cards)"


class DeckManager:
    """牌组管理器，提供给其他模块使用的接口"""
    
    def __init__(self):
        """初始化牌组管理器"""
        self._deck = Deck(shuffle=True)
    
    def get_shuffled_deck(self) -> Deck:
        """
        获取一副洗好的新牌
        
        Returns:
            Deck: 洗好的牌组
        """
        new_deck = Deck(shuffle=True)
        return new_deck
    
    def get_cards(self, count: int) -> List[Card]:
        """
        从当前牌组获取指定数量的牌
        
        Args:
            count: 需要的牌数
            
        Returns:
            List[Card]: 发出的牌列表
            
        Raises:
            ValueError: 如果牌数不足，会自动重新洗牌后再发牌
        """
        try:
            return self._deck.deal_cards(count)
        except ValueError:
            # 牌数不足，重新洗牌
            self._deck.reset(shuffle=True)
            return self._deck.deal_cards(count)
    
    def reset_deck(self):
        """重置并洗牌"""
        self._deck.reset(shuffle=True)
    
    def cards_remaining(self) -> int:
        """获取当前牌组剩余牌数"""
        return self._deck.cards_remaining()


# 全局牌组管理器实例，供其他模块使用
deck_manager = DeckManager()