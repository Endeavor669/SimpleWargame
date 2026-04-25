# ==============================
# unit.py
# Wargame 2.0 - 算子（Unit）系统
# 职责：定义作战单位的核心属性与基础行为
# ==============================

from settings import (
    UNIT_DEFAULT_ATTACK,
    UNIT_DEFAULT_MOVE,
    INFANTRY_PURSUIT_DISTANCE,
    ARMORED_PURSUIT_DISTANCE
)

# 新增：番号自动编号计数器
RED_UNIT_COUNTER = 1
BLUE_UNIT_COUNTER = 1


class Unit:
    """六边形地图作战算子（单位）- 基类"""

    def __init__(self, attack=None, move=None, camp="red", designation=None, pursuit_distance=0):
        # 攻击力：优先使用传入值，无则用默认值
        self.attack = attack if attack is not None else UNIT_DEFAULT_ATTACK
        # 移动力：优先使用传入值，无则用默认值
        self.move = move if move is not None else UNIT_DEFAULT_MOVE
        # 阵营：新增属性（red/blue）
        self.camp = camp
        # 回合行动状态（新增）
        self.has_moved = False  # 本回合是否已移动
        self.has_attacked = False  # 本回合是否已攻击
        # 新增：追击格数属性
        self.pursuit_distance = pursuit_distance
        # 新增：混乱属性，撤退后变为混乱
        self.is_disordered = False

        # 新增：番号属性（自动生成/手动指定）
        global RED_UNIT_COUNTER, BLUE_UNIT_COUNTER
        if designation is None:
            if self.camp == "red":
                self.designation = f"red_{RED_UNIT_COUNTER}"
                RED_UNIT_COUNTER += 1
            else:  # blue阵营
                self.designation = f"blue_{BLUE_UNIT_COUNTER}"
                BLUE_UNIT_COUNTER += 1
        else:
            self.designation = designation  # 手动指定番号

    def __repr__(self):
        """便于调试的字符串表示（新增番号+追击格数+混乱状态）"""
        return f"Unit(番号={self.designation}, attack={self.attack}, move={self.move}, camp={self.camp}, pursuit_distance={self.pursuit_distance}, has_moved={self.has_moved}, has_attacked={self.has_attacked}, is_disordered={self.is_disordered})"

    # 重置回合行动状态（新增）
    def reset_action_status(self):
        """回合切换时重置移动/攻击状态（混乱状态不在这里恢复）"""
        self.has_moved = False
        self.has_attacked = False

    # 新增：判断单位是否已完成当前阶段行动
    def is_action_completed(self, current_phase):
        """
        根据当前回合阶段判断单位是否已行动：
        - 移动阶段：判断has_moved
        - 攻击阶段：判断has_attacked
        """
        if current_phase in ["RED_MOVE", "BLUE_MOVE"]:
            return self.has_moved
        elif current_phase in ["RED_ATTACK", "BLUE_ATTACK"]:
            return self.has_attacked
        return False

    # 新增：判断单位是否处于混乱状态
    def is_disordered_state(self):
        return self.is_disordered

    # 新增：恢复混乱状态
    def recover_disordered(self):
        self.is_disordered = False
        print(f"🔄 单位 {self.designation} 混乱状态已恢复！")


# 新增：步兵子类
class Infantry(Unit):
    """步兵单位 - 继承自Unit"""
    def __init__(self, attack=None, move=None, camp="red", designation=None):
        # 调用父类初始化，指定步兵追击格数
        super().__init__(
            attack=attack,
            move=move,
            camp=camp,
            designation=designation,
            pursuit_distance=INFANTRY_PURSUIT_DISTANCE
        )
        # 可选：扩展步兵专属属性/方法
        self.unit_type = "infantry"  # 标记单位类型


# 新增：装甲子类
class Armored(Unit):
    """装甲单位 - 继承自Unit"""
    def __init__(self, attack=None, move=None, camp="red", designation=None):
        # 调用父类初始化，指定装甲单位追击格数
        super().__init__(
            attack=attack,
            move=move,
            camp=camp,
            designation=designation,
            pursuit_distance=ARMORED_PURSUIT_DISTANCE
        )
        # 可选：扩展装甲专属属性/方法
        self.unit_type = "armored"  # 标记单位类型