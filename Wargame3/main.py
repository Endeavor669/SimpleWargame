# main.py
# 主入口：仅保留初始化+主循环，无任何业务逻辑
import pygame
import sys
from settings import *
from hex_map import HexMap
from renderer import Renderer

# 导入全局状态与模块
import game_state as gs
from events import handle_events
from ui import draw_turn_info, draw_unit_list_button, draw_unit_list_window, draw_cancel_pursuit_btn

# ====================== 初始化（原代码1:1搬运）
pygame.init()
gs.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Wargame")
gs.clock = pygame.time.Clock()

# 实例化核心模块
gs.hex_map = HexMap()
gs.renderer = Renderer(gs.screen)

# 初始化单位（原代码1:1搬运）
from unit import Infantry, Armored

red_infantry = Infantry(camp=RED)
red_armored = Armored(camp=RED)
blue_infantry = Infantry(camp=BLUE)
blue_armored = Armored(camp=BLUE)

red_unit_hex = None
blue_unit_hex = None
for hex_tile in gs.hex_map.hexes:
    if hex_tile.q == 0 and hex_tile.r == 0:
        hex_tile.units.append(red_infantry)
        hex_tile.units.append(red_armored)
        red_unit_hex = hex_tile
    elif hex_tile.q == 1 and hex_tile.r == 0:
        hex_tile.units.append(blue_infantry)
        hex_tile.units.append(blue_armored)
        blue_unit_hex = hex_tile

# ====================== 主循环（极简）
running = True
while running:
    gs.screen.fill(COLOR_BACKGROUND)

    # 1. 处理所有事件
    handle_events()

    # 2. 绘制地图
    gs.renderer.draw_map(gs.hex_map)

    # 3. 绘制战斗/移动/追击高亮
    if gs.current_phase in ["RED_ATTACK", "BLUE_ATTACK"] and gs.valid_attack_hexes:
        gs.renderer.draw_attack_targets(gs.valid_attack_hexes)
    if gs.target_enemy_hex is not None:
        x, y = gs.renderer.axial_to_pixel(gs.target_enemy_hex.q, gs.target_enemy_hex.r)
        corners = gs.renderer.get_hex_corners(x, y)
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surface, (255, 0, 0, 100), corners)
        gs.screen.blit(temp_surface, (0, 0))
    if gs.selected_hex is not None:
        gs.renderer.draw_zoc(gs.enemy_zoc_hexes, color=(200, 100, 100, 50))
    if gs.selected_hex is not None and gs.current_phase in ["RED_MOVE", "BLUE_MOVE"]:
        gs.renderer.draw_moveable_hexes(gs.moveable_hexes)
    if gs.is_pursuit_active and gs.selected_hex and gs.pursuit_moveable_hexes:
        gs.renderer.draw_moveable_hexes(gs.pursuit_moveable_hexes, color=COLOR_PURSUIT)

    # 4. 绘制UI
    draw_cancel_pursuit_btn()
    for hex_tile in gs.hex_map.hexes:
        if hex_tile.units:
            is_selected = (gs.selected_hex is not None) and (hex_tile == gs.selected_hex)
            is_multi_selected = any(ht == hex_tile and u in hex_tile.units for ht, u in gs.selected_units)
            gs.renderer.draw_unit(hex_tile, selected=is_selected, is_multi_selected=is_multi_selected)
    draw_turn_info()
    draw_unit_list_button()
    draw_unit_list_window()

    # 5. 刷新屏幕
    pygame.display.flip()
    gs.clock.tick(FPS)

pygame.quit()
sys.exit()