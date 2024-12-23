from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal

class GridView(QWidget):
    # 添加信号，用于通知坐标变化
    mouse_position_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell_size = 20  # 默认单元格大小
        self.grid = None
        self.offset = QPoint(10, 10)  # 添加边距
        # 增加更小的缩放级别
        self.zoom_levels = [
            0.01, 0.02, 0.03, 0.05, 0.07,  # 非常小的缩放级别
            0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75,  # 小缩放级别
            1.0,  # 标准大小
            1.5, 2.0, 2.5, 3.0, 4.0  # 放大级别
        ]
        self.current_zoom_index = 13  # 默认使用1.0缩放
        
        # 鼠标拖动相关
        self.last_mouse_pos = None
        self.is_panning = False
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
        # 设置焦点策略，使得widget可以接收键盘事件
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        
        # 添加当前鼠标位置属性
        self.current_grid_pos = QPoint(-1, -1)
        
        # 添加键盘移动步长
        self.key_move_step = 50  # 每次按键移动的像素数
    
    @property
    def current_cell_size(self):
        """计算当前缩放级别下的单元格大小，确保至少为1像素"""
        size = self.cell_size * self.zoom_levels[self.current_zoom_index]
        return max(1, int(size))  # 确保最小为1像素
        
    def zoom_in(self):
        """放大"""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            # 发送缩放比例变化信号
            self.update_zoom_info()
            self.update()
            
    def zoom_out(self):
        """缩小"""
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            # 发送缩放比例变化信号
            self.update_zoom_info()
            self.update()
    
    def update_zoom_info(self):
        """更新缩放信息"""
        zoom_text = f"缩放: {self.zoom_levels[self.current_zoom_index]:.2f}x"
        self.mouse_position_changed.emit(zoom_text)  # 复用现有信号
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件"""
        # 获取鼠标位置并转换为QPoint
        mouse_pos = event.position().toPoint()  # 转换为QPoint
        
        # 记录鼠标位置对应的网格坐标
        old_pos = self.screen_to_grid(mouse_pos)
        
        # 根据滚轮方向调整缩放
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
        # 调整偏移，使得鼠标下的网格点保持不变
        new_pos = self.grid_to_screen(old_pos)
        delta = mouse_pos - new_pos  # 现在两者都是QPoint类型，可以相减
        self.offset += delta
        self.update()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        # 处理拖动
        if self.is_panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()
        
        # 更新鼠标位置
        pos = event.pos()
        grid_pos = self.screen_to_grid(pos)
        
        # 检查是否在点阵范围内
        if (self.grid and 
            0 <= grid_pos.x() < self.grid.cols and 
            0 <= grid_pos.y() < self.grid.rows):
            position_text = f"({grid_pos.x()}, {grid_pos.y()})"
        else:
            position_text = "(-,-)"
            
        # 发送坐标变化信号
        self.mouse_position_changed.emit(position_text)
    
    def screen_to_grid(self, pos):
        """屏幕坐标转网格坐标"""
        cell_size = self.current_cell_size  # 现在保证不会为0
        x = (pos.x() - self.offset.x()) / cell_size
        y = (pos.y() - self.offset.y()) / cell_size
        return QPoint(int(x), int(y))
    
    def grid_to_screen(self, pos):
        """网格坐标转屏幕坐标"""
        cell_size = self.current_cell_size
        x = pos.x() * cell_size + self.offset.x()
        y = pos.y() * cell_size + self.offset.y()
        return QPoint(int(x), int(y))
    
    def get_visible_range(self):
        """获取当前可见的网格范围"""
        if not self.grid:
            return QRect()
            
        cell_size = self.current_cell_size
        
        # 计算可见区域的网格范围
        visible_rect = self.rect()
        start_col = max(0, int((visible_rect.left() - self.offset.x()) / cell_size))
        start_row = max(0, int((visible_rect.top() - self.offset.y()) / cell_size))
        end_col = min(self.grid.cols, int((visible_rect.right() - self.offset.x()) / cell_size) + 1)
        end_row = min(self.grid.rows, int((visible_rect.bottom() - self.offset.y()) / cell_size) + 1)
        
        return QRect(start_col, start_row, end_col - start_col, end_row - start_row)
    
    def paintEvent(self, event):
        if not self.grid:
            return
            
        painter = QPainter(self)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        cell_size = self.current_cell_size
        visible_range = self.get_visible_range()
        
        # 在极小缩放时（cell_size <= 2）绘制外框
        if cell_size <= 2:
            # 计算整个点阵的边界框
            left = self.offset.x()
            top = self.offset.y()
            width = self.grid.cols * cell_size
            height = self.grid.rows * cell_size
            
            # 绘制边界框
            painter.setPen(QColor(100, 100, 100))  # 灰色边框
            painter.drawRect(left, top, width, height)
            
            # 在边界框内绘制黑点
            painter.setPen(QColor(0, 0, 0))  # 黑色点
            for row in range(visible_range.top(), visible_range.bottom()):
                for col in range(visible_range.left(), visible_range.right()):
                    if (0 <= row < self.grid.rows and 
                        0 <= col < self.grid.cols and 
                        self.grid.points[row, col] == 1):
                        x = self.offset.x() + col * cell_size
                        y = self.offset.y() + row * cell_size
                        painter.drawPoint(x, y)
        else:
            # 只在单元格足够大时才绘制网格线
            if cell_size >= 4:
                painter.setPen(QColor(200, 200, 200))
                for row in range(visible_range.top(), visible_range.bottom() + 1):
                    y = self.offset.y() + row * cell_size
                    painter.drawLine(
                        self.offset.x() + visible_range.left() * cell_size, y,
                        self.offset.x() + visible_range.right() * cell_size, y
                    )
                    
                for col in range(visible_range.left(), visible_range.right() + 1):
                    x = self.offset.x() + col * cell_size
                    painter.drawLine(
                        x, self.offset.y() + visible_range.top() * cell_size,
                        x, self.offset.y() + visible_range.bottom() * cell_size
                    )
            
            # 正常绘制点阵
            for row in range(visible_range.top(), visible_range.bottom()):
                for col in range(visible_range.left(), visible_range.right()):
                    if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
                        x = self.offset.x() + col * cell_size
                        y = self.offset.y() + row * cell_size
                        
                        if self.grid.points[row, col] == 0:
                            color = QColor(255, 255, 255)
                        else:
                            color = QColor(0, 0, 0)
                        
                        painter.fillRect(x + 1, y + 1, 
                                       cell_size - 1, cell_size - 1, color)
        
        # 在高缩放级别下显示坐标
        if self.zoom_levels[self.current_zoom_index] >= 2.0:
            painter.setPen(QColor(100, 100, 100))
            # 每5个格子显示一次坐标
            for row in range(visible_range.top() - visible_range.top() % 5, 
                           visible_range.bottom(), 5):
                if 0 <= row < self.grid.rows:
                    y = self.offset.y() + row * cell_size
                    painter.drawText(5, y + cell_size//2, str(row))
            
            for col in range(visible_range.left() - visible_range.left() % 5,
                           visible_range.right(), 5):
                if 0 <= col < self.grid.cols:
                    x = self.offset.x() + col * cell_size
                    painter.drawText(x + cell_size//2, 15, str(col))
    
    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        # 获取当前鼠标位置作为缩放中心点
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        
        # 处理缩放快捷键
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:  # 加号或等号键放大
            # 记录鼠标位置对应的网格坐标
            old_pos = self.screen_to_grid(mouse_pos)
            self.zoom_in()
            # 调整偏移，使得鼠标下的网格点保持不变
            new_pos = self.grid_to_screen(old_pos)
            delta = mouse_pos - new_pos
            self.offset += delta
            
        elif event.key() == Qt.Key.Key_Minus:  # 减号键缩小
            # 记录鼠标位置对应的网格坐标
            old_pos = self.screen_to_grid(mouse_pos)
            self.zoom_out()
            # 调整偏移，使得鼠标下的网格点保持不变
            new_pos = self.grid_to_screen(old_pos)
            delta = mouse_pos - new_pos
            self.offset += delta
        
        # 方向键移动
        elif event.key() == Qt.Key.Key_Left:
            self.offset += QPoint(self.key_move_step, 0)
        elif event.key() == Qt.Key.Key_Right:
            self.offset += QPoint(-self.key_move_step, 0)
        elif event.key() == Qt.Key.Key_Up:
            self.offset += QPoint(0, self.key_move_step)
        elif event.key() == Qt.Key.Key_Down:
            self.offset += QPoint(0, -self.key_move_step)
        
        # 按住Shift键时移动速度加快
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if event.key() == Qt.Key.Key_Left:
                self.offset += QPoint(self.key_move_step * 3, 0)
            elif event.key() == Qt.Key.Key_Right:
                self.offset += QPoint(-self.key_move_step * 3, 0)
            elif event.key() == Qt.Key.Key_Up:
                self.offset += QPoint(0, self.key_move_step * 3)
            elif event.key() == Qt.Key.Key_Down:
                self.offset += QPoint(0, -self.key_move_step * 3)
        
        # 更新显示
        self.update()
        
        # 更新鼠标位置显示
        grid_pos = self.screen_to_grid(mouse_pos)
        if (self.grid and 
            0 <= grid_pos.x() < self.grid.cols and 
            0 <= grid_pos.y() < self.grid.rows):
            position_text = f"({grid_pos.x()}, {grid_pos.y()})"
        else:
            position_text = "(-,-)"
        self.mouse_position_changed.emit(position_text)