from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QPointF
from core.region_manager import RegionManager
from core.region import Region

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
        
        self.region_manager = RegionManager()
        self.current_region = None  # 当前正在绘制的区域
        
        # 添加区域创建相关的状态
        self.is_creating_region = False
        self.current_region = None
    
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
            
            # 如果正在创建区域，显示当前区域信息
            if self.is_creating_region and self.current_region:
                position_text += f" - 区域 {self.current_region.name.upper()}"
                position_text += f" ({len(self.current_region.points)} 个点)"
        else:
            position_text = "(-,-)"
            
        # 发送坐标变化信号
        self.mouse_position_changed.emit(position_text)
    
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
        
        # 绘制区域
        if cell_size > 2:  # 只在足够大时绘制区域
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 添加抗锯齿
            
            # 先绘制已完成的区域
            for name, region in self.region_manager.regions.items():
                if region.is_closed:
                    self._draw_region(painter, region)
            
            # 绘制正在创建的区域
            if self.is_creating_region and self.current_region:
                self._draw_region(painter, self.current_region, True)
    
    def _draw_region(self, painter: QPainter, region: Region, is_creating: bool = False):
        """绘制单个区域"""
        if len(region.points) == 0:
            return
            
        # 创建路径
        path = QPainterPath()
        first_point = self.grid_to_screen(region.points[0])
        path.moveTo(first_point)
        
        # 计算区域中心点
        sum_x = sum(point.x() for point in region.points)
        sum_y = sum(point.y() for point in region.points)
        center = QPointF(sum_x / len(region.points), sum_y / len(region.points))
        center_screen = self.grid_to_screen(center)
        
        # 添加所有点
        for point in region.points[1:]:
            screen_point = self.grid_to_screen(point)
            path.lineTo(screen_point)
        
        # 如果区域已关闭或正在创建，连接到鼠标位置
        if region.is_closed:
            path.closeSubpath()
        elif is_creating:
            # 连接到鼠标当前位置
            mouse_pos = QPointF(self.mapFromGlobal(self.cursor().pos()))
            path.lineTo(mouse_pos)
            if len(region.points) >= 3:
                # 显示可能的闭合路径
                path.lineTo(first_point)
        
        # 绘制填充
        painter.fillPath(path, region.color)
        
        # 绘制边框
        pen = QPen(region.color.darker(150), 2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 绘制顶点
        vertex_pen = QPen(Qt.GlobalColor.white, 1)
        vertex_brush = QBrush(region.color.darker(150))
        painter.setPen(vertex_pen)
        painter.setBrush(vertex_brush)
        for point in region.points:
            screen_point = self.grid_to_screen(point)
            painter.drawEllipse(screen_point, 4, 4)
        
        # 只在区域完成时才在中心绘制区域名称
        if region.is_closed:
            # 设置文本样式
            font = painter.font()
            font.setBold(True)  # 加粗
            font.setPointSize(12)  # 设置字体大小
            painter.setFont(font)
            
            # 计算文本矩形
            text = region.name.upper()
            text_rect = painter.fontMetrics().boundingRect(text)
            
            # 计算文本位置（居中）
            text_point = QPoint(
                int(center_screen.x() - text_rect.width() / 2),
                int(center_screen.y() + text_rect.height() / 2)
            )
            
            # 绘制白色背景（可选）
            background_rect = text_rect.translated(text_point)
            background_rect.adjust(-2, -2, 2, 2)  # 稍微扩大背景区域
            painter.fillRect(background_rect, Qt.GlobalColor.white)
            
            # 绘制文本
            painter.setPen(region.color.darker(150))
            painter.drawText(text_point, text)
    
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
    
    def start_region_creation(self):
        """开始创建区域"""
        self.is_creating_region = True
        self.current_region = None  # 等待第一次点击时创建
        self.setCursor(Qt.CursorShape.CrossCursor)  # 改变鼠标样式
    
    def cancel_region_creation(self):
        """取消区域创建"""
        if self.is_creating_region:
            self.is_creating_region = False
            self.current_region = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()