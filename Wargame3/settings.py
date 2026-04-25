# ==============================
# settings.py
# Wargame 2.0 - 全局配置文件
# 所有常量、尺寸、颜色统一管理
# 新增：中文字体加载函数（解决中文显示方框问题）
# 新增：追击高亮颜色
# ==============================
import pygame

# 地图核心超参数
MAP_RINGS = 10          # 地图圈数（可自由修改）
HEX_RADIUS = 40         # 六边形半径

# 屏幕
pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
FPS = 60

# 颜色
COLOR_BACKGROUND = (25, 25, 30)
COLOR_HEX_NORMAL = (60, 70, 90)
COLOR_HEX_BORDER = (120, 140, 170)
COLOR_PURSUIT = (0, 255, 120, 100)  # 追击高亮颜色（青绿色）

# 地形配置（新增）
TERRAIN_PLAIN = "plain"    # 平原
TERRAIN_FOREST = "forest"  # 森林
TERRAIN_RED_CITY = "red_city"      # 红方城市
TERRAIN_BLUE_CITY = "blue_city"      # 蓝方城市
# 地形移动消耗
TERRAIN_MOVE_COST = {
    TERRAIN_PLAIN: 1,
    TERRAIN_FOREST: 2,
    TERRAIN_RED_CITY: 1,
    TERRAIN_BLUE_CITY: 1
}
# 地形渲染颜色
TERRAIN_COLOR = {
    TERRAIN_PLAIN: (60, 70, 90),    # 浅灰蓝（原默认色）
    TERRAIN_FOREST: (30, 80, 40),    # 深绿
    TERRAIN_RED_CITY: (80, 70, 60),       # 深棕
    TERRAIN_BLUE_CITY: (120, 30, 80)
}

# 算子（Unit）默认属性
UNIT_DEFAULT_ATTACK = 2  # 默认攻击力
UNIT_DEFAULT_MOVE = 3    # 默认移动力
# 新增：追击格数配置
INFANTRY_PURSUIT_DISTANCE = 1  # 步兵追击格数
ARMORED_PURSUIT_DISTANCE = 2   # 装甲单位追击格数

# 阵营
RED = "red"
BLUE = "blue"

# 堆叠上限配置
RED_STACKING_LIMIT = 2   # 红方单格子堆叠上限
BLUE_STACKING_LIMIT = 2  # 蓝方单格子堆叠上限

# 中文字体配置（解决中文显示方框问题）
def get_chinese_font(size):
    """获取支持中文的字体（优先级：系统字体 → 内置兜底）"""
    # 1. 系统常见中文字体名（跨平台适配）
    font_names = [
        "Microsoft YaHei",    # Windows 微软雅黑
        "PingFang SC",       # macOS 苹方
        "WenQuanYi Micro Hei",# Linux 文泉驿微米黑
        "SimHei",            # Windows 黑体
        "Heiti TC",          # macOS 黑体
        "SimSun",            # 宋体
        "FangSong",          # 仿宋
    ]
    # 2. 遍历匹配系统已安装的中文字体
    for name in font_names:
        if pygame.font.match_font(name):
            return pygame.font.SysFont(name, size)
    # 3. 终极兜底：使用Pygame内置字体（保证中文不显示方框）
    return pygame.font.Font(pygame.font.match_font("simsun"), size)


# ====================== 战斗结果表（固定配置） ======================
BATTLE_TABLE = {
    1: ["AE", "EX", "EX", "EX", "DR1", "DR2", "DR3"],
    2: ["AE", "AR", "AR", "DR1", "DR2", "DR3", "DR4"],
    3: ["AR", "AR", "DR1", "DR2", "DR3", "DR4", "DE"],
    4: ["AR", "DR1", "DR2", "DR3", "DR4", "DE", "DE"],
    5: ["DR1", "DR2", "DR2", "DR3", "DR4", "DE", "DE"],
    6: ["DR2", "DR3", "DR3", "DR4", "DE", "DE", "DE"]
}
# 战斗结果表列名（对应战力比值）
BATTLE_COLUMNS = ["1:2", "1:1", "2:1", "3:1", "4:1", "5:1", "6:1"]