# events.py
# 事件处理（原main.py代码1:1搬运）
import pygame
import sys
from settings import *
import game_state as gs
from game_utils import get_hex_at_pixel
from movement import calculate_moveable_hexes, move_unit_with_zoc_rule
from battle import select_attacker_unit, execute_attack
from pursuit import calculate_pursuit_hexes, execute_pursuit_move
from ui import check_unit_list_click

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                gs.switch_phase()
            if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                gs.is_shift_pressed = True
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                gs.is_shift_pressed = False

        if event.type == pygame.MOUSEWHEEL:
            gs.renderer.scale += event.y * gs.ZOOM_SPEED
            gs.renderer.scale = max(gs.MIN_ZOOM, min(gs.MAX_ZOOM, gs.renderer.scale))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            gs.renderer.is_dragging = True
            gs.renderer.drag_start_pos = (event.pos[0], event.pos[1])
            gs.renderer.drag_start_offset = (gs.renderer.offset_x, gs.renderer.offset_y)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            gs.renderer.is_dragging = False
        if event.type == pygame.MOUSEMOTION and gs.renderer.is_dragging:
            dx = event.pos[0] - gs.renderer.drag_start_pos[0]
            dy = event.pos[1] - gs.renderer.drag_start_pos[1]
            gs.renderer.offset_x = gs.renderer.drag_start_offset[0] + dx
            gs.renderer.offset_y = gs.renderer.drag_start_offset[1] + dy

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if gs.cancel_pursuit_btn_rect and gs.cancel_pursuit_btn_rect.collidepoint(mouse_x, mouse_y):
                gs.reset_pursuit_status()
                print("⏹️ 已手动取消所有追击！")
                continue

            if gs.UNIT_LIST_BUTTON_RECT.collidepoint(mouse_x, mouse_y):
                gs.is_show_unit_list = not gs.is_show_unit_list
                continue

            list_click_result = check_unit_list_click((mouse_x, mouse_y))
            if list_click_result:
                unit, hex_tile = list_click_result
                if gs.current_phase in ["RED_ATTACK", "BLUE_ATTACK"]:
                    from battle import can_unit_attack
                    if not can_unit_attack(unit, gs.current_phase):
                        continue
                    item = (hex_tile, unit)
                    if item in gs.selected_units:
                        gs.selected_units.remove(item)
                    else:
                        if gs.is_shift_pressed:
                            gs.selected_units.append(item)
                        else:
                            gs.selected_units = [item]
                    from battle import get_combined_attack_targets
                    gs.valid_attack_hexes = get_combined_attack_targets(gs.selected_units, gs.hex_map)
                else:
                    if unit.has_moved or unit.is_disordered:
                        continue
                    if gs.selected_hex == hex_tile:
                        gs.selected_hex = None
                        gs.moveable_hexes = []
                        gs.enemy_zoc_hexes = set()
                        gs.own_zoc_hexes = set()
                    else:
                        gs.selected_hex = hex_tile
                        from game_utils import update_enemy_own_zoc
                        update_enemy_own_zoc(gs.selected_hex, gs.hex_map)
                        gs.moveable_hexes, gs.captured_cities = calculate_moveable_hexes(gs.selected_hex, gs.hex_map)
                    gs.selected_units = []
                    gs.valid_attack_hexes = []
                continue

            clicked_hex = get_hex_at_pixel(mouse_x, mouse_y)
            if clicked_hex:
                handle_hex_click(clicked_hex)

def handle_hex_click(clicked_hex):
    if gs.current_phase in ["RED_MOVE", "BLUE_MOVE"]:
        gs.valid_attack_hexes = []
        if gs.selected_hex is None:
            if clicked_hex.units:
                unit = clicked_hex.units[0]
                if ((gs.current_phase == "RED_MOVE" and unit.camp == RED and not unit.has_moved and not unit.is_disordered) or
                        (gs.current_phase == "BLUE_MOVE" and unit.camp == BLUE and not unit.has_moved and not unit.is_disordered)):
                    gs.selected_hex = clicked_hex
                    from game_utils import update_enemy_own_zoc
                    update_enemy_own_zoc(gs.selected_hex, gs.hex_map)
                    gs.moveable_hexes, gs.captured_cities = calculate_moveable_hexes(gs.selected_hex, gs.hex_map)
        else:
            if clicked_hex == gs.selected_hex:
                gs.selected_hex = None
                gs.moveable_hexes = []
                gs.enemy_zoc_hexes = set()
                gs.own_zoc_hexes = set()
            else:
                if clicked_hex in gs.moveable_hexes:
                    move_unit_with_zoc_rule(gs.selected_hex, clicked_hex, gs.captured_cities)
                gs.selected_hex = None
                gs.moveable_hexes = []
                gs.captured_cities = {}
                gs.enemy_zoc_hexes = set()
                gs.own_zoc_hexes = set()

    elif gs.current_phase in ["RED_ATTACK", "BLUE_ATTACK"]:
        from battle import get_attacker_camp
        attacker_camp = get_attacker_camp(gs.current_phase)
        if gs.is_pursuit_active:
            handle_pursuit_click(clicked_hex)
            return

        if clicked_hex.units and clicked_hex.units[0].camp == attacker_camp:
            is_already_selected = any(ht == clicked_hex for ht, _ in gs.selected_units)
            if is_already_selected and not gs.is_shift_pressed:
                gs.selected_units = []
                gs.valid_attack_hexes = []
                gs.target_enemy_hex = None
            else:
                select_attacker_unit(clicked_hex)
            gs.selected_hex = None
        elif clicked_hex.units and clicked_hex.units[0].camp != attacker_camp:
            gs.target_enemy_hex = clicked_hex
            execute_attack(gs.selected_units, gs.target_enemy_hex, gs.attacked_enemy_units, gs.current_phase)
        else:
            gs.selected_units = []
            gs.target_enemy_hex = None
            gs.selected_hex = None
            gs.valid_attack_hexes = []

def handle_pursuit_click(clicked_hex):
    found_pursuit_unit = None
    for unit in clicked_hex.units:
        if unit in gs.current_pursuit_units:
            found_pursuit_unit = unit
            break

    if found_pursuit_unit:
        if gs.selected_pursuit_unit == found_pursuit_unit and gs.selected_hex == clicked_hex:
            gs.selected_pursuit_unit = None
            gs.selected_hex = None
            gs.pursuit_moveable_hexes.clear()
        else:
            gs.selected_hex = clicked_hex
            gs.selected_pursuit_unit = found_pursuit_unit
            gs.pursuit_moveable_hexes.clear()
            pursuit_hexes, cities = calculate_pursuit_hexes(found_pursuit_unit, clicked_hex, gs.current_pursuit_def_hex, gs.hex_map)
            gs.pursuit_moveable_hexes.extend(pursuit_hexes)
            gs.captured_cities = cities
    elif gs.selected_pursuit_unit and gs.selected_hex and clicked_hex in gs.pursuit_moveable_hexes:
        execute_pursuit_move(gs.selected_pursuit_unit, gs.selected_hex, clicked_hex, gs.captured_cities)
        gs.selected_hex = None