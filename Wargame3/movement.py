# movement.py
# 移动逻辑（原main.py代码1:1搬运）
from settings import *
import game_state as gs
from game_utils import *

def calculate_moveable_hexes(start_hex, hex_map):
    moveable = []
    if not start_hex.units:
        return moveable, {}

    own_camp = start_hex.units[0].camp
    max_move = start_hex.units[0].move
    update_enemy_own_zoc(start_hex, hex_map)
    initial_in_ezoc = is_initial_in_enemy_zoc(start_hex)

    visited = {}
    queue = [start_hex]
    visited[start_hex] = 0
    captured_cities = {}
    captured_cities[start_hex] = []

    while queue:
        current_hex = queue.pop(0)
        current_cost = visited[current_hex]
        neighbor_coords = current_hex.get_neighbors()

        for (q, r) in neighbor_coords:
            neighbor_hex = hex_map.get_hex_by_coords(q, r)
            if not neighbor_hex or neighbor_hex in visited:
                continue
            if has_enemy_units(neighbor_hex, own_camp):
                continue
            if is_stack_limit_reached(neighbor_hex, own_camp):
                continue
            if ((initial_in_ezoc and current_hex == start_hex and is_in_enemy_zoc(neighbor_hex))
                    or (is_in_enemy_zoc(current_hex) and is_in_enemy_zoc(neighbor_hex))):
                continue

            terrain_cost = TERRAIN_MOVE_COST[neighbor_hex.terrain]
            total_cost = current_cost + terrain_cost

            if total_cost <= max_move:
                visited[neighbor_hex] = total_cost
                queue.append(neighbor_hex)
                moveable.append(neighbor_hex)
                cities = captured_cities[current_hex].copy()
                if gs.current_phase == "RED_MOVE":
                    if neighbor_hex.terrain == "blue_city":
                        cities.append(neighbor_hex)
                elif gs.current_phase == "BLUE_MOVE":
                    if neighbor_hex.terrain == "red_city":
                        cities.append(neighbor_hex)
                captured_cities[neighbor_hex] = cities
    return moveable, captured_cities

def move_unit_with_zoc_rule(start_hex, target_hex, captured_cities):
    if not start_hex or not target_hex or not start_hex.units:
        return False

    unit_to_move = start_hex.units[0]
    own_camp = unit_to_move.camp

    if unit_to_move.is_disordered_state():
        print(f"🚫 单位 {unit_to_move.designation} 处于混乱状态，无法移动！")
        return False

    if gs.current_phase not in ["RED_MOVE", "BLUE_MOVE"]:
        return False
    if (gs.current_phase == "RED_MOVE" and own_camp != RED) or (gs.current_phase == "BLUE_MOVE" and own_camp != BLUE):
        return False
    if unit_to_move.has_moved:
        return False

    if has_enemy_units(target_hex, own_camp) or is_stack_limit_reached(target_hex, own_camp):
        return False

    target_hex.units.append(unit_to_move)
    start_hex.units.remove(unit_to_move)
    unit_to_move.has_moved = True

    for city_hex in captured_cities[target_hex]:
        if city_hex.terrain == "blue_city":
            city_hex.terrain = "red_city"
        elif city_hex.terrain == "red_city":
            city_hex.terrain = "blue_city"
    return True