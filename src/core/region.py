from typing import List, Tuple
import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QPointF, QRectF

class Region:
    """分割区域类"""
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size  # 正方形边长
        self.position = QPointF(0, 0)  # 左上角位置
        self.color = QColor()
        self.is_placed = False  # 是否已放置
    
    def set_position(self, pos: QPointF):
        """设置区域位置"""
        self.position = pos
    
    def get_rect(self) -> QRectF:
        """获取区域矩形"""
        return QRectF(self.position.x(), self.position.y(), 
                     self.size, self.size)
    
    def contains_point(self, point: QPointF) -> bool:
        """检查点是否在区域内"""
        return self.get_rect().contains(point) 