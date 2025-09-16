"""
德州扑克主程序
2+4模式德州扑克游戏启动器
"""

import os
import sys
import time

# 添加项目路径到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from game_interface import GameInterface
from game_types import GamePhase, PlayerAction, PlayerStatus


def main():
    """主游戏循环"""
    interface = GameInterface()
    
    # 显示开始菜单
    interface.start_game_menu()
    
    if not interface.game:
        print("游戏初始化失败")
        return
    
    game = interface.game
    
    try:
        # 游戏主循环
        while not game.is_game_over():
            # 开始新一手牌
            game.start_new_hand()
            interface.display_game()
            
            print(f"第 {game.hand_number} 手牌开始!")
            time.sleep(1)
            
            # 翻牌前下注轮
            betting_round(interface, "翻牌前下注")
            if game.phase == GamePhase.ENDED:
                continue
            
            # 发翻牌 (3张)
            game.deal_flop()
            interface.display_game()
            print("翻牌已发出!")
            time.sleep(1)
            
            # 翻牌后下注轮
            betting_round(interface, "翻牌后下注")
            if game.phase == GamePhase.ENDED:
                continue
            
            # 发转牌 (1张)
            game.deal_turn()
            interface.display_game()
            print("转牌已发出!")
            time.sleep(1)
            
            # 转牌后下注轮 (最终下注轮)
            betting_round(interface, "转牌后下注")
            if game.phase == GamePhase.ENDED:
                continue
            
            # 摊牌阶段
            game.show_cards()
            interface.display_game()
            
            # 显示手牌结果
            interface.show_hand_result()
            
            # 检查是否有玩家被淘汰
            eliminated_players = game.eliminate_players()
            if eliminated_players:
                print("\\n玩家被淘汰:")
                for player in eliminated_players:
                    print(f"  {player.name} (筹码不足)")
                input("按回车键继续...")
        
        # 游戏结束
        interface.show_game_summary()
        
    except KeyboardInterrupt:
        print("\\n\\n游戏被中断，再见!")
    except Exception as e:
        print(f"\\n游戏出现错误: {e}")
        print("请重新启动游戏")


def betting_round(interface: GameInterface, round_name: str):
    """执行一轮下注"""
    game = interface.game
    if not game:
        return
    
    print(f"\\n--- {round_name} ---")
    time.sleep(1)
    
    game.start_betting_round()
    
    while not game.betting_round_complete:
        interface.display_game()
        
        current_player = game.players[game.current_player]
        
        # AI玩家自动决策
        if not game.is_human_player(game.current_player):
            action, amount = ai_player_decision(current_player, game)
            print(f"{current_player.name} 选择了: {format_action_with_amount(action, amount)}")
            
            game.process_player_action(action, amount)
            time.sleep(1.5)  # 给玩家观察时间
        else:
            # 人类玩家交互
            available_actions = interface.show_available_actions(current_player)
            if available_actions:
                action, amount = interface.get_player_input(available_actions)
                game.process_player_action(action, amount)
            else:
                # 没有可用动作，跳过
                game.next_player()


def ai_player_decision(player, game) -> tuple[PlayerAction, int]:
    """AI玩家决策逻辑"""
    available_actions = player.get_available_actions(game.current_bet, game.min_raise)
    
    if not available_actions:
        return PlayerAction.FOLD, 0
    
    # 简单的AI策略：
    # 1. 如果可以过牌，30%概率过牌
    # 2. 如果需要跟注，根据筹码比例决定
    # 3. 随机添加一些加注行为
    
    import random
    
    # 计算需要跟注的金额占筹码的比例
    call_amount = game.current_bet - player.current_bet
    chip_ratio = call_amount / max(player.chips, 1) if player.chips > 0 else 1.0
    
    # 根据筹码比例和随机因素决策
    decision_factor = random.random()
    
    if PlayerAction.CHECK in available_actions and decision_factor < 0.3:
        return PlayerAction.CHECK, 0
    elif PlayerAction.CALL in available_actions:
        if chip_ratio < 0.2:  # 跟注成本低
            if decision_factor < 0.7:
                return PlayerAction.CALL, 0
            elif PlayerAction.RAISE in available_actions and decision_factor < 0.85:
                # 小幅加注
                min_raise = game.current_bet + game.min_raise
                max_raise = player.chips + player.current_bet
                raise_amount = min(min_raise + random.randint(0, game.min_raise), max_raise)
                return PlayerAction.RAISE, raise_amount
        elif chip_ratio < 0.5:  # 跟注成本中等
            if decision_factor < 0.5:
                return PlayerAction.CALL, 0
        # 跟注成本高，更容易弃牌
    
    # 默认行为
    if PlayerAction.FOLD in available_actions:
        return PlayerAction.FOLD, 0
    elif PlayerAction.CHECK in available_actions:
        return PlayerAction.CHECK, 0
    elif PlayerAction.CALL in available_actions:
        return PlayerAction.CALL, 0
    else:
        return available_actions[0], 0


def format_action_with_amount(action: PlayerAction, amount: int) -> str:
    """格式化动作和金额显示"""
    from game_types import format_action, format_chips
    
    if action == PlayerAction.RAISE and amount > 0:
        return f"{format_action(action)} 到 {format_chips(amount)}"
    elif action == PlayerAction.ALL_IN:
        return f"{format_action(action)} {format_chips(amount)}"
    else:
        return format_action(action)


if __name__ == "__main__":
    main()