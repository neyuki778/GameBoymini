"""
德州扑克游戏状态和枚举定义
包含游戏阶段、玩家动作、玩家状态等定义
"""

from enum import Enum
from typing import List, Optional


class GamePhase(Enum):
    """游戏阶段"""
    WAITING = "waiting"        # 等待开始
    PREFLOP = "preflop"       # 翻牌前(发底牌)
    FLOP = "flop"             # 翻牌(3张公共牌)
    TURN = "turn"             # 转牌(第4张公共牌)
    RIVER = "river"           # 河牌(第5张公共牌)
    SHOWDOWN = "showdown"     # 摊牌
    ENDED = "ended"           # 游戏结束


class PlayerAction(Enum):
    """玩家动作"""
    FOLD = "fold"             # 弃牌
    CHECK = "check"           # 过牌(不下注)
    CALL = "call"             # 跟注
    RAISE = "raise"           # 加注
    ALL_IN = "all_in"         # 全押
    

class PlayerStatus(Enum):
    """玩家状态"""
    ACTIVE = "active"         # 活跃(还在游戏中)
    FOLDED = "folded"         # 已弃牌
    ALL_IN = "all_in"         # 已全押
    OUT = "out"               # 已淘汰(筹码为0)


class Position(Enum):
    """玩家位置"""
    SMALL_BLIND = "small_blind"   # 小盲注
    BIG_BLIND = "big_blind"       # 大盲注
    EARLY = "early"               # 早期位置
    MIDDLE = "middle"             # 中期位置
    LATE = "late"                 # 后期位置
    BUTTON = "button"             # 按钮位置


# 游戏配置常量
class GameConfig:
    """游戏配置"""
    MIN_PLAYERS = 2           # 最少玩家数
    MAX_PLAYERS = 8           # 最多玩家数
    DEFAULT_PLAYERS = 4       # 默认玩家数
    STARTING_CHIPS = 1000     # 初始筹码
    SMALL_BLIND = 10          # 小盲注
    BIG_BLIND = 20            # 大盲注
    MIN_RAISE = BIG_BLIND     # 最小加注额
    
    # 对于2+4模式，只发4张公共牌
    COMMUNITY_CARDS = 4       # 公共牌数量(修改为4张)
    HOLE_CARDS = 2            # 底牌数量


def format_chips(chips: int) -> str:
    """格式化筹码显示"""
    if chips >= 1000:
        return f"{chips//1000}K"
    return str(chips)


def format_action(action: PlayerAction, amount: int = 0) -> str:
    """格式化动作显示"""
    if action == PlayerAction.FOLD:
        return "弃牌"
    elif action == PlayerAction.CHECK:
        return "过牌"
    elif action == PlayerAction.CALL:
        return f"跟注 {amount}"
    elif action == PlayerAction.RAISE:
        return f"加注到 {amount}"
    elif action == PlayerAction.ALL_IN:
        return f"全押 {amount}"
    else:
        return str(action.value)