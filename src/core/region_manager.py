from typing import List, Dict
from .region import Region
import numpy as np
import string
from PyQt6.QtGui import QColor

class RegionManager:
    """区域管理器"""
    def __init__(self):
        self.regions: Dict[str, Region] = {}  # 区域字典
        self._next_name = 0  # 下一个区域名称的索引
        self._colors = self._generate_colors(26)  # 生成26种颜色
        
    def _generate_colors(self, count: int) -> List[QColor]:
        """生成不同的颜色"""
        colors = []
        for i in range(count):
            hue = (i * 137.508) % 360  # 使用黄金角来生成分散的颜色
            color = QColor.fromHsv(int(hue), 200, 255, 127)  # 半透明色
            colors.append(color)
        return colors
        
    def create_region(self) -> Region:
        """创建新区域"""
        if self._next_name >= 26:
            raise ValueError("已达到最大区域数量限制(26)")
            
        name = string.ascii_lowercase[self._next_name]
        region = Region(name)
        region.color = self._colors[self._next_name]
        self.regions[name] = region
        self._next_name += 1
        return region
        
    def get_combined_mask(self, rows: int, cols: int) -> np.ndarray:
        """获取所有区域的组合mask"""
        combined = np.zeros((rows, cols), dtype=np.uint8)
        for name, region in self.regions.items():
            mask = region.get_mask(rows, cols)
            # 使用区域索引+1作为mask值
            combined[mask] = ord(name) - ord('a') + 1
        return combined 