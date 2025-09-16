"""
扑克牌包初始化文件
提供扑克牌相关类和功能的导入接口
"""

from .card import Card, Suit, Rank
from .deck import Deck, DeckManager, deck_manager

__all__ = [
    'Card', 'Suit', 'Rank',
    'Deck', 'DeckManager', 'deck_manager'
]

__version__ = '1.0.0'
__author__ = 'GameBoy Mini'
__description__ = '扑克牌模块 - 提供完整的扑克牌和牌组功能'