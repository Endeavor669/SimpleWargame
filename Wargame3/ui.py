
# ui.py
# UI绘制（原main.py代码1:1搬运）
import pygame
from settings import *
import game_state as gs

def draw_turn_info():
    font = get_chinese_font(40)
    turn_text = f"回合：{gs.current_turn} | 阶段：{gs.TURN_PHASES[gs.current_phase]}"
    text_surf = font.render(turn_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(topleft=(20, 20))
    gs.screen.blit(text_surf, text_rect)

def draw_unit_list_button():
    pygame.draw.rect(gs.screen, (80, 80, 100), gs.UNIT_LIST_BUTTON_RECT, border_radius=8)
    pygame.draw.rect(gs.screen, (150, 150, 180), gs.UNIT_LIST_BUTTON_RECT, 2, border_radius=8)
    font = get_chinese_font(30)
    button_text = "单位列表" if not gs.is_show_unit_list else "收起列表"
    text_surf = font.render(button_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=gs.UNIT_LIST_BUTTON_RECT.center)
    gs.screen.blit(text_surf, text_rect)

def draw_unit_list_window():
    if not gs.is_show_unit_list:
        return []

    window_surface = pygame.Surface(gs.UNIT_LIST_WINDOW_RECT.size, pygame.SRCALPHA)
    window_surface.fill((30, 30, 40, 230))
    pygame.draw.rect(window_surface, (150, 150, 180), (0, 0, *gs.UNIT_LIST_WINDOW_RECT.size), 2, border_radius=8)
    gs.screen.blit(window_surface, gs.UNIT_LIST_WINDOW_RECT.topleft)

    target_camp = RED if gs.current_phase in ["RED_MOVE", "RED_ATTACK"] else BLUE
    current_units = []
    for hex_tile in gs.hex_map.hexes:
        for unit in hex_tile.units:
            if unit.camp == target_camp:
                current_units.append((unit, hex_tile))

    title_font = get_chinese_font(30)
    phase_text = "红方单位" if target_camp == RED else "蓝方单位"
    status_text = "（移动阶段）" if gs.current_phase.endswith("MOVE") else "（攻击阶段）"
    title_surf = title_font.render(f"{phase_text}{status_text}", True, (255, 255, 255))
    title_rect = title_surf.get_rect(topleft=(gs.UNIT_LIST_WINDOW_RECT.x + 10, gs.UNIT_LIST_WINDOW_RECT.y + 10))
    gs.screen.blit(title_surf, title_rect)

    font = get_chinese_font(gs.UNIT_LIST_FONT_SIZE)
    start_y = gs.UNIT_LIST_WINDOW_RECT.y + 50
    max_items = (gs.UNIT_LIST_WINDOW_RECT.height - 60) // gs.UNIT_LIST_ITEM_HEIGHT

    for idx, (unit, hex_tile) in enumerate(current_units[:max_items]):
        item_y = start_y + idx * gs.UNIT_LIST_ITEM_HEIGHT
        if (hex_tile, unit) in gs.selected_units:
            text_color = (255, 255, 0)
        elif unit.is_action_completed(gs.current_phase):
            text_color = (120, 120, 120)
        else:
            text_color = (255, 255, 255)

        action_status = "已移动" if gs.current_phase.endswith("MOVE") else "已攻击"
        unit_info = f"{unit.designation} | 坐标({hex_tile.q},{hex_tile.r}) | {action_status if unit.is_action_completed(gs.current_phase) else '未行动'}"
        item_surf = font.render(unit_info, True, text_color)
        item_rect = item_surf.get_rect(topleft=(gs.UNIT_LIST_WINDOW_RECT.x + 10, item_y))
        gs.screen.blit(item_surf, item_rect)

        if idx < max_items - 1 and idx < len(current_units) - 1:
            pygame.draw.line(
                gs.screen, (80, 80, 100),
                (gs.UNIT_LIST_WINDOW_RECT.x + 10, item_y + gs.UNIT_LIST_ITEM_HEIGHT - 1),
                (gs.UNIT_LIST_WINDOW_RECT.x + gs.UNIT_LIST_WINDOW_RECT.width - 10, item_y + gs.UNIT_LIST_ITEM_HEIGHT - 1),
                1
            )
    return current_units

def check_unit_list_click(mouse_pos):
    if not gs.is_show_unit_list or not gs.UNIT_LIST_WINDOW_RECT.collidepoint(mouse_pos):
        return None

    target_camp = RED if gs.current_phase in ["RED_MOVE", "RED_ATTACK"] else BLUE
    current_units = []
    for hex_tile in gs.hex_map.hexes:
        for unit in hex_tile.units:
            if unit.camp == target_camp:
                current_units.append((unit, hex_tile))

    mouse_x, mouse_y = mouse_pos
    start_y = gs.UNIT_LIST_WINDOW_RECT.y + 50
    max_items = (gs.UNIT_LIST_WINDOW_RECT.height - 60) // gs.UNIT_LIST_ITEM_HEIGHT

    if mouse_y < start_y:
        return None
    idx = (mouse_y - start_y) // gs.UNIT_LIST_ITEM_HEIGHT
    if idx >= 0 and idx < len(current_units) and idx < max_items:
        return current_units[idx]
    return None

def draw_cancel_pursuit_btn():
    gs.cancel_pursuit_btn_rect = None
    if gs.is_pursuit_active and gs.selected_pursuit_unit and gs.selected_hex:
        unit_x, unit_y = gs.renderer.axial_to_pixel(gs.selected_hex.q, gs.selected_hex.r)
        btn_x = unit_x - gs.CANCEL_PURSUIT_BTN_WIDTH // 2
        btn_y = unit_y - 60
        gs.cancel_pursuit_btn_rect = pygame.Rect(btn_x, btn_y, gs.CANCEL_PURSUIT_BTN_WIDTH, gs.CANCEL_PURSUIT_BTN_HEIGHT)

        pygame.draw.rect(gs.screen, (200, 50, 50), gs.cancel_pursuit_btn_rect, border_radius=5)
        pygame.draw.rect(gs.screen, (255, 255, 255), gs.cancel_pursuit_btn_rect, 2, border_radius=5)
        text_surf = gs.CANCEL_PURSUIT_FONT.render("取消追击", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=gs.cancel_pursuit_btn_rect.center)
        gs.screen.blit(text_surf, text_rect)