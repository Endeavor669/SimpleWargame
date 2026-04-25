# ==============================
# hex_map.py
# Wargame 2.0 - 六边形地图系统
# 坐标：轴向坐标
# 形状：上下尖、左右平（绝对不搞反）
# 生成：MAP_RINGS 控制圈数
# ==============================

import random  # 新增：用于随机分配地形
from settings import MAP_RINGS, TERRAIN_PLAIN, TERRAIN_FOREST, TERRAIN_RED_CITY, TERRAIN_BLUE_CITY


class Hex:
    """单个六边形格子"""

    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.s = -q - r  # 立方坐标第三轴
        self.units = []  # 替换原unit属性为列表，支持堆叠多个单位
        # 新增：地形属性（随机分配，可自定义权重）
        self.terrain = self._random_terrain()

    def _random_terrain(self):
        """随机生成地形（可调整权重）"""
        terrain_types = [TERRAIN_PLAIN, TERRAIN_FOREST, TERRAIN_RED_CITY, TERRAIN_BLUE_CITY]
        # 权重：平原60%、森林30%、红方城市5%、蓝方城市5%
        weights = [0.6, 0.3, 0.05, 0.05]
        return random.choices(terrain_types, weights=weights)[0]

    def distance_to(self, other):
        """计算到另一个六边形的距离（轴向坐标标准公式）"""
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2

    def get_neighbors(self):
        """获取当前格子的6个相邻格子坐标（轴向）"""
        # 上下尖六边形的6个相邻方向（轴向坐标）
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        neighbors = []
        for dq, dr in directions:
            neighbors.append((self.q + dq, self.r + dr))
        return neighbors


class HexMap:
    """六边形地图生成器"""

    def __init__(self):
        self.hexes = []
        self.generate_map()
        # 构建坐标到Hex对象的映射，方便快速查找
        self.hex_dict = {(h.q, h.r): h for h in self.hexes}

    def generate_map(self):
        """生成环形地图（上下尖、左右平六边形）"""
        self.hexes = []
        # 生成 N 圈环形六边形网格
        for ring in range(0, MAP_RINGS + 1):
            if ring == 0:
                self.hexes.append(Hex(0, 0))
            else:
                self.hexes.extend(self._get_ring(ring))

    def get_hex_by_coords(self, q, r):
        """通过坐标快速获取Hex对象（不存在返回None）"""
        return self.hex_dict.get((q, r), None)

    def _get_ring(self, radius):
        """获取指定半径的环（轴向坐标标准算法）"""
        hexes = []
        # 6个方向（轴向坐标，上下尖六边形标准方向）
        directions = [
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, 0),
            (-1, 1),
            (0, 1)
        ]
        q, r = -radius, radius
        for dq, dr in directions:
            for _ in range(radius):
                hexes.append(Hex(q, r))
                q += dq
                r += dr
        return hexes