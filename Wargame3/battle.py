# battle.py
# 战斗逻辑（原main.py代码1:1搬运）
import random
import math
from settings import *
import game_state as gs
from game_utils import *

def get_attacker_camp(current_phase):
    return RED if current_phase == "RED_ATTACK" else BLUE

def can_unit_attack(unit, current_phase):
    attacker_camp = get_attacker_camp(current_phase)
    if unit.is_disordered_state():
        print(f"🚫 单位 {unit.designation} 处于混乱状态，无法发起攻击！")
        return False
    return (current_phase in ["RED_ATTACK", "BLUE_ATTACK"] and
            unit.camp == attacker_camp and
            not unit.has_attacked)

def is_enemy_in_attack_zoc(attack_unit, enemy_hex, hex_map):
    for hex_tile in hex_map.hexes:
        if attack_unit in hex_tile.units:
            return (enemy_hex.q, enemy_hex.r) in hex_tile.get_neighbors()
    return False

def all_attackers_can_target(attack_units, enemy_hex, hex_map):
    for _, unit in attack_units:
        if not is_enemy_in_attack_zoc(unit, enemy_hex, hex_map):
            return False
    return True

def execute_retreat(units, start_hex, base_retreat_dist, hex_map):
    camp = units.camp
    update_enemy_own_zoc(start_hex, hex_map)
    retreat_unit = units
    current_dist = base_retreat_dist
    target_hex = None

    while True:
        empty_tiles, safe_stack, overload_stack = find_retreat_path_bfs(start_hex, camp, current_dist)
        all_valid = empty_tiles + safe_stack + overload_stack
        if not all_valid:
            if retreat_unit in start_hex.units:
                remove_unit_from_map(start_hex, retreat_unit)
            print(f"☠️ 单位 {retreat_unit.designation} 无撤退路径，被消灭！")
            break
        if empty_tiles:
            target_hex = random.choice(empty_tiles)
        elif safe_stack:
            target_hex = random.choice(safe_stack)
        else:
            current_dist += 1
            print(f"📦 堆叠超限！{retreat_unit.designation} 额外撤退1格，新距离：{current_dist}")
            continue
        if retreat_unit in start_hex.units:
            start_hex.units.remove(retreat_unit)
        target_hex.units.append(retreat_unit)
        retreat_unit.is_disordered = True
        print(f"🚪 单位 {retreat_unit.designation} 撤退至 ({target_hex.q},{target_hex.r})，陷入混乱！")
        break

def handle_battle_result(result_code, attackers, defenders, def_hex):
    atk_hex_and_units = []
    if attackers:
        for attacker in attackers:
            for hex_tile in gs.hex_map.hexes:
                if attacker in hex_tile.units:
                    atk_hex_and_units.append((hex_tile, attacker))
                    break

    print(f"======================================")
    print(f"🎯 执行战斗结果：{result_code}")
    print(f"======================================")

    if result_code == "AE":
        for atk_hex, attacker in atk_hex_and_units:
            remove_unit_from_map(atk_hex, attacker)
    elif result_code == "AR":
        for atk_hex, attacker in atk_hex_and_units:
            execute_retreat(attacker, atk_hex, 1, gs.hex_map)
    elif result_code == "EX":
        if attackers:
            atk_hex, attacker = random.choice(atk_hex_and_units)
            remove_unit_from_map(atk_hex, attacker)
        if defenders:
            defender = random.choice(defenders)
            remove_unit_from_map(def_hex, defender)
    elif result_code.startswith("DR"):
        dist = int(result_code.replace("DR", ""))
        for defender in defenders.copy():
            execute_retreat(defender, def_hex, dist, gs.hex_map)
    elif result_code == "DE":
        for unit in defenders.copy():
            remove_unit_from_map(def_hex, unit)

    print(f"======================================\n")

    if result_code == "EX" or not attackers:
        gs.reset_pursuit_status()
        return

    has_disordered_attacker = any(unit.is_disordered for unit in attackers)
    if has_disordered_attacker:
        print(f"🚫 攻击方单位陷入混乱，取消本次追击阶段！")
        gs.reset_pursuit_status()
        return

    gs.is_pursuit_active = True
    gs.current_pursuit_units = attackers.copy()
    gs.current_pursuit_def_hex = def_hex
    print(f"🚀 追击触发！参与进攻的单位可执行追击！")

def calculate_attack_result(attack_units, def_hex):
    attackers = [unit for _, unit in attack_units]
    defenders = def_hex.units
    if not attackers or not defenders:
        print("❌ 攻击/防守方无单位，战斗取消")
        return None

    total_atk = sum(unit.attack for unit in attackers)
    total_def = sum(unit.attack for unit in defenders)
    if def_hex.terrain in [TERRAIN_FOREST, TERRAIN_RED_CITY, TERRAIN_BLUE_CITY]:
        total_def *= 2
        print(f"🌳 防守方地形加成！总防御力翻倍 → {total_def}")

    print(f"⚔️ 总攻击力：{total_atk} | 🛡️ 总防御力：{total_def}")

    ratio_str = ""
    if total_atk > total_def:
        ratio = total_atk // total_def
        ratio_str = f"{ratio}:1"
    elif total_atk < total_def:
        ratio = math.ceil(total_def / total_atk)
        ratio_str = f"1:{ratio}"
    else:
        ratio_str = "1:1"

    if ratio_str.startswith("1:"):
        x = int(ratio_str.split(":")[1])
        if x >= 3:
            print(f"❌ 战力比值 {ratio_str} ≤ 1:3，禁止攻击！")
            return None
    if ratio_str.endswith(":1"):
        x = int(ratio_str.split(":")[0])
        if x > 6:
            ratio_str = "6:1"
            print(f"📏 战力比值超限，修正为 6:1")

    print(f"📊 最终战力比值：{ratio_str}")
    dice = random.randint(1, 6)
    print(f"🎲 掷骰结果：{dice}")

    col_idx = BATTLE_COLUMNS.index(ratio_str)
    result = BATTLE_TABLE[dice][col_idx]
    print(f"✅ 战斗结果：{result}")

    handle_battle_result(result, attackers, defenders, def_hex)
    return result

def execute_attack(attack_units, enemy_hex, attacked_units_set, current_phase):
    if not attack_units or not enemy_hex or not enemy_hex.units:
        return False

    gs.reset_pursuit_status()
    attacker_camp = get_attacker_camp(current_phase)
    defender_units = enemy_hex.units

    for _, unit in attack_units:
        if not can_unit_attack(unit, current_phase):
            print("❌ 攻击失败：存在不符合条件的攻击单位")
            return False

    if defender_units[0].camp == attacker_camp:
        print("❌ 攻击失败：不能攻击己方单位")
        return False

    if not all_attackers_can_target(attack_units, enemy_hex, gs.hex_map):
        print("❌ 攻击失败：单位不在攻击范围内")
        return False

    for unit in defender_units:
        if unit in attacked_units_set:
            print("❌ 攻击失败：敌方单位已被攻击过")
            return False

    battle_result = calculate_attack_result(attack_units, enemy_hex)
    if battle_result is None:
        return False

    for _, unit in attack_units:
        unit.has_attacked = True
    for unit in defender_units:
        attacked_units_set.add(unit)

    print(f"✅ 攻击完成！敌方格子 ({enemy_hex.q},{enemy_hex.r}) 战斗结束")

    gs.selected_units = []
    gs.target_enemy_hex = None
    gs.valid_attack_hexes = []
    return True

def get_single_unit_attack_targets(unit_hex, unit, hex_map):
    targets = set()
    neighbor_coords = unit_hex.get_neighbors()
    for q, r in neighbor_coords:
        neighbor_hex = hex_map.get_hex_by_coords(q, r)
        if neighbor_hex and has_enemy_units(neighbor_hex, unit.camp):
            targets.add(neighbor_hex)
    return targets

def get_combined_attack_targets(selected_units, hex_map):
    if not selected_units:
        return []
    hex0, unit0 = selected_units[0]
    common_targets = get_single_unit_attack_targets(hex0, unit0, hex_map)
    for hex_tile, unit in selected_units[1:]:
        unit_targets = get_single_unit_attack_targets(hex_tile, unit, hex_map)
        common_targets &= unit_targets
    return list(common_targets)

def select_attacker_unit(hex_tile):
    if not hex_tile or not hex_tile.units:
        gs.valid_attack_hexes = []
        return False

    first_unit = hex_tile.units[0]
    if not can_unit_attack(first_unit, gs.current_phase):
        gs.valid_attack_hexes = []
        return False

    if gs.target_enemy_hex is not None:
        gs.selected_units = []
        gs.target_enemy_hex = None

    if gs.is_shift_pressed:
        for unit in hex_tile.units:
            if can_unit_attack(unit, gs.current_phase) and (hex_tile, unit) not in gs.selected_units:
                gs.selected_units.append((hex_tile, unit))
    else:
        gs.selected_units = [(hex_tile, unit) for unit in hex_tile.units if can_unit_attack(unit, gs.current_phase)]

    gs.valid_attack_hexes = get_combined_attack_targets(gs.selected_units, gs.hex_map)
    return True