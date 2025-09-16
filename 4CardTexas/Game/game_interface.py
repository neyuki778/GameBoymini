"""
德州扑克命令行界面
提供用户友好的游戏交互界面
"""

import os
import sys
from typing import List, Optional

from game_types import GamePhase, PlayerAction, PlayerStatus, format_chips, format_action
from texas_holdem import TexasHoldemGame
from player import Player


class GameInterface:
    """游戏命令行界面"""
    
    def __init__(self):
        self.game: Optional[TexasHoldemGame] = None
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_separator(self):
        """打印分隔线"""
        print("=" * 60)
    
    def print_game_header(self):
        """打印游戏标题"""
        print("🃏 德州扑克 (2+4模式) 🃏")
        print("规则: 每位玩家2张底牌 + 4张公共牌")
        self.print_separator()
    
    def print_game_state(self):
        """显示当前游戏状态"""
        if not self.game:
            return
        
        print(f"第 {self.game.hand_number} 手牌 | 阶段: {self._format_phase(self.game.phase)}")
        print(f"底池: {format_chips(self.game.pot)} | 当前下注: {format_chips(self.game.current_bet)}")
        
        # 调试：显示筹码总量
        total_chips = sum(p.chips for p in self.game.players) + self.game.pot
        print(f"筹码总量: {total_chips} (应该是{len(self.game.players) * 1000})")
        
        # 显示公共牌
        if self.game.community_cards:
            community_str = " ".join(str(card) for card in self.game.community_cards)
            card_count = len(self.game.community_cards)
            phase_name = ""
            if card_count == 2:
                phase_name = " (翻牌)"
            elif card_count == 3:
                phase_name = " (转牌)"
            elif card_count == 4:
                phase_name = " (河牌)"
            print(f"公共牌: {community_str}{phase_name}")
        else:
            print("公共牌: (尚未发出)")
        
        print()
    
    def print_players_info(self, show_all_cards: bool = False):
        """显示所有玩家信息"""
        if not self.game:
            return
        
        print("玩家信息:")
        for i, player in enumerate(self.game.players):
            # 标记当前行动玩家
            current_marker = "👉 " if i == self.game.current_player and not self.game.betting_round_complete else "   "
            
            # 位置标记
            position_marker = ""
            if player.position:
                if player.position.value == "small_blind":
                    position_marker = "(SB) "
                elif player.position.value == "big_blind":
                    position_marker = "(BB) "
                elif player.position.value == "button":
                    position_marker = "(BTN) "
            
            # 显示玩家基本信息
            status_info = self._get_player_status_info(player)
            # 人类玩家显示真实手牌，AI玩家显示背面或在摊牌时显示真实手牌
            is_human = self.game.is_human_player(i) if self.game else False
            hand_display = player.get_hand_display(show_all_cards or is_human)
            
            # 当前手牌总下注 (total_bet)
            total_bet_info = f" | 总下注:{format_chips(player.total_bet):>4}" if player.total_bet > 0 else ""
            
            print(f"{current_marker}{position_marker}{player.name:8} | 筹码:{format_chips(player.chips):>6} | "
                  f"底牌:{hand_display} | 当前下注:{format_chips(player.current_bet):>4}{total_bet_info} {status_info}")
        
        print()
    
    def _get_player_status_info(self, player: Player) -> str:
        """获取玩家状态信息"""
        if player.status == PlayerStatus.FOLDED:
            return "| 已弃牌"
        elif player.status == PlayerStatus.ALL_IN:
            return "| 全押"
        elif player.last_action:
            return f"| {format_action(player.last_action)}"
        else:
            return ""
    
    def _format_phase(self, phase: GamePhase) -> str:
        """格式化游戏阶段"""
        phase_names = {
            GamePhase.WAITING: "等待开始",
            GamePhase.PREFLOP: "翻牌前",
            GamePhase.FLOP: "翻牌",
            GamePhase.TURN: "转牌", 
            GamePhase.RIVER: "河牌",
            GamePhase.SHOWDOWN: "摊牌",
            GamePhase.ENDED: "游戏结束"
        }
        return phase_names.get(phase, str(phase.value))
    
    def show_available_actions(self, player: Player) -> List[PlayerAction]:
        """显示并获取可用动作"""
        if not self.game:
            return []
        
        available_actions = player.get_available_actions(self.game.current_bet, self.game.min_raise)
        
        if not available_actions:
            return []
        
        print(f"{player.name}的回合，可用动作:")
        
        action_map = {}
        for i, action in enumerate(available_actions):
            key = str(i + 1)
            action_map[key] = action
            
            # 显示动作描述
            if action == PlayerAction.FOLD:
                print(f"  {key}. 弃牌")
            elif action == PlayerAction.CHECK:
                print(f"  {key}. 过牌")
            elif action == PlayerAction.CALL:
                call_amount = self.game.current_bet - player.current_bet
                print(f"  {key}. 跟注 {format_chips(call_amount)}")
            elif action == PlayerAction.RAISE:
                min_raise_to = self.game.current_bet + self.game.min_raise
                max_raise_to = player.chips + player.current_bet
                print(f"  {key}. 加注 (范围: {format_chips(min_raise_to)} - {format_chips(max_raise_to)})")
            elif action == PlayerAction.ALL_IN:
                print(f"  {key}. 全押 {format_chips(player.chips)}")
        
        print()
        return available_actions
    
    def get_player_input(self, available_actions: List[PlayerAction]) -> tuple[PlayerAction, int]:
        """获取玩家输入"""
        while True:
            try:
                choice = input("请选择动作 (输入数字): ").strip()
                
                if choice == "help" or choice == "h":
                    self._show_help()
                    continue
                
                if choice == "rules" or choice == "r":
                    self._show_rules()
                    continue
                
                # 解析数字选择
                try:
                    action_index = int(choice) - 1
                    if 0 <= action_index < len(available_actions):
                        action = available_actions[action_index]
                        
                        # 如果是加注，需要获取加注金额
                        if action == PlayerAction.RAISE:
                            return self._get_raise_amount(action)
                        else:
                            return action, 0
                    else:
                        print("无效选择，请重新输入")
                except ValueError:
                    print("请输入有效的数字")
                    
            except KeyboardInterrupt:
                print("\\n游戏已退出")
                sys.exit(0)
    
    def _get_raise_amount(self, action: PlayerAction) -> tuple[PlayerAction, int]:
        """获取加注金额"""
        if not self.game:
            return action, 0
        
        player = self.game.players[self.game.current_player]
        min_raise_to = self.game.current_bet + self.game.min_raise
        max_raise_to = player.chips + player.current_bet
        
        while True:
            try:
                amount_str = input(f"请输入加注金额 ({format_chips(min_raise_to)} - {format_chips(max_raise_to)}): ").strip()
                amount = int(amount_str)
                
                if min_raise_to <= amount <= max_raise_to:
                    return action, amount
                else:
                    print(f"加注金额必须在 {format_chips(min_raise_to)} 到 {format_chips(max_raise_to)} 之间")
                    
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\\n返回动作选择")
                return self.get_player_input(player.get_available_actions(self.game.current_bet, self.game.min_raise))
    
    def _show_help(self):
        """显示帮助信息"""
        print("\\n=== 帮助信息 ===")
        print("输入数字选择动作")
        print("输入 'help' 或 'h' 查看帮助")
        print("输入 'rules' 或 'r' 查看游戏规则")
        print("按 Ctrl+C 退出游戏")
        print()
    
    def _show_rules(self):
        """显示游戏规则"""
        print("\\n=== 2+4德州扑克规则 ===")
        print("1. 每位玩家获得2张底牌")
        print("2. 发出4张公共牌 (翻牌3张 + 转牌1张)")
        print("3. 从6张牌中选出最佳的5张牌")
        print("4. 牌型大小: 皇家同花顺 > 同花顺 > 四条 > 葫芦 > 同花 > 顺子 > 三条 > 两对 > 对子 > 高牌")
        print("5. 动作说明:")
        print("   - 弃牌: 放弃本手牌")
        print("   - 过牌: 不下注但继续游戏")
        print("   - 跟注: 跟上当前最高下注")
        print("   - 加注: 提高下注金额")
        print("   - 全押: 下注全部筹码")
        print()
    
    def show_hand_result(self):
        """显示手牌结果"""
        if not self.game:
            return
        
        print("\\n" + "="*30 + " 手牌结果 " + "="*30)
        
        # 显示所有玩家的最终手牌
        active_players = [p for p in self.game.players if p.status != PlayerStatus.FOLDED]
        
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"🎉 {winner.name} 获胜! (其他玩家已弃牌)")
            print(f"获得底池: {format_chips(self.game.pot)}")
        else:
            print("最终手牌:")
            
            # 导入评估器进行牌力计算
            try:
                sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Poker', 'holdem'))
                from texas_holdem_evaluator import texas_evaluator
                
                player_results = []
                for player in active_players:
                    if len(self.game.community_cards) >= 4 and len(player.hole_cards) == 2:
                        hand_eval = texas_evaluator.evaluate_6_cards(player.hole_cards, self.game.community_cards)
                        score = texas_evaluator._calculate_total_score(hand_eval)
                        player_results.append((player, hand_eval, score))
                
                # 按分数排序
                player_results.sort(key=lambda x: x[2], reverse=True)
                
                for i, (player, hand_eval, score) in enumerate(player_results):
                    hand_cards_str = " ".join(str(card) for card in hand_eval.cards)
                    print(f"{i+1}. {player.name:8} | {hand_eval.hand_type} | 使用牌: {hand_cards_str}")
                
                # 显示获胜者
                if player_results:
                    best_score = player_results[0][2]
                    winners = [result[0] for result in player_results if result[2] == best_score]
                    
                    if len(winners) == 1:
                        print(f"\\n🎉 获胜者: {winners[0].name}")
                    else:
                        winner_names = ", ".join(w.name for w in winners)
                        print(f"\\n🤝 平局获胜者: {winner_names}")
            
            except ImportError:
                print("无法导入手牌评估器，显示基本信息")
                for i, player in enumerate(active_players):
                    hand_display = player.get_hand_display(True)
                    print(f"{i+1}. {player.name:8} | 底牌: {hand_display}")
        
        print()
        input("按回车键继续...")
    
    def show_game_summary(self):
        """显示游戏总结"""
        if not self.game:
            return
        
        print("\\n" + "="*25 + " 游戏结束 " + "="*25)
        print("最终排名:")
        
        # 按筹码排序
        sorted_players = sorted(self.game.players, key=lambda p: p.chips, reverse=True)
        
        for i, player in enumerate(sorted_players):
            print(f"{i+1}. {player.name:8} - {format_chips(player.chips)} 筹码")
        
        print("\\n感谢游戏!")
    
    def display_game(self):
        """显示完整游戏界面"""
        self.clear_screen()
        self.print_game_header()
        self.print_game_state()
        self.print_players_info()
    
    def start_game_menu(self):
        """开始游戏菜单"""
        self.clear_screen()
        self.print_game_header()
        
        print("欢迎来到德州扑克!")
        print("这是一个2+4模式的德州扑克游戏")
        print("每位玩家2张底牌，4张公共牌")
        print()
        
        # 获取玩家数量
        num_players = self._get_player_count()
        if num_players is None:
            return
        
        # 获取人类玩家设置
        human_players = self._get_human_players_setup(num_players)
        if human_players is None:
            return
        
        # 创建游戏
        self.game = TexasHoldemGame(num_players, human_players)
    
    def _get_player_count(self) -> Optional[int]:
        """获取玩家数量"""
        while True:
            try:
                num_players_input = input(f"请输入玩家数量 (2-8，默认4): ").strip()
                if not num_players_input:
                    return 4
                
                num_players = int(num_players_input)
                if 2 <= num_players <= 8:
                    return num_players
                else:
                    print("玩家数量必须在2-8之间")
                    
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\\n再见!")
                return None
    
    def _get_human_players_setup(self, total_players: int) -> Optional[List[int]]:
        """获取人类玩家设置"""
        print(f"\\n总共 {total_players} 位玩家")
        print("现在设置哪些玩家由您操作 (其余为AI)")
        print("玩家编号: 1, 2, 3, ...", total_players)
        print()
        
        while True:
            try:
                human_input = input("请输入您要操作的玩家编号 (用逗号分隔，如: 1,3,5 或直接回车默认只操作玩家1): ").strip()
                
                if not human_input:
                    return [0]  # 默认只操作第一个玩家(编号0)
                
                # 解析输入
                human_numbers = []
                for num_str in human_input.split(','):
                    num_str = num_str.strip()
                    if num_str:
                        player_num = int(num_str)
                        if 1 <= player_num <= total_players:
                            human_numbers.append(player_num - 1)  # 转换为0基索引
                        else:
                            print(f"玩家编号 {player_num} 超出范围 (1-{total_players})")
                            raise ValueError()
                
                if not human_numbers:
                    print("至少需要操作一个玩家")
                    continue
                
                # 去重并排序
                human_players = sorted(list(set(human_numbers)))
                
                # 显示确认信息
                human_names = [f"玩家{i+1}" for i in human_players]
                ai_players = [i for i in range(total_players) if i not in human_players]
                ai_names = [f"AI{i+1}" for i in ai_players]
                
                print(f"\\n设置确认:")
                print(f"您操作的玩家: {', '.join(human_names)}")
                print(f"AI玩家: {', '.join(ai_names)}")
                
                confirm = input("确认这个设置吗? (y/n，默认y): ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return human_players
                
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\\n再见!")
                return None