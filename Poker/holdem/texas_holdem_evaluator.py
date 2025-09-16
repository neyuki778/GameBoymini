"""
德州扑克牌力评估器
用于计算6张牌(2张底牌+4张公共牌)中最佳5张牌的牌力
"""

from enum import Enum
from typing import List, Tuple, Optional
from itertools import combinations
from collections import Counter

# 导入扑克牌模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Sheet'))
from card import Card, Suit, Rank


class HandType(Enum):
    """德扑牌型枚举，按强度从低到高排序"""
    HIGH_CARD = 1      # 高牌
    PAIR = 2           # 对子
    TWO_PAIR = 3       # 两对
    THREE_KIND = 4     # 三条
    STRAIGHT = 5       # 顺子
    FLUSH = 6          # 同花
    FULL_HOUSE = 7     # 葫芦(三带二)
    FOUR_KIND = 8      # 四条
    STRAIGHT_FLUSH = 9 # 同花顺
    ROYAL_FLUSH = 10   # 皇家同花顺

    def __str__(self):
        names = {
            1: "高牌", 2: "对子", 3: "两对", 4: "三条", 5: "顺子",
            6: "同花", 7: "葫芦", 8: "四条", 9: "同花顺", 10: "皇家同花顺"
        }
        return names[self.value]


class HandEvaluation:
    """牌力评估结果"""
    
    def __init__(self, hand_type: HandType, cards: List[Card], score: int, kickers: Optional[List[int]] = None):
        """
        初始化牌力评估结果
        
        Args:
            hand_type: 牌型
            cards: 组成这个牌型的5张牌
            score: 牌型基础分数
            kickers: 踢脚牌点数列表，用于同牌型比较
        """
        self.hand_type = hand_type
        self.cards = cards
        self.score = score
        self.kickers = kickers or []
    
    def __str__(self):
        return f"{self.hand_type}({[str(card) for card in self.cards]})"
    
    def __repr__(self):
        return f"HandEvaluation({self.hand_type}, score={self.score})"


class TexasHoldemEvaluator:
    """德州扑克牌力评估器"""
    
    def __init__(self):
        """初始化评估器"""
        pass
    
    def evaluate_6_cards(self, hole_cards: List[Card], community_cards: List[Card]) -> HandEvaluation:
        """
        评估6张牌(2张底牌+4张公共牌)的最佳牌力
        
        Args:
            hole_cards: 2张底牌
            community_cards: 4张公共牌
            
        Returns:
            HandEvaluation: 最佳牌力评估结果
            
        Raises:
            ValueError: 如果牌数不正确
        """
        if len(hole_cards) != 2:
            raise ValueError("底牌必须是2张")
        if len(community_cards) != 4:
            raise ValueError("公共牌必须是4张")
        
        all_cards = hole_cards + community_cards
        
        # 从6张牌中选择5张牌的所有组合
        best_evaluation: Optional[HandEvaluation] = None
        best_score = -1
        
        for five_cards in combinations(all_cards, 5):
            evaluation = self._evaluate_5_cards(list(five_cards))
            total_score = self._calculate_total_score(evaluation)
            
            if total_score > best_score:
                best_score = total_score
                best_evaluation = evaluation
        
        if best_evaluation is None:
            raise ValueError("无法评估牌力")
        
        return best_evaluation
    
    def _evaluate_5_cards(self, cards: List[Card]) -> HandEvaluation:
        """
        评估5张牌的牌力
        
        Args:
            cards: 5张牌
            
        Returns:
            HandEvaluation: 牌力评估结果
        """
        if len(cards) != 5:
            raise ValueError("必须是5张牌")
        
        # 按点数排序
        sorted_cards = sorted(cards, key=lambda x: x.rank.value, reverse=True)
        
        # 检查各种牌型
        if self._is_royal_flush(sorted_cards):
            return HandEvaluation(HandType.ROYAL_FLUSH, sorted_cards, 10000)
        
        straight_flush_result = self._check_straight_flush(sorted_cards)
        if straight_flush_result:
            return straight_flush_result
        
        four_kind_result = self._check_four_of_a_kind(sorted_cards)
        if four_kind_result:
            return four_kind_result
        
        full_house_result = self._check_full_house(sorted_cards)
        if full_house_result:
            return full_house_result
        
        flush_result = self._check_flush(sorted_cards)
        if flush_result:
            return flush_result
        
        straight_result = self._check_straight(sorted_cards)
        if straight_result:
            return straight_result
        
        three_kind_result = self._check_three_of_a_kind(sorted_cards)
        if three_kind_result:
            return three_kind_result
        
        two_pair_result = self._check_two_pair(sorted_cards)
        if two_pair_result:
            return two_pair_result
        
        pair_result = self._check_pair(sorted_cards)
        if pair_result:
            return pair_result
        
        # 高牌
        return self._check_high_card(sorted_cards)
    
    def _is_royal_flush(self, cards: List[Card]) -> bool:
        """检查是否为皇家同花顺"""
        if not self._is_flush(cards):
            return False
        
        ranks = [card.rank.value for card in cards]
        royal_ranks = [14, 13, 12, 11, 10]  # A, K, Q, J, 10
        return sorted(ranks, reverse=True) == royal_ranks
    
    def _check_straight_flush(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查同花顺"""
        if self._is_flush(cards) and self._is_straight_values([card.rank.value for card in cards]):
            high_card = max(cards, key=lambda x: x.rank.value)
            # 特殊处理A-2-3-4-5的情况
            ranks = [card.rank.value for card in cards]
            if sorted(ranks) == [2, 3, 4, 5, 14]:  # A-2-3-4-5
                score = 500 + 5  # 5为最高牌
            else:
                score = 500 + high_card.rank.value
            return HandEvaluation(HandType.STRAIGHT_FLUSH, cards, score, [high_card.rank.value])
        return None
    
    def _check_four_of_a_kind(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查四条"""
        rank_counts = Counter(card.rank.value for card in cards)
        for rank, count in rank_counts.items():
            if count == 4:
                kicker = [r for r in rank_counts.keys() if r != rank][0]
                score = 400 + rank
                return HandEvaluation(HandType.FOUR_KIND, cards, score, [rank, kicker])
        return None
    
    def _check_full_house(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查葫芦"""
        rank_counts = Counter(card.rank.value for card in cards)
        three_rank = None
        pair_rank = None
        
        for rank, count in rank_counts.items():
            if count == 3:
                three_rank = rank
            elif count == 2:
                pair_rank = rank
        
        if three_rank and pair_rank:
            score = 300 + three_rank
            return HandEvaluation(HandType.FULL_HOUSE, cards, score, [three_rank, pair_rank])
        return None
    
    def _check_flush(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查同花"""
        if self._is_flush(cards):
            kickers = sorted([card.rank.value for card in cards], reverse=True)
            score = 200 + kickers[0]
            return HandEvaluation(HandType.FLUSH, cards, score, kickers)
        return None
    
    def _check_straight(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查顺子"""
        ranks = [card.rank.value for card in cards]
        if self._is_straight_values(ranks):
            # 特殊处理A-2-3-4-5的情况
            if sorted(ranks) == [2, 3, 4, 5, 14]:
                score = 100 + 5  # 5为最高牌
                high_rank = 5
            else:
                high_rank = max(ranks)
                score = 100 + high_rank
            return HandEvaluation(HandType.STRAIGHT, cards, score, [high_rank])
        return None
    
    def _check_three_of_a_kind(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查三条"""
        rank_counts = Counter(card.rank.value for card in cards)
        for rank, count in rank_counts.items():
            if count == 3:
                kickers = sorted([r for r in rank_counts.keys() if r != rank], reverse=True)
                score = 90 + rank
                return HandEvaluation(HandType.THREE_KIND, cards, score, [rank] + kickers)
        return None
    
    def _check_two_pair(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查两对"""
        rank_counts = Counter(card.rank.value for card in cards)
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            score = 80 + pairs[0]
            return HandEvaluation(HandType.TWO_PAIR, cards, score, pairs + [kicker])
        return None
    
    def _check_pair(self, cards: List[Card]) -> Optional[HandEvaluation]:
        """检查对子"""
        rank_counts = Counter(card.rank.value for card in cards)
        for rank, count in rank_counts.items():
            if count == 2:
                kickers = sorted([r for r in rank_counts.keys() if r != rank], reverse=True)
                score = 70 + rank
                return HandEvaluation(HandType.PAIR, cards, score, [rank] + kickers)
        return None
    
    def _check_high_card(self, cards: List[Card]) -> HandEvaluation:
        """高牌"""
        kickers = sorted([card.rank.value for card in cards], reverse=True)
        score = 60 + kickers[0]
        return HandEvaluation(HandType.HIGH_CARD, cards, score, kickers)
    
    def _is_flush(self, cards: List[Card]) -> bool:
        """检查是否为同花"""
        suits = [card.suit for card in cards]
        return len(set(suits)) == 1
    
    def _is_straight_values(self, ranks: List[int]) -> bool:
        """检查数值是否构成顺子"""
        sorted_ranks = sorted(set(ranks))
        
        # 检查正常顺子
        if len(sorted_ranks) == 5:
            for i in range(1, len(sorted_ranks)):
                if sorted_ranks[i] != sorted_ranks[i-1] + 1:
                    break
            else:
                return True
        
        # 检查A-2-3-4-5的特殊情况
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False
    
    def _calculate_total_score(self, evaluation: HandEvaluation) -> int:
        """
        计算总分数，用于比较不同牌型
        
        Args:
            evaluation: 牌力评估结果
            
        Returns:
            int: 总分数
        """
        # 牌型基础分数(乘以大数确保牌型优先级)
        base_score = evaluation.hand_type.value * 1000000
        
        # 牌型内部分数
        type_score = evaluation.score * 1000
        
        # 添加踢脚牌分数(权重较小)
        kicker_score = 0
        for i, kicker in enumerate(evaluation.kickers):
            # 使用更小的权重，每个踢脚牌最多贡献15分
            kicker_score += kicker * (16 ** (len(evaluation.kickers) - i - 1))
        
        # 确保踢脚牌分数不会超过100000
        kicker_score = min(kicker_score, 99999)
        
        return base_score + type_score + kicker_score
    
    def compare_hands(self, eval1: HandEvaluation, eval2: HandEvaluation) -> int:
        """
        比较两手牌的大小
        
        Args:
            eval1: 第一手牌的评估结果
            eval2: 第二手牌的评估结果
            
        Returns:
            int: 1表示eval1更大，-1表示eval2更大，0表示平局
        """
        score1 = self._calculate_total_score(eval1)
        score2 = self._calculate_total_score(eval2)
        
        if score1 > score2:
            return 1
        elif score1 < score2:
            return -1
        else:
            return 0


# 创建全局评估器实例
texas_evaluator = TexasHoldemEvaluator()