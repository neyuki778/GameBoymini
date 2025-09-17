"""
德州扑克主游戏类
处理游戏逻辑、下注轮次、牌力比较等核心功能
"""

from typing import List, Optional, Tuple, Dict
import sys
import os

# 导入扑克牌模块
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Poker', 'Sheet'))
from card import Card
from deck import deck_manager

# 导入德扑评估器
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Poker', 'holdem'))
from texas_holdem_evaluator import texas_evaluator

from game_types import GamePhase, PlayerAction, PlayerStatus, Position, GameConfig
from player import Player


class TexasHoldemGame:
    """2+4德州扑克游戏主类"""
    
    def __init__(self, num_players: int = GameConfig.DEFAULT_PLAYERS, human_players: Optional[List[int]] = None):
        """
        初始化游戏
        
        Args:
            num_players: 玩家数量
            human_players: 人类玩家的ID列表，如[0, 1]表示前两个玩家是人类
        """
        if not (GameConfig.MIN_PLAYERS <= num_players <= GameConfig.MAX_PLAYERS):
            raise ValueError(f"玩家数量必须在{GameConfig.MIN_PLAYERS}-{GameConfig.MAX_PLAYERS}之间")
        
        self.num_players = num_players
        self.human_players = human_players or [0]  # 默认第一个玩家是人类
        self.players: List[Player] = []
        self.community_cards: List[Card] = []
        self.pot = 0                     # 底池
        self.current_bet = 0             # 当前轮次最高下注
        self.min_raise = GameConfig.MIN_RAISE
        self.phase = GamePhase.WAITING
        self.dealer_position = 0         # 庄家位置
        self.current_player = 0          # 当前行动玩家
        self.betting_round_complete = False
        self.hand_number = 0             # 手牌局数
        
        # 初始化玩家
        self._initialize_players()
    
    def _initialize_players(self):
        """初始化玩家"""
        for i in range(self.num_players):
            if i in self.human_players:
                if len(self.human_players) == 1:
                    player_name = "你"
                else:
                    player_name = f"玩家{i+1}"
            else:
                player_name = f"AI{i+1}"
            player = Player(i, player_name, GameConfig.STARTING_CHIPS)
            self.players.append(player)
    
    def start_new_hand(self):
        """开始新一手牌"""
        self.hand_number += 1
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = GameConfig.MIN_RAISE
        self.betting_round_complete = False
        
        # 重置所有玩家状态
        for player in self.players:
            player.reset_for_new_hand()
        
        # 移除已淘汰的玩家
        self.players = [p for p in self.players if p.status != PlayerStatus.OUT]
        
        if len(self.players) < 2:
            self.phase = GamePhase.ENDED
            return
        
        # 设置位置
        self._set_positions()
        
        # 发底牌
        self._deal_hole_cards()
        
        # 下盲注
        self._post_blinds()
        
        # 开始翻牌前阶段
        self.phase = GamePhase.PREFLOP
        self._start_betting_round()
    
    def _set_positions(self):
        """设置玩家位置"""
        active_players = [p for p in self.players if p.status == PlayerStatus.ACTIVE]
        num_active = len(active_players)
        
        if num_active < 2:
            return
        
        # 重置所有位置
        for player in self.players:
            player.position = None
        
        # 设置庄家位置
        dealer_idx = self.dealer_position % num_active
        
        if num_active == 2:
            # 两人游戏：庄家是小盲注
            active_players[dealer_idx].position = Position.SMALL_BLIND
            active_players[(dealer_idx + 1) % num_active].position = Position.BIG_BLIND
        else:
            # 多人游戏
            active_players[dealer_idx].position = Position.BUTTON
            active_players[(dealer_idx + 1) % num_active].position = Position.SMALL_BLIND
            active_players[(dealer_idx + 2) % num_active].position = Position.BIG_BLIND
    
    def _deal_hole_cards(self):
        """发底牌"""
        deck_manager.reset_deck()
        
        # 给每个活跃玩家发2张底牌
        for _ in range(2):
            for player in self.players:
                if player.status == PlayerStatus.ACTIVE:
                    card = deck_manager.get_cards(1)[0]
                    player.hole_cards.append(card)
    
    def _post_blinds(self):
        """下盲注"""
        small_blind_player = None
        big_blind_player = None
        
        for player in self.players:
            if player.position == Position.SMALL_BLIND:
                small_blind_player = player
            elif player.position == Position.BIG_BLIND:
                big_blind_player = player
        
        # 下小盲注
        if small_blind_player:
            sb_amount = min(GameConfig.SMALL_BLIND, small_blind_player.chips)
            small_blind_player.place_bet(sb_amount)
            self.pot += sb_amount
        
        # 下大盲注
        if big_blind_player:
            bb_amount = min(GameConfig.BIG_BLIND, big_blind_player.chips)
            big_blind_player.place_bet(bb_amount)
            self.pot += bb_amount
            self.current_bet = bb_amount
    
    def _start_betting_round(self):
        """开始新的下注轮次"""
        # 重置玩家当前轮次下注
        for player in self.players:
            player.reset_for_new_betting_round()
        
        # 如果不是翻牌前，重置当前下注
        if self.phase != GamePhase.PREFLOP:
            self.current_bet = 0
        
        # 找到第一个应该行动的玩家
        self._find_first_to_act()
        self.betting_round_complete = False
    
    def _find_first_to_act(self):
        """找到第一个应该行动的玩家"""
        active_players = [p for p in self.players if p.can_act()]
        
        if not active_players:
            self.betting_round_complete = True
            return
        
        if self.phase == GamePhase.PREFLOP:
            # 翻牌前：大盲注左边的玩家先行动
            big_blind_idx = None
            for i, player in enumerate(self.players):
                if player.position == Position.BIG_BLIND:
                    big_blind_idx = i
                    break
            
            if big_blind_idx is not None:
                start_idx = (big_blind_idx + 1) % len(self.players)
                for i in range(len(self.players)):
                    player_idx = (start_idx + i) % len(self.players)
                    if self.players[player_idx].can_act():
                        self.current_player = player_idx
                        return
        else:
            # 其他阶段：小盲注先行动
            small_blind_idx = None
            for i, player in enumerate(self.players):
                if player.position == Position.SMALL_BLIND:
                    small_blind_idx = i
                    break
            
            if small_blind_idx is not None:
                for i in range(len(self.players)):
                    player_idx = (small_blind_idx + i) % len(self.players)
                    if self.players[player_idx].can_act():
                        self.current_player = player_idx
                        return
        
        # 如果没有找到特定位置，找第一个可以行动的玩家
        for i, player in enumerate(self.players):
            if player.can_act():
                self.current_player = i
                return
    
    def process_player_action(self, action: PlayerAction, amount: int = 0) -> bool:
        """
        处理玩家动作
        
        Args:
            action: 玩家动作
            amount: 动作金额(用于加注)
            
        Returns:
            bool: 动作是否成功
        """
        if self.betting_round_complete:
            return False
        
        player = self.players[self.current_player]
        if not player.can_act():
            return False
        
        success = False
        
        if action == PlayerAction.FOLD:
            player.fold()
            success = True
            
        elif action == PlayerAction.CHECK:
            if player.current_bet == self.current_bet:
                success = player.check()
            
        elif action == PlayerAction.CALL:
            call_amount = self.current_bet - player.current_bet
            if call_amount > 0:
                success = player.call(call_amount)
                if success:
                    self.pot += min(call_amount, player.chips + call_amount)
            
        elif action == PlayerAction.RAISE:
            if amount > self.current_bet:
                old_bet = player.current_bet
                success = player.raise_bet(amount)
                if success:
                    bet_increase = player.current_bet - old_bet
                    self.pot += bet_increase
                    self.current_bet = amount
                    self.min_raise = max(self.min_raise, amount - (self.current_bet - bet_increase))
            
        elif action == PlayerAction.ALL_IN:
            old_bet = player.current_bet
            all_in_amount = player.all_in()
            if all_in_amount > 0:
                self.pot += all_in_amount
                if player.current_bet > self.current_bet:
                    self.current_bet = player.current_bet
                success = True
        
        if success:
            self._move_to_next_player()
            self._check_betting_round_complete()
        
        return success
    
    def _move_to_next_player(self):
        """移动到下一个玩家"""
        start_player = self.current_player
        
        while True:
            self.current_player = (self.current_player + 1) % len(self.players)
            
            # 如果回到起始玩家，说明一轮结束
            if self.current_player == start_player:
                break
                
            # 找到可以行动的玩家
            if self.players[self.current_player].can_act():
                break
    
    def _check_betting_round_complete(self):
        """检查下注轮次是否完成"""
        active_players = [p for p in self.players if p.status == PlayerStatus.ACTIVE]
        all_in_players = [p for p in self.players if p.status == PlayerStatus.ALL_IN]
        non_folded_players = active_players + all_in_players
        
        # 如果只有一个或没有非弃牌玩家，直接结束手牌并进入摊牌
        if len(non_folded_players) <= 1:
            self.betting_round_complete = True
            self.phase = GamePhase.SHOWDOWN  # 直接进入摊牌
            self._showdown()  # 立即分配筹码给获胜者
            return
        
        # 检查是否所有可行动的玩家都已行动且下注相等
        can_act_players = [p for p in active_players if p.can_act()]
        
        if not can_act_players:
            # 没有可以行动的玩家，本轮结束
            self.betting_round_complete = True
            return
        
        # 检查所有活跃玩家的下注是否相等(除了全押玩家)
        non_all_in_active_players = [p for p in active_players if p.status != PlayerStatus.ALL_IN]
        
        if len(non_all_in_active_players) <= 1:
            self.betting_round_complete = True
            return
        
        # 检查所有非全押的活跃玩家的下注是否相等且都已行动
        for player in non_all_in_active_players:
            if player.current_bet != self.current_bet or player.last_action is None:
                return
        
        self.betting_round_complete = True
    
    def advance_to_next_phase(self):
        """进入下一个游戏阶段"""
        if self.phase == GamePhase.PREFLOP:
            self._deal_flop()
            self.phase = GamePhase.FLOP
        elif self.phase == GamePhase.FLOP:
            self._deal_turn()
            self.phase = GamePhase.TURN
        elif self.phase == GamePhase.TURN:
            self._deal_river()
            self.phase = GamePhase.RIVER
        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN
            self._showdown()
            return
        
        # 开始新的下注轮次
        self._start_betting_round()
    
    def _deal_flop(self):
        """发翻牌(2张公共牌) - 2+4模式"""
        # 烧牌
        deck_manager.get_cards(1)
        # 发2张公共牌(不是传统的3张)
        self.community_cards.extend(deck_manager.get_cards(2))
    
    def _deal_turn(self):
        """发转牌(第3张公共牌) - 2+4模式"""
        # 烧牌
        deck_manager.get_cards(1)
        # 发第3张公共牌
        self.community_cards.extend(deck_manager.get_cards(1))
    
    def _deal_river(self):
        """发河牌(第4张公共牌) - 2+4模式"""
        # 烧牌
        deck_manager.get_cards(1)
        # 发第4张公共牌(最后一张)
        self.community_cards.extend(deck_manager.get_cards(1))
    
    def _showdown(self):
        """摊牌阶段"""
        active_players = [p for p in self.players if p.status != PlayerStatus.FOLDED and p.status != PlayerStatus.OUT]
        
        if len(active_players) == 1:
            # 只有一个玩家，直接获胜
            winner = active_players[0]
            winner.chips += self.pot
            self.pot = 0  # 清空底池
            self.phase = GamePhase.ENDED  # 标记手牌结束
            return
        
        # 评估所有活跃玩家的牌力
        player_hands = []
        for player in active_players:
            if len(self.community_cards) >= 4 and len(player.hole_cards) == 2:
                # 2+4模式：2张底牌 + 4张公共牌
                hand_eval = texas_evaluator.evaluate_6_cards(player.hole_cards, self.community_cards)
                player_hands.append((player, hand_eval))
        
        # 找出获胜者
        if player_hands:
            # 按牌力排序
            player_hands.sort(key=lambda x: texas_evaluator._calculate_total_score(x[1]), reverse=True)
            
            # 分配奖池
            winners = [player_hands[0][0]]  # 至少有一个获胜者
            
            # 检查是否有平局
            best_score = texas_evaluator._calculate_total_score(player_hands[0][1])
            for player, hand_eval in player_hands[1:]:
                if texas_evaluator._calculate_total_score(hand_eval) == best_score:
                    winners.append(player)
                else:
                    break
            
            # 平分奖池
            pot_per_winner = self.pot // len(winners)
            remainder = self.pot % len(winners)
            
            for i, winner in enumerate(winners):
                winner.chips += pot_per_winner
                if i < remainder:  # 余数给前几个获胜者
                    winner.chips += 1
        
        # 清空底池并标记手牌结束
        self.pot = 0
        self.phase = GamePhase.ENDED
    
    def is_hand_complete(self) -> bool:
        """检查当前手牌是否结束"""
        active_players = [p for p in self.players if p.status not in [PlayerStatus.FOLDED, PlayerStatus.OUT]]
        
        # 只有一个或没有活跃玩家
        if len(active_players) <= 1:
            return True
        
        # 已经到摊牌阶段
        if self.phase == GamePhase.SHOWDOWN:
            return True
        
        # 在2+4模式中，河牌阶段即为最后阶段
        if self.phase == GamePhase.RIVER and self.betting_round_complete:
            return True
        
        return False
    
    def get_current_player(self) -> Optional[Player]:
        """获取当前应该行动的玩家"""
        if self.betting_round_complete or self.phase in [GamePhase.SHOWDOWN, GamePhase.ENDED]:
            return None
        return self.players[self.current_player]
    
    def get_active_players(self) -> List[Player]:
        """获取所有活跃玩家"""
        return [p for p in self.players if p.status not in [PlayerStatus.FOLDED, PlayerStatus.OUT]]
    
    def advance_dealer(self):
        """移动庄家位置到下一个玩家"""
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        active_players = [p for p in self.players if p.status != PlayerStatus.OUT]
        return len(active_players) <= 1
    
    def start_betting_round(self):
        """开始下注轮次(供外部调用)"""
        self._start_betting_round()
    
    def deal_flop(self):
        """发翻牌(供外部调用)"""
        self._deal_flop()
        self.phase = GamePhase.FLOP
    
    def deal_turn(self):
        """发转牌(供外部调用)"""
        self._deal_turn()
        self.phase = GamePhase.TURN
    
    def deal_river(self):
        """发河牌(供外部调用)"""
        self._deal_river()
        self.phase = GamePhase.RIVER
    
    def show_cards(self):
        """进入摊牌阶段(供外部调用)"""
        self.phase = GamePhase.SHOWDOWN
        self._showdown()
    
    def eliminate_players(self) -> List[Player]:
        """淘汰没有筹码的玩家"""
        eliminated = []
        for player in self.players:
            if player.chips <= 0 and player.status != PlayerStatus.OUT:
                player.status = PlayerStatus.OUT
                eliminated.append(player)
        return eliminated
    
    def next_player(self):
        """移动到下一个玩家(供外部调用)"""
        self._move_to_next_player()
    
    def is_human_player(self, player_id: int) -> bool:
        """检查指定玩家是否为人类玩家"""
        return player_id in self.human_players