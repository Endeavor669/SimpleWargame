# game_state.py
# 全局变量、回合状态、追击状态 统一管理
import pygame
from settings import *
from hex_map import HexMap
from renderer import Renderer

# ====================== 全局核心实例（主文件初始化后赋值）
hex_map: HexMap = None
renderer: Renderer = None
screen = None
clock = None

# ====================== 选中与移动状态
selected_hex = None
moveable_hexes = []
captured_cities = {}
enemy_zoc_hexes = set()
own_zoc_hexes = set()

# 攻击目标
valid_attack_hexes = []
attacked_enemy_units = set()
target_enemy_hex = None

# 地图交互
ZOOM_SPEED = 0.1
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0

# 单位列表
is_show_unit_list = False
UNIT_LIST_BUTTON_RECT = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 50)
UNIT_LIST_WINDOW_RECT = pygame.Rect(SCREEN_WIDTH - 350, 80, 330, 500)
UNIT_LIST_ITEM_HEIGHT = 40
UNIT_LIST_FONT_SIZE = 24

# ====================== 回合制核心
TURN_PHASES = {
    "RED_MOVE": "红方移动阶段",
    "RED_ATTACK": "红方攻击阶段",
    "BLUE_MOVE": "蓝方移动阶段",
    "BLUE_ATTACK": "蓝方攻击阶段"
}
current_phase = "RED_MOVE"
current_turn = 1

# ====================== 多选
selected_units = []
is_shift_pressed = False

# ====================== 追击核心
current_pursuit_units = []
current_pursuit_def_hex = None
pursuit_moveable_hexes = []
is_pursuit_active = False
selected_pursuit_unit = None

# 取消追击按钮
CANCEL_PURSUIT_FONT = get_chinese_font(18)
CANCEL_PURSUIT_BTN_WIDTH = 100
CANCEL_PURSUIT_BTN_HEIGHT = 30
cancel_pursuit_btn_rect = None

# ====================== 核心状态函数（原main.py代码1:1搬运）
def reset_all_units_action_status():
    for hex_tile in hex_map.hexes:
        for unit in hex_tile.units:
            unit.reset_action_status()

def recover_disordered_units(camp):
    for hex_tile in hex_map.hexes:
        for unit in hex_tile.units:
            if unit.camp == camp and unit.is_disordered_state():
                unit.recover_disordered()

def switch_phase():
    global current_phase, current_turn, selected_hex, moveable_hexes, enemy_zoc_hexes, own_zoc_hexes, selected_units
    global attacked_enemy_units, target_enemy_hex, valid_attack_hexes, selected_pursuit_unit

    phase_order = list(TURN_PHASES.keys())
    current_idx = phase_order.index(current_phase)
    next_idx = (current_idx + 1) % len(phase_order)

    if current_phase == "RED_ATTACK":
        recover_disordered_units(RED)
    elif current_phase == "BLUE_ATTACK":
        recover_disordered_units(BLUE)

    current_phase = phase_order[next_idx]

    if current_phase == "RED_MOVE":
        current_turn += 1
        reset_all_units_action_status()

    selected_hex = None
    moveable_hexes = []
    enemy_zoc_hexes = set()
    own_zoc_hexes = set()
    selected_units = []
    attacked_enemy_units = set()
    target_enemy_hex = None
    valid_attack_hexes = []
    selected_pursuit_unit = None
    reset_pursuit_status()

def reset_pursuit_status():
    global current_pursuit_units, current_pursuit_def_hex, pursuit_moveable_hexes, is_pursuit_active, selected_pursuit_unit
    current_pursuit_units = []
    current_pursuit_def_hex = None
    pursuit_moveable_hexes = []
    is_pursuit_active = False
    selected_pursuit_unit = None
    print(f"🔄 追击状态已重置")