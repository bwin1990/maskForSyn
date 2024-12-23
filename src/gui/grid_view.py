from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen
import numpy as np

class GridView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = None
        self.cell_size = 10  # 每个点的默认大小
        self.offset_x = 0    # 视图偏移量
        self.offset_y = 0
        self.zoom_level = 1.0
        
        # 设置鼠标追踪，用于显示坐标
        self.setMouseTracking(True)
        
    def set_grid(self, grid):
        """设置要显示的点阵数据"""
        self.grid = grid
        self.update()
        
    def paintEvent(self, event):
        if not self.grid:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算可见区域
        visible_rect = event.rect()
        start_row = max(0, int(visible_rect.top() / (self.cell_size * self.zoom_level)))
        end_row = min(self.grid.rows, int(visible_rect.bottom() / (self.cell_size * self.zoom_level)) + 1)
        start_col = max(0, int(visible_rect.left() / (self.cell_size * self.zoom_level)))
        end_col = min(self.grid.cols, int(visible_rect.right() / (self.cell_size * self.zoom_level)) + 1)
        
        # 绘制点阵
        cell_size = self.cell_size * self.zoom_level
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                x = col * cell_size + self.offset_x
                y = row * cell_size + self.offset_y
                
                # 根据点的状态设置颜色
                if self.grid.points[row, col] == 0:
                    color = QColor(200, 200, 200)  # 未分配点
                else:
                    color = QColor(100, 100, 255)  # 已分配点
                
                painter.fillRect(x, y, cell_size-1, cell_size-1, color)
                
        # 在较高缩放级别时显示网格线
        if self.zoom_level >= 2.0:
            painter.setPen(QPen(QColor(220, 220, 220)))
            for row in range(start_row, end_row + 1):
                y = row * cell_size + self.offset_y
                painter.drawLine(visible_rect.left(), y, visible_rect.right(), y)
            
            for col in range(start_col, end_col + 1):
                x = col * cell_size + self.offset_x
                painter.drawLine(x, visible_rect.top(), x, visible_rect.bottom())
    
    def wheelEvent(self, event):
        """处理鼠标滚轮缩放"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # 计算缩放前鼠标位置对应的网格坐标
            pos = event.position()
            old_row = (pos.y() - self.offset_y) / (self.cell_size * self.zoom_level)
            old_col = (pos.x() - self.offset_x) / (self.cell_size * self.zoom_level)
            
            # 更新缩放级别
            if event.angleDelta().y() > 0:
                self.zoom_level = min(4.0, self.zoom_level * 1.2)
            else:
                self.zoom_level = max(0.5, self.zoom_level / 1.2)
                
            # 调整偏移量，保持鼠标位置对应的网格坐标不变
            new_x = pos.x() - old_col * self.cell_size * self.zoom_level
            new_y = pos.y() - old_row * self.cell_size * self.zoom_level
            self.offset_x += new_x - self.offset_x
            self.offset_y += new_y - self.offset_y
            
            self.update()
        else:
            super().wheelEvent(event)
            
    def mouseMoveEvent(self, event):
        """显示当前坐标"""
        if self.grid:
            pos = event.position()
            row = int((pos.y() - self.offset_y) / (self.cell_size * self.zoom_level))
            col = int((pos.x() - self.offset_x) / (self.cell_size * self.zoom_level))
            if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
                self.setToolTip(f"行: {row+1}, 列: {col+1}") 