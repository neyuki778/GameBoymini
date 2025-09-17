import tkinter as tk
from tkinter import PhotoImage
import os

class TableObserverGUI:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("牌桌观察者视图")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # PNG资源路径
        self.card_path = r"c:\Users\hkx\OneDrive\桌面\2025Summer\GameBoymini\Poker\PNG\Cards (medium)"

        # 创建Canvas
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='black')
        self.canvas.pack()

        # 加载卡牌图片缓存
        self.card_images = {}
        self._load_card_images()

        # 文本标签
        self.pot_label = self.canvas.create_text(400, 50, text="奖池: 0", font=("Arial", 16), fill="white")
        self.round_label = self.canvas.create_text(400, 80, text="当前轮次: 翻牌前", font=("Arial", 14), fill="white")

        # 公共牌位置 (5个位置)
        self.community_positions = [(200, 300), (300, 300), (400, 300), (500, 300), (600, 300)]
        self.community_cards = [self.canvas.create_image(pos[0], pos[1], image=self.card_images.get('back', None)) for pos in self.community_positions]

        # 玩家信息区域
        self.player_labels = []
        for i in range(6):  # 假设最多6个玩家
            x = 50 if i < 3 else 700
            y = 150 + (i % 3) * 100
            label = self.canvas.create_text(x, y, text=f"玩家{i+1}: 筹码 1000", font=("Arial", 12), fill="white", anchor="w" if i < 3 else "e")
            self.player_labels.append(label)

    def _load_card_images(self):
        """加载所有卡牌图片"""
        try:
            self.card_images['back'] = PhotoImage(file=os.path.join(self.card_path, "card_back.png"))
            # 加载其他卡牌 (简化版，只加载部分)
            suits = ['spades', 'hearts', 'diamonds', 'clubs']
            ranks = ['02','03','04','05','06','07','08','09','10','J','Q','K','A']
            for suit in suits:
                for rank in ranks:
                    filename = f"card_{suit}_{rank}.png"
                    filepath = os.path.join(self.card_path, filename)
                    if os.path.exists(filepath):
                        self.card_images[f"{suit}_{rank}"] = PhotoImage(file=filepath)
        except Exception as e:
            print(f"加载图片失败: {e}")

    def _card_to_key(self, card):
        """将Card对象转换为图片key"""
        if not card:
            return 'back'
        suit_map = {'SPADES': 'spades', 'HEARTS': 'hearts', 'DIAMONDS': 'diamonds', 'CLUBS': 'clubs'}
        rank_map = {'TWO': '02', 'THREE': '03', 'FOUR': '04', 'FIVE': '05', 'SIX': '06',
                   'SEVEN': '07', 'EIGHT': '08', 'NINE': '09', 'TEN': '10', 'JACK': 'J',
                   'QUEEN': 'Q', 'KING': 'K', 'ACE': 'A'}
        suit = suit_map.get(card.suit.name, 'spades')
        rank = rank_map.get(card.rank.name, 'A')
        return f"{suit}_{rank}"

    def update_display(self, game_state):
        """更新显示
        game_state: 字典包含 'pot', 'round', 'community_cards', 'players'
        """
        # 更新奖池
        pot = game_state.get('pot', 0)
        self.canvas.itemconfig(self.pot_label, text=f"奖池: {pot}")

        # 更新轮次
        round_name = game_state.get('round', '翻牌前')
        self.canvas.itemconfig(self.round_label, text=f"当前轮次: {round_name}")

        # 更新公共牌
        community_cards = game_state.get('community_cards', [])
        for i, card in enumerate(community_cards[:5]):
            key = self._card_to_key(card)
            image = self.card_images.get(key, self.card_images.get('back'))
            self.canvas.itemconfig(self.community_cards[i], image=image)

        # 隐藏多余的牌
        for i in range(len(community_cards), 5):
            self.canvas.itemconfig(self.community_cards[i], image=self.card_images.get('back'))

        # 更新玩家信息
        players = game_state.get('players', [])
        for i, player in enumerate(players[:6]):
            name = player.get('name', f'玩家{i+1}')
            chips = player.get('chips', 0)
            status = player.get('status', '活跃')
            text = f"{name}: 筹码 {chips} ({status})"
            self.canvas.itemconfig(self.player_labels[i], text=text)

        # 隐藏多余玩家
        for i in range(len(players), 6):
            self.canvas.itemconfig(self.player_labels[i], text="")

        self.root.update()

    def run(self):
        """启动GUI"""
        self.root.mainloop()

# 使用示例
if __name__ == "__main__":
    gui = TableObserverGUI()
    # 模拟游戏状态
    sample_state = {
        'pot': 500,
        'round': '翻牌后',
        'community_cards': [],  # 传入Card对象列表
        'players': [
            {'name': '玩家1', 'chips': 950, 'status': '活跃'},
            {'name': '玩家2', 'chips': 800, 'status': '活跃'},
        ]
    }
    gui.update_display(sample_state)
    gui.run()