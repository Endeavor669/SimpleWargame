# game_utils.py
# 通用工具函数（原main.py代码1:1搬运）
import pygame
from collections import deque
from settings import *
import game_state as gs

def get_hex_at_pixel(pixel_x, pixel_y):
    q, r = gs.renderer.pixel_to_axial(pixel_x, pixel_y)
    return gs.hex_map.get_hex_by_coords(q, r)

def calculate_all_zoc(hex_map):
    zoc_dict = {"red": set(), "blue": set()}
    for hex_tile in hex_map.hexes:
        valid_units = [u for u in hex_tile.units if not u.is_disordered_state()]
        if valid_units:
            camp = valid_units[0].camp
            neighbor_coords = hex_tile.get_neighbors()
            for (q, r) in neighbor_coords:
                neighbor_hex = hex_map.get_hex_by_coords(q, r)
                if neighbor_hex:
                    zoc_dict[camp].add(neighbor_hex)
    for camp in zoc_dict:
        zoc_dict[camp] = set(zoc_dict[camp])
    return zoc_dict

def update_enemy_own_zoc(selected_hex, hex_map):
    zoc_dict = calculate_all_zoc(hex_map)
    if selected_hex and selected_hex.units:
        camp = selected_hex.units[0].camp
        enemy_camp = "blue" if camp == "red" else "red"
        gs.own_zoc_hexes = zoc_dict[camp]
        gs.enemy_zoc_hexes = zoc_dict[enemy_camp]
    else:
        gs.own_zoc_hexes = set()
        gs.enemy_zoc_hexes = set()

def is_in_enemy_zoc(hex_tile):
    return hex_tile in gs.enemy_zoc_hexes

def is_initial_in_enemy_zoc(start_hex):
    update_enemy_own_zoc(gs.selected_hex, gs.hex_map)
    return start_hex in gs.enemy_zoc_hexes

def get_stack_limit(camp):
    if camp == RED:
        return RED_STACKING_LIMIT
    elif camp == BLUE:
        return BLUE_STACKING_LIMIT
    return 0

def has_enemy_units(hex_tile, own_camp):
    if not hex_tile.units:
        return False
    return hex_tile.units[0].camp != own_camp

def is_stack_limit_reached(hex_tile, camp):
    if not hex_tile.units:
        return False
    if hex_tile.units[0].camp != camp:
        return True
    return len(hex_tile.units) >= get_stack_limit(camp)

def remove_unit_from_map(hex_tile, unit):
    if unit in hex_tile.units:
        hex_tile.units.remove(unit)
        print(f"💀 单位 {unit.designation} 被消灭！")

def is_retreat_tile_legal(start_hex, target_hex, own_camp):
    if not target_hex:
        return False
    if target_hex == start_hex:
        return False
    if has_enemy_units(target_hex, own_camp):
        return False
    if target_hex in gs.enemy_zoc_hexes:
        return False
    return True

def find_retreat_path_bfs(start_hex, camp, required_dist):
    if not start_hex:
        return [], [], []

    visited = {}
    q = deque()
    q.append((start_hex, 0))
    visited[start_hex] = 0

    empty_tiles = []
    safe_stack = []
    overload_stack = []

    while q:
        current_hex, dist = q.popleft()
        if dist == required_dist:
            if not current_hex.units:
                empty_tiles.append(current_hex)
            elif not is_stack_limit_reached(current_hex, camp):
                safe_stack.append(current_hex)
            else:
                overload_stack.append(current_hex)
        if dist >= required_dist:
            continue
        for dq, dr in current_hex.get_neighbors():
            neighbor = gs.hex_map.get_hex_by_coords(dq, dr)
            if neighbor and neighbor not in visited and is_retreat_tile_legal(start_hex, neighbor, camp):
                visited[neighbor] = dist + 1
                q.append((neighbor, dist + 1))
    return empty_tiles, safe_stack, overload_stack