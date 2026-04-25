# pursuit.py
# 追击逻辑（原main.py代码1:1搬运）
from settings import *
import game_state as gs
from game_utils import *

def calculate_pursuit_hexes(unit, start_hex, def_hex, hex_map):
    pursuit_hexes = set()
    max_pursuit = unit.pursuit_distance
    own_camp = unit.camp
    captured_cities = {}
    city = []

    first_pursuit_hex = def_hex
    if (first_pursuit_hex and
            not has_enemy_units(first_pursuit_hex, own_camp) and
            not is_stack_limit_reached(first_pursuit_hex, own_camp)):
        pursuit_hexes.add(first_pursuit_hex)
        if gs.current_phase == "RED_ATTACK":
            if first_pursuit_hex.terrain == "blue_city":
                city.append(first_pursuit_hex)
        elif gs.current_phase == "BLUE_ATTACK":
            if first_pursuit_hex.terrain == "red_city":
                city.append(first_pursuit_hex)
        captured_cities[first_pursuit_hex] = city

        if max_pursuit == 2:
            update_enemy_own_zoc(start_hex, hex_map)
            if first_pursuit_hex not in gs.enemy_zoc_hexes:
                second_neighbors = first_pursuit_hex.get_neighbors()
                for q, r in second_neighbors:
                    second_hex = hex_map.get_hex_by_coords(q, r)
                    if (second_hex and
                            not has_enemy_units(second_hex, own_camp) and
                            not is_stack_limit_reached(second_hex, own_camp)):
                        pursuit_hexes.add(second_hex)
                        cities = city.copy()
                        if gs.current_phase == "RED_ATTACK":
                            if second_hex.terrain == "blue_city":
                                cities.append(second_hex)
                        elif gs.current_phase == "BLUE_ATTACK":
                            if second_hex.terrain == "red_city":
                                cities.append(second_hex)
                        captured_cities[second_hex] = cities
    return list(pursuit_hexes), captured_cities

def execute_pursuit_move(unit, start_hex, target_hex, captured_cities):
    if (not unit or not start_hex or not target_hex or unit not in gs.current_pursuit_units):
        return False

    own_camp = unit.camp
    if (has_enemy_units(target_hex, own_camp) or
            is_stack_limit_reached(target_hex, own_camp) or
            target_hex not in gs.pursuit_moveable_hexes):
        print(f"🚫 追击移动无效！")
        return False

    if unit in start_hex.units:
        start_hex.units.remove(unit)
    target_hex.units.append(unit)
    gs.current_pursuit_units.remove(unit)
    print(f"🏎️ 单位 {unit.designation} 追击至 ({target_hex.q},{target_hex.r})")

    for city_hex in captured_cities[target_hex]:
        if city_hex.terrain == "blue_city":
            city_hex.terrain = "red_city"
        elif city_hex.terrain == "red_city":
            city_hex.terrain = "blue_city"

    gs.selected_pursuit_unit = None
    gs.pursuit_moveable_hexes.clear()

    if not gs.current_pursuit_units:
        gs.reset_pursuit_status()
    return True