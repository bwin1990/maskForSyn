from PyQt6.QtWidgets import (QWidget, QDialog, QMessageBox, 
                            QMainWindow)
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal, QPointF
from core.region_manager import RegionManager
from core.region import Region
from gui.region_size_dialog import RegionSizeDialog

class GridView(QWidget):
    # 添加信号，用于通知坐标变化
    mouse_position_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell_size = 20  # 默认单元格大小
        self.grid = None
        self.offset = QPoint(10, 10)  # 添加边距
        # 修改缩放级别，添加更小的缩放比例
        self.zoom_levels = [
            0.001, 0.002, 0.003, 0.005, 0.007,  # 超小缩放级别
            0.01, 0.02, 0.03, 0.05, 0.07,       # 很小缩放级别
            0.1, 0.15, 0.2, 0.3, 0.5, 0.7,      # 小缩放级别
            1.0,                                 # 标准大小
            1.5, 2.0                            # 放大级别
        ]
        self.current_zoom_index = self.zoom_levels.index(1.0)  # 默认使用1.0缩放
        
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
        
        self.region_manager = RegionManager()
        self.current_region = None  # 当前正在绘制的区域
        
        # 添加区域创建相关的状态
        self.is_creating_region = False
        self.current_region = None
        
        # 添加鼠标悬停位置属性
        self.hover_pos = QPoint(-1, -1)  # 初始化为无效位置
        # 添加上一次悬停位置，用于优化重绘
        self.last_hover_pos = QPoint(-1, -1)
        
        self.dragging_region = None  # 当前正在拖动的区域
        self.drag_offset = QPointF(0, 0)  # 拖动偏移
    
    @property
    def current_cell_size(self):
        """计算当前缩放级别下的单元格大小"""
        size = self.cell_size * self.zoom_levels[self.current_zoom_index]
        # 不再强制最小值为1，而是返回实际计算值
        return size
        
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
        if not self.grid:  # 如果没有点阵数据，直接返回
            return
        
        # 获取鼠标位置并转换为QPoint
        mouse_pos = event.position().toPoint()
        
        # 记录鼠标位置对应的网格坐标
        old_pos = self.screen_to_grid(mouse_pos)
        
        # 根据滚轮方向调整缩放
        if event.angleDelta().y() > 0:
            if self.current_zoom_index < len(self.zoom_levels) - 1:
                self.current_zoom_index += 1
                self.update_zoom_info()
        else:
            if self.current_zoom_index > 0:
                self.current_zoom_index -= 1
                self.update_zoom_info()
        
        # 调整偏移，使得鼠标下的网格点保持不变
        try:
            new_pos = self.grid_to_screen(QPointF(old_pos.x(), old_pos.y()))
            delta = mouse_pos - QPoint(int(new_pos.x()), int(new_pos.y()))
            self.offset += delta
        except Exception as e:
            print(f"缩放调整错误: {e}")
        
        self.update()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.LeftButton and self.dragging_region:
            # 开始拖动区域
            grid_pos = self.screen_to_grid(event.pos())
            # 检查是否点击在区域内
            if self.dragging_region.contains_point(grid_pos):
                # 计算区域中心点
                region_center = QPointF(
                    self.dragging_region.position.x() + self.dragging_region.size / 2,
                    self.dragging_region.position.y() + self.dragging_region.size / 2
                )
                # 计算鼠标点击位置相对于区域中心的偏移
                self.drag_offset = QPointF(grid_pos.x() - region_center.x(),
                                         grid_pos.y() - region_center.y())
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                # 如果点击在区域外，取消拖动
                self.dragging_region = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.is_creating_region and event.button() == Qt.MouseButton.LeftButton:
            # 开始创建新区域或添加点到当前区域
            grid_pos = self.screen_to_grid(event.pos())
            if 0 <= grid_pos.x() < self.grid.cols and 0 <= grid_pos.y() < self.grid.rows:
                if not self.current_region:
                    # 开始新区域
                    self.current_region = self.region_manager.create_region()
                
                # 添加点到当前区域
                self.current_region.add_point(QPointF(grid_pos.x(), grid_pos.y()))
                self.update()
        elif self.is_creating_region and event.button() == Qt.MouseButton.RightButton:
            # 右键完成区域创建
            if self.current_region and len(self.current_region.points) >= 3:
                self.current_region.close_region()
                self.is_creating_region = False
                self.current_region = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                # 取消工具栏按钮的选中状态
                from PyQt6.QtWidgets import QMainWindow  # 添加导入
                parent = self.parent()
                if isinstance(parent, QMainWindow):
                    parent.create_region_action.setChecked(False)
                self.update()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif event.button() == Qt.MouseButton.LeftButton and self.dragging_region:
            print(f"\n鼠标释放前状态:")
            print(f"  - region名称: {self.dragging_region.name}")
            print(f"  - is_placed: {self.dragging_region.is_placed}")
            print(f"  - manager中的is_placed: {self.region_manager.regions[self.dragging_region.name].is_placed}")
            
            # 检查是否与其他区域重叠
            if self.region_manager.check_overlap(self.dragging_region):
                # 重叠，删除区域并显示警告
                name = self.dragging_region.name
                self.region_manager.remove_region(name)
                self.dragging_region = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                QMessageBox.warning(self, "错误", "区域与已有区域重叠，请重新放置")
            else:
                # 先更新region_manager中的状态
                name = self.dragging_region.name
                self.region_manager.regions[name].is_placed = True
                # 再更新dragging_region的状态
                self.dragging_region.is_placed = True
                
                print(f"\n设置is_placed后:")
                print(f"  - region名称: {name}")
                print(f"  - dragging_region的is_placed: {self.dragging_region.is_placed}")
                print(f"  - manager中的is_placed: {self.region_manager.regions[name].is_placed}")
                
                # 清除拖动状态
                self.dragging_region = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # 取消工具栏按钮的选中状态
            if isinstance(self.parent(), QMainWindow):
                self.parent().create_region_action.setChecked(False)
            
            print("\n状态更新后的所有区域:")
            for name, region in self.region_manager.regions.items():
                print(f"区域 {name}:")
                print(f"  - is_placed: {region.is_placed}")
            
            self.update()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        # 处理视图平移
        if self.is_panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()
            return  # 拖动时不处理悬停效果
        
        # 处理区域拖动
        if self.dragging_region:
            grid_pos = self.screen_to_grid(event.pos())
            
            # 首先限制grid_pos在有效范围内
            grid_pos.setX(max(0, min(self.grid.cols, grid_pos.x())))
            grid_pos.setY(max(0, min(self.grid.rows, grid_pos.y())))
            
            # 计算新的中心位置（取整到最近的整数）
            center_x = round(grid_pos.x() - self.drag_offset.x())
            center_y = round(grid_pos.y() - self.drag_offset.y())
            
            # 从中心位置计算左上角位置
            new_x = round(center_x - self.dragging_region.size / 2)
            new_y = round(center_y - self.dragging_region.size / 2)
            
            # 限制在网格范围内
            max_x = self.grid.cols - self.dragging_region.size
            max_y = self.grid.rows - self.dragging_region.size
            
            # 确保位置是整数，并严格限制在有效范围内
            new_x = max(0, min(int(max_x), int(new_x)))
            new_y = max(0, min(int(max_y), int(new_y)))
            
            # 更新区域位置
            self.dragging_region.set_position(QPointF(new_x, new_y))
            
            # 检查位置是否有效和是否重叠
            is_valid = self.dragging_region.is_valid_position(self.grid.cols, self.grid.rows)
            is_overlapping = self.region_manager.check_overlap(self.dragging_region)
            
            # 更新region_manager中的状态
            name = self.dragging_region.name
            if name in self.region_manager.regions:
                self.region_manager.regions[name].position = self.dragging_region.position
                self.region_manager.regions[name].is_placed = True
            
            # 更新dragging_region的状态
            self.dragging_region.is_placed = True
            
            if not is_valid or is_overlapping:
                self.setCursor(Qt.CursorShape.ForbiddenCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            
            self.update()
            
            # 更新状态栏显示
            position_text = f"区域 {self.dragging_region.name.upper()}: ({int(new_x)}, {int(new_y)})"
            if not is_valid:
                position_text += " - 位置无效"
            elif is_overlapping:
                position_text += " - 与其他区域重叠"
            self.mouse_position_changed.emit(position_text)
            return
        
        # 更新鼠标位置
        pos = event.pos()
        grid_pos = self.screen_to_grid(pos)
        
        # 检查是否在点阵范围内
        if (self.grid and 
            0 <= grid_pos.x() < self.grid.cols and 
            0 <= grid_pos.y() < self.grid.rows):
            new_hover_pos = QPoint(int(grid_pos.x()), int(grid_pos.y()))
            
            # 只有当位置改变时才更新
            if new_hover_pos != self.hover_pos:
                self.last_hover_pos = self.hover_pos  # 保存旧位置
                self.hover_pos = new_hover_pos
                
                # 计算需要重绘的区域
                cell_size = self.current_cell_size
                if cell_size > 2:  # 只在格子足够大时才显示悬停效果
                    # 重绘旧位置
                    if self.last_hover_pos != QPoint(-1, -1):
                        x = int(self.offset.x() + self.last_hover_pos.x() * cell_size)
                        y = int(self.offset.y() + self.last_hover_pos.y() * cell_size)
                        self.update(QRect(x, y, int(cell_size), int(cell_size)))
                    
                    # 重绘新位置
                    x = int(self.offset.x() + self.hover_pos.x() * cell_size)
                    y = int(self.offset.y() + self.hover_pos.y() * cell_size)
                    self.update(QRect(x, y, int(cell_size), int(cell_size)))
                
                # 使用悬停位置更新坐标显示
                position_text = f"({self.hover_pos.x()}, {self.hover_pos.y()})"
                self.mouse_position_changed.emit(position_text)
        else:
            # 鼠标移出点阵范围时清除悬停效果
            if self.hover_pos != QPoint(-1, -1):
                cell_size = self.current_cell_size
                if cell_size > 2:
                    x = int(self.offset.x() + self.hover_pos.x() * cell_size)
                    y = int(self.offset.y() + self.hover_pos.y() * cell_size)
                    self.update(QRect(x, y, int(cell_size), int(cell_size)))
                self.hover_pos = QPoint(-1, -1)
                # 清除坐标显示
                self.mouse_position_changed.emit("(-,-)")
    
    def screen_to_grid(self, pos):
        """屏幕坐标转网格坐标"""
        try:
            cell_size = self.current_cell_size  # 现在保证不会为0
            x = (pos.x() - self.offset.x()) / cell_size
            y = (pos.y() - self.offset.y()) / cell_size
            return QPointF(x, y)  # 返回浮点坐标
        except Exception as e:
            print(f"坐标转换错误: {e}")
            return QPointF(0, 0)
    
    def grid_to_screen(self, pos):
        """网格坐标转屏幕坐标"""
        cell_size = self.current_cell_size
        x = pos.x() * cell_size + self.offset.x()
        y = pos.y() * cell_size + self.offset.y()
        return QPointF(float(x), float(y))  # 返回QPointF而不是QPoint
    
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
        rect = event.rect()
        painter.fillRect(rect, QColor(240, 240, 240))
        
        cell_size = self.current_cell_size
        visible_range = self.get_visible_range()
        
        if cell_size <= 2:
            # 小缩放比例下的绘制代码
            # 计算整点阵的边界框
            left = int(self.offset.x())
            top = int(self.offset.y())
            width = int(self.grid.cols * cell_size)
            height = int(self.grid.rows * cell_size)
            
            # 绘制边界框
            painter.setPen(QColor(100, 100, 100))
            painter.drawRect(left, top, width, height)
            
            # 在边界框内绘制点
            for row in range(visible_range.top(), visible_range.bottom()):
                for col in range(visible_range.left(), visible_range.right()):
                    if (0 <= row < self.grid.rows and 
                        0 <= col < self.grid.cols and 
                        self.grid.get_point(row, col) == 1):
                        x = int(self.offset.x() + col * cell_size)
                        y = int(self.offset.y() + row * cell_size)
                        # 根据缩放比例调整点的透明度
                        alpha = min(255, int(255 * cell_size))
                        painter.setPen(QColor(0, 0, 0, alpha))
                        painter.drawPoint(x, y)
        else:
            # 网格线绘制代码
            if cell_size >= 4:
                painter.setPen(QColor(200, 200, 200))
                # 绘制水平网格线
                for row in range(visible_range.top(), visible_range.bottom() + 1):
                    if row <= self.grid.rows:  # 修改条件，包含最后一行
                        y = int(self.offset.y() + row * cell_size)
                        painter.drawLine(
                            int(self.offset.x() + visible_range.left() * cell_size),
                            y,
                            int(self.offset.x() + (visible_range.right() + 1) * cell_size),  # 修改这里，确保线段长度一致
                            y
                        )
                
                # 绘制垂直网格线
                for col in range(visible_range.left(), visible_range.right() + 1):
                    if col <= self.grid.cols:  # 修改条件，包含最后一列
                        x = int(self.offset.x() + col * cell_size)
                        painter.drawLine(
                            x,
                            int(self.offset.y() + visible_range.top() * cell_size),
                            x,
                            int(self.offset.y() + (visible_range.bottom() + 1) * cell_size)  # 修改这里，确保线段长度一致
                        )
            
            # 正常绘制点阵
            for row in range(visible_range.top(), visible_range.bottom() + 1):
                for col in range(visible_range.left(), visible_range.right() + 1):
                    if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
                        x = int(self.offset.x() + col * cell_size)
                        y = int(self.offset.y() + row * cell_size)
                        
                        # 简化悬停效果的判断
                        is_hover = (col == self.hover_pos.x() and row == self.hover_pos.y())
                        
                        # 根据状态设置颜色
                        if self.grid.get_point(row, col) == 0:
                            color = QColor(220, 220, 220) if is_hover else QColor(255, 255, 255)
                        else:
                            color = QColor(50, 50, 50) if is_hover else QColor(0, 0, 0)
                        
                        painter.fillRect(x + 1, y + 1, 
                                       int(cell_size - 1), int(cell_size - 1), color)
        
        # 在高缩放级别下显示坐标
        if self.zoom_levels[self.current_zoom_index] >= 2.0:
            painter.setPen(QColor(100, 100, 100))
            # 每5个格子显示一次坐标
            for row in range(visible_range.top() - visible_range.top() % 5, 
                           visible_range.bottom(), 5):
                if 0 <= row < self.grid.rows:
                    y = int(self.offset.y() + row * cell_size)  # 转换为整数
                    painter.drawText(5, y + int(cell_size / 2), str(row))
            
            for col in range(visible_range.left() - visible_range.left() % 5,
                           visible_range.right(), 5):
                if 0 <= col < self.grid.cols:
                    x = int(self.offset.x() + col * cell_size)  # 转换为整数
                    painter.drawText(x + int(cell_size / 2), 15, str(col))
        
        # 绘制区域
        if cell_size > 2:  # 只在足够大时绘制区域
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 添加调试信息
            print("\n当前所有区域状态：")
            for name, region in self.region_manager.regions.items():
                print(f"区域 {name}:")
                print(f"  - 位置: ({region.position.x()}, {region.position.y()})")
                print(f"  - 大小: {region.size}")
                print(f"  - 是否放置: {region.is_placed}")
                print(f"  - 位置是否有效: {region.is_valid_position(self.grid.cols, self.grid.rows)}")
            
            # 绘制所有区域，包括正在拖动的和已放置的
            for name, region in self.region_manager.regions.items():
                if region.is_placed or (self.dragging_region and region.name == self.dragging_region.name):
                    is_invalid = not region.is_valid_position(self.grid.cols, self.grid.rows)
                    self._draw_region(painter, region, is_invalid=is_invalid)
    
    def _draw_region(self, painter: QPainter, region: Region, is_invalid: bool = False):
        """绘制区域"""
        rect = region.get_rect()
        screen_rect = QRectF(
            self.grid_to_screen(rect.topLeft()),
            self.grid_to_screen(rect.bottomRight())
        )
        
        # 根据是否有效设置颜色
        color = region.color
        if is_invalid:
            color = QColor(255, 0, 0, 100)  # 无效位置显示红色
        
        # 绘制半透明填充
        painter.fillRect(screen_rect, color)
        
        # 绘制边框
        painter.setPen(QPen(color.darker(150), 2))
        painter.drawRect(screen_rect)
        
        # 绘制区域名称
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, region.name.upper())
    
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
            # 将 QPointF 转换为 QPoint 进行运算
            delta = mouse_pos - QPoint(int(new_pos.x()), int(new_pos.y()))
            self.offset += delta
            
        elif event.key() == Qt.Key.Key_Minus:  # 减号键缩小
            # 记录鼠标位置对应的网格坐标
            old_pos = self.screen_to_grid(mouse_pos)
            self.zoom_out()
            # 调整偏移，使得鼠标下的网格点保持不变
            new_pos = self.grid_to_screen(old_pos)
            # 将 QPointF 转换为 QPoint 进行运算
            delta = mouse_pos - QPoint(int(new_pos.x()), int(new_pos.y()))
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
    
    def start_region_creation(self):
        """开始创建区域"""
        try:
            dialog = RegionSizeDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                size = dialog.get_size()
                # 创建新区域并放置在视图中心
                region = self.region_manager.create_region(size)
                center = self.rect().center()
                grid_pos = self.screen_to_grid(center)
                region.set_position(QPointF(grid_pos.x() - size/2, grid_pos.y() - size/2))
                self.dragging_region = region
                # 确保新创建的region是未放置状态
                self.dragging_region.is_placed = False
                self.setCursor(Qt.CursorShape.SizeAllCursor)
                self.update()
            else:
                # 如果用户取消了对话框，取消按钮选中状态
                if isinstance(self.parent(), QMainWindow):
                    self.parent().create_region_action.setChecked(False)
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))
            # 取消工具栏按钮的选中状态
            if isinstance(self.parent(), QMainWindow):
                self.parent().create_region_action.setChecked(False)
    
    def cancel_region_creation(self):
        """取消区域创建"""
        if self.dragging_region:
            name = self.dragging_region.name
            self.region_manager.remove_region(name)
            self.dragging_region = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
    
    def delete_region(self, name: str):
        """删除区域"""
        if name in self.region_manager.regions:
            # 如果正在拖动这个区域，取消拖动
            if self.dragging_region and self.dragging_region.name == name:
                self.dragging_region = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
            # 从管理器中删除区域
            self.region_manager.remove_region(name)
            self.update()