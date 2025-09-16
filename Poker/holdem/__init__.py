"""
德州扑克模块
包含德州扑克牌力评估和相关功能
"""

from .texas_holdem_evaluator import TexasHoldemEvaluator, HandType, HandEvaluation, texas_evaluator

__all__ = [
    'TexasHoldemEvaluator', 'HandType', 'HandEvaluation', 'texas_evaluator'
]

__version__ = '1.0.0'
__author__ = 'GameBoy Mini'
__description__ = '德州扑克模块 - 提供牌力评估和比较功能'