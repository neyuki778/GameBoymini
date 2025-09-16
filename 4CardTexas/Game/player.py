"""
德州扑克玩家类
包含玩家信息、筹码管理、动作处理等
"""

from typing import List, Optional
import sys
import os

# 导入扑克牌模块
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Poker', 'Sheet'))
from card import Card

from game_types import PlayerAction, PlayerStatus, Position, GameConfig


class Player:
    """德州扑克玩家类"""
    
    def __init__(self, player_id: int, name: str, chips: int = GameConfig.STARTING_CHIPS):
        """
        初始化玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家姓名
            chips: 初始筹码
        """
        self.player_id = player_id
        self.name = name
        self.chips = chips
        self.hole_cards: List[Card] = []  # 底牌
        self.current_bet = 0              # 当前轮次已下注金额
        self.total_bet = 0                # 本局总下注金额
        self.status = PlayerStatus.ACTIVE
        self.position: Optional[Position] = None
        self.last_action: Optional[PlayerAction] = None
        self.is_human = True              # 是否为人类玩家
    
    def deal_hole_cards(self, cards: List[Card]):
        """发底牌"""
        self.hole_cards = cards.copy()
    
    def place_bet(self, amount: int) -> bool:
        """
        下注
        
        Args:
            amount: 下注金额
            
        Returns:
            bool: 是否成功下注
        """
        if amount > self.chips:
            return False
        
        self.chips -= amount
        self.current_bet += amount
        self.total_bet += amount
        
        if self.chips == 0:
            self.status = PlayerStatus.ALL_IN
        
        return True
    
    def call(self, call_amount: int) -> bool:
        """
        跟注
        
        Args:
            call_amount: 需要跟注的金额
            
        Returns:
            bool: 是否成功跟注
        """
        actual_call = min(call_amount, self.chips)
        if self.place_bet(actual_call):
            if actual_call < call_amount:
                self.last_action = PlayerAction.ALL_IN
            else:
                self.last_action = PlayerAction.CALL
            return True
        return False
    
    def raise_bet(self, raise_to: int) -> bool:
        """
        加注到指定金额
        
        Args:
            raise_to: 加注到的总金额
            
        Returns:
            bool: 是否成功加注
        """
        raise_amount = raise_to - self.current_bet
        if raise_amount <= 0:
            return False
        
        if self.place_bet(raise_amount):
            if self.chips == 0:
                self.last_action = PlayerAction.ALL_IN
            else:
                self.last_action = PlayerAction.RAISE
            return True
        return False
    
    def check(self) -> bool:
        """过牌"""
        if self.current_bet == 0 or self.status == PlayerStatus.ALL_IN:
            self.last_action = PlayerAction.CHECK
            return True
        return False
    
    def fold(self):
        """弃牌"""
        self.status = PlayerStatus.FOLDED
        self.last_action = PlayerAction.FOLD
    
    def all_in(self) -> int:
        """全押，返回全押金额"""
        all_in_amount = self.chips
        if all_in_amount > 0:
            self.place_bet(all_in_amount)
            self.last_action = PlayerAction.ALL_IN
        return all_in_amount
    
    def can_act(self) -> bool:
        """判断玩家是否可以行动"""
        return self.status == PlayerStatus.ACTIVE and self.chips > 0
    
    def reset_for_new_hand(self):
        """为新一手牌重置玩家状态"""
        self.hole_cards = []
        self.current_bet = 0
        self.total_bet = 0
        self.last_action = None
        if self.chips > 0:
            self.status = PlayerStatus.ACTIVE
        else:
            self.status = PlayerStatus.OUT
    
    def reset_for_new_betting_round(self):
        """为新一轮下注重置"""
        self.current_bet = 0  # 重置当前轮次下注
        self.last_action = None
    
    def get_available_actions(self, current_bet: int, min_raise: int) -> List[PlayerAction]:
        """
        获取玩家可用的动作
        
        Args:
            current_bet: 当前轮次最高下注
            min_raise: 最小加注额
            
        Returns:
            List[PlayerAction]: 可用动作列表
        """
        if not self.can_act():
            return []
        
        actions = []
        
        # 总是可以弃牌(除非已经全押)
        if self.status != PlayerStatus.ALL_IN:
            actions.append(PlayerAction.FOLD)
        
        call_amount = current_bet - self.current_bet
        
        # 如果不需要跟注，可以过牌
        if call_amount == 0:
            actions.append(PlayerAction.CHECK)
        # 如果需要跟注且有足够筹码
        elif call_amount <= self.chips:
            actions.append(PlayerAction.CALL)
        
        # 可以加注的条件
        min_raise_to = current_bet + min_raise
        if self.chips + self.current_bet >= min_raise_to:
            actions.append(PlayerAction.RAISE)
        
        # 总是可以全押(如果还有筹码)
        if self.chips > 0:
            actions.append(PlayerAction.ALL_IN)
        
        return actions
    
    def __str__(self) -> str:
        """返回玩家信息字符串"""
        status_str = ""
        if self.status == PlayerStatus.FOLDED:
            status_str = " (已弃牌)"
        elif self.status == PlayerStatus.ALL_IN:
            status_str = " (全押)"
        elif self.status == PlayerStatus.OUT:
            status_str = " (已淘汰)"
        
        return f"{self.name}(筹码:{self.chips}){status_str}"
    
    def get_hand_display(self, show_hole_cards: bool = False) -> str:
        """
        获取手牌显示
        
        Args:
            show_hole_cards: 是否显示底牌
            
        Returns:
            str: 手牌显示字符串
        """
        if not show_hole_cards or self.status == PlayerStatus.FOLDED:
            return "🂠🂠"  # 背面牌
        
        if len(self.hole_cards) == 2:
            return f"{self.hole_cards[0]} {self.hole_cards[1]}"
        else:
            return "无底牌"