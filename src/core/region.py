from typing import List, Tuple
import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QPointF

class Region:
    """分割区域类"""
    def __init__(self, name: str):
        self.name = name  # 区域名称 (a-z)
        self.points: List[QPointF] = []  # 多边形顶点列表
        self.color = QColor()  # 区域颜色
        self.is_closed = False  # 是否闭合
        self._mask = None  # 缓存的mask数组
        
    def add_point(self, point: QPointF):
        """添加顶点"""
        self.points.append(point)
        self._mask = None  # 清除缓存
        
    def close_region(self):
        """闭合区域"""
        if len(self.points) >= 3:
            self.is_closed = True
            
    def get_mask(self, rows: int, cols: int) -> np.ndarray:
        """获取区域的mask数组（使用缓存）"""
        if self._mask is not None:
            return self._mask
            
        # 创建mask数组
        self._mask = np.zeros((rows, cols), dtype=bool)
        if not self.is_closed:
            return self._mask
            
        # 使用扫描线算法填充多边形
        # TODO: 实现扫描线算法
        
        return self._mask 