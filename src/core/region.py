from typing import List, Tuple
import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QPointF, QRectF

class Region:
    """分割区域类"""
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        self.width = width   # 矩形宽度
        self.height = height # 矩形高度
        self.position = QPointF(0, 0)  # 左上角位置
        self.color = QColor()
        self.is_placed = False  # 是否已放置
    
    def set_position(self, pos: QPointF):
        """设置区域位置"""
        self.position = pos
    
    def get_rect(self) -> QRectF:
        """获取区域矩形"""
        return QRectF(self.position.x(), self.position.y(), 
                     self.width, self.height)
    
    def contains_point(self, point: QPointF) -> bool:
        """检查点是否在区域内"""
        return self.get_rect().contains(point) 
    
    def is_valid_position(self, grid_cols: int, grid_rows: int) -> bool:
        """检查区域位置是否有效（完全在点阵范围内）"""
        # 添加一个小的容差值来处理浮点数精度问题
        epsilon = 1e-10
        
        # 左边界检查
        if self.position.x() < (0 - epsilon):
            return False
        # 上边界检查    
        if self.position.y() < (0 - epsilon):
            return False
        # 右边界检查（确保整个区域都在点阵内）    
        if self.position.x() + self.width > (grid_cols + epsilon):
            return False
        # 下边界检查    
        if self.position.y() + self.height > (grid_rows + epsilon):
            return False
        
        return True 
    
    def intersects_with(self, other: 'Region') -> bool:
        """检查是否与其他区域重叠"""
        # 获取两个区域的矩形
        rect1 = self.get_rect()
        rect2 = other.get_rect()
        
        # 检查是否重叠
        return rect1.intersects(rect2) 