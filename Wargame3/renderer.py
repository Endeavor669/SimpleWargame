# ==============================
# renderer.py （新增混乱状态可视化）
# ==============================
import math
import pygame
from settings import HEX_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT, TERRAIN_COLOR, COLOR_HEX_BORDER, get_chinese_font


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.is_dragging = False
        self.drag_start_pos = (0, 0)
        self.drag_start_offset = (0, 0)

    def axial_to_pixel(self, q, r):
        x = HEX_RADIUS * self.scale * math.sqrt(3) * (q + r / 2)
        y = HEX_RADIUS * self.scale * 3 / 2 * r
        screen_x = x + SCREEN_WIDTH // 2 + self.offset_x
        screen_y = y + SCREEN_HEIGHT // 2 + self.offset_y
        return screen_x, screen_y

    def pixel_to_axial(self, pixel_x, pixel_y):
        x = (pixel_x - SCREEN_WIDTH // 2 - self.offset_x) / (HEX_RADIUS * self.scale * math.sqrt(3))
        y = (pixel_y - SCREEN_HEIGHT // 2 - self.offset_y) / (HEX_RADIUS * self.scale * 3 / 2)
        q = x - y / 2
        r = y
        s = -q - r
        q_rounded = round(q)
        r_rounded = round(r)
        s_rounded = round(s)
        sum_error = abs(q_rounded) + abs(r_rounded) + abs(s_rounded)
        if sum_error % 2 != 0:
            dq = abs(q - q_rounded)
            dr = abs(r - r_rounded)
            ds = abs(s - s_rounded)
            if dq > dr and dq > ds:
                q_rounded = -r_rounded - s_rounded
            elif dr > ds:
                r_rounded = -q_rounded - s_rounded
            else:
                s_rounded = -q_rounded - r_rounded
                r_rounded = -q_rounded - s_rounded
        return q_rounded, r_rounded

    def get_hex_corners(self, cx, cy):
        corners = []
        scaled_radius = HEX_RADIUS * self.scale
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6
            x = cx + scaled_radius * math.cos(angle)
            y = cy + scaled_radius * math.sin(angle)
            corners.append((x, y))
        return corners

    def draw_map(self, hex_map):
        for h in hex_map.hexes:
            x, y = self.axial_to_pixel(h.q, h.r)
            corners = self.get_hex_corners(x, y)
            terrain_color = TERRAIN_COLOR[h.terrain]
            pygame.draw.polygon(self.screen, terrain_color, corners)
            pygame.draw.polygon(self.screen, COLOR_HEX_BORDER, corners, 2)
            font = get_chinese_font(int(16 * self.scale))
            terrain_text = {"plain": "平", "forest": "森", "red_city": "红城", "blue_city": "蓝城"}[h.terrain]
            text_surf = font.render(terrain_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(x, y))
            self.screen.blit(text_surf, text_rect)

    def draw_unit(self, hex_tile, selected=False, is_multi_selected=False):
        if not hex_tile.units:
            return
        camp = hex_tile.units[0].camp
        unit_radius = (HEX_RADIUS * self.scale) // 3
        offset_step = unit_radius // 2
        if camp == "red":
            unit_color = (255, 0, 0)
            selected_color = (200, 0, 0)
            multi_selected_color = (150, 0, 0)
        elif camp == "blue":
            unit_color = (0, 0, 255)
            selected_color = (0, 0, 200)
            multi_selected_color = (0, 0, 150)
        else:
            unit_color = (150, 150, 150)
            selected_color = (100, 100, 100)
            multi_selected_color = (80, 80, 80)
        if selected:
            final_color = selected_color
        elif is_multi_selected:
            final_color = multi_selected_color
        else:
            final_color = unit_color
        base_x, base_y = self.axial_to_pixel(hex_tile.q, hex_tile.r)
        for idx, unit in enumerate(hex_tile.units):
            # 混乱单位黄色边框
            disordered_border_color = (255, 200, 0) if unit.is_disordered else None

            if idx == 0:
                draw_x = base_x - offset_step
                draw_y = base_y
            elif idx == 1:
                draw_x = base_x + offset_step
                draw_y = base_y
            else:
                draw_x = base_x
                draw_y = base_y - offset_step * (idx - 1)
            draw_x_int = int(draw_x)
            draw_y_int = int(draw_y)
            if hasattr(unit, 'unit_type') and unit.unit_type == "armored":
                square_rect = pygame.Rect(draw_x_int - unit_radius, draw_y_int - unit_radius, 2 * unit_radius,
                                          2 * unit_radius)
                pygame.draw.rect(self.screen, final_color, square_rect)
                # 混乱单位绘制黄色边框
                if disordered_border_color:
                    pygame.draw.rect(self.screen, disordered_border_color, square_rect, 3)
                if is_multi_selected:
                    pygame.draw.rect(self.screen, (255, 255, 0), square_rect, 2)
            else:
                pygame.draw.circle(self.screen, final_color, (draw_x_int, draw_y_int), unit_radius)
                # 混乱单位绘制黄色边框
                if disordered_border_color:
                    pygame.draw.circle(self.screen, disordered_border_color, (draw_x_int, draw_y_int), unit_radius, 3)
                if is_multi_selected:
                    pygame.draw.circle(self.screen, (255, 255, 0), (draw_x_int, draw_y_int), unit_radius, 2)
            font = get_chinese_font(int(14 * self.scale))
            unit_text = font.render(f"{unit.attack}-{unit.move}", True, (255, 255, 255))
            text_x = draw_x - (10 * self.scale)
            text_y = draw_y + unit_radius
            self.screen.blit(unit_text, (text_x, text_y))
            designation_font = get_chinese_font(int(12 * self.scale))
            designation_surf = designation_font.render(unit.designation, True, (255, 255, 255))
            designation_rect = designation_surf.get_rect(center=(draw_x, draw_y - unit_radius - 5 * self.scale))
            self.screen.blit(designation_surf, designation_rect)
            status_font = get_chinese_font(int(16 * self.scale))
            status_text = ""
            if unit.has_moved:
                status_text += "移"
            if unit.has_attacked:
                status_text += "攻"
            # 混乱状态显示
            if unit.is_disordered:
                status_text += "混"
            if status_text:
                status_surf = status_font.render(status_text, True, (255, 255, 0))
                status_rect = status_surf.get_rect(center=(draw_x, draw_y))
                self.screen.blit(status_surf, status_rect)

    def draw_moveable_hexes(self, hex_list, color=(100, 180, 100, 80)):
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for hex_tile in hex_list:
            x, y = self.axial_to_pixel(hex_tile.q, hex_tile.r)
            corners = self.get_hex_corners(x, y)
            pygame.draw.polygon(temp_surface, color, corners)
        self.screen.blit(temp_surface, (0, 0))

    def draw_zoc(self, hex_list, color=(200, 100, 100, 50)):
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for hex_tile in hex_list:
            x, y = self.axial_to_pixel(hex_tile.q, hex_tile.r)
            corners = self.get_hex_corners(x, y)
            pygame.draw.polygon(temp_surface, color, corners)
            pygame.draw.polygon(temp_surface, (255, 255, 255, 100), corners, 1)
        self.screen.blit(temp_surface, (0, 0))

    # 【新增】攻击目标高亮方法
    def draw_attack_targets(self, hex_list, color=(255, 0, 0, 100)):
        """绘制可攻击的敌方格子（红色半透明高亮）"""
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for hex_tile in hex_list:
            x, y = self.axial_to_pixel(hex_tile.q, hex_tile.r)
            corners = self.get_hex_corners(x, y)
            pygame.draw.polygon(temp_surface, color, corners)
        self.screen.blit(temp_surface, (0, 0))