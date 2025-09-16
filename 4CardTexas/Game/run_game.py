#!/usr/bin/env python3
"""
德州扑克游戏启动脚本
直接启动2+4德州扑克游戏
"""

import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 直接导入并启动游戏
from main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"游戏启动失败: {e}")
        print("请检查依赖文件是否存在")