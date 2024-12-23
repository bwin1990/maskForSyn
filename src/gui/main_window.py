from PyQt6.QtWidgets import (QMainWindow, QToolBar, QPushButton, 
                            QStatusBar, QMessageBox, QDialog, QLabel)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .grid_view import GridView
from .grid_size_dialog import GridSizeDialog
from core.grid import Grid

class MainWindow(QMainWindow):
    def __init__(self, grid=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("点阵分割工具")
        
        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 添加新建点阵按钮
        new_grid_action = QAction("新建点阵", self)
        new_grid_action.triggered.connect(self._create_new_grid)
        toolbar.addAction(new_grid_action)
        
        toolbar.addSeparator()  # 添加分隔符
        
        # 添加缩放按钮
        zoom_in_action = QAction("放大", self)
        zoom_in_action.triggered.connect(self._zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(self._zoom_out)
        toolbar.addAction(zoom_out_action)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 添加永久显示的缩放比例标签
        self.zoom_label = QLabel("缩放: 1.00x")
        self.statusBar.addPermanentWidget(self.zoom_label)
        
        # 创建网格视图
        self.grid_view = GridView(self)
        self.setCentralWidget(self.grid_view)
        
        # 连接鼠标位置信号
        self.grid_view.mouse_position_changed.connect(self._update_status_bar)
        
        # 如果提供了grid，则加载它
        if grid:
            self.load_grid(grid)
            
        # 设置窗口默认大小
        self.resize(800, 600)
    
    def _update_status_bar(self, position_text):
        """更新状态栏显示的坐标"""
        if position_text.startswith("缩放:"):
            # 更新缩放比例标签
            self.zoom_label.setText(position_text)
        else:
            # 更新坐标信息
            self.statusBar.showMessage(f"坐标: {position_text}")
    
    def _zoom_in(self):
        self.grid_view.zoom_in()
    
    def _zoom_out(self):
        self.grid_view.zoom_out()
    
    def load_grid(self, grid):
        """加载点阵数据"""
        self.grid_view.grid = grid
        self.grid_view.update()
    
    def _create_new_grid(self):
        """创建新的点阵"""
        dialog = GridSizeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rows, cols = dialog.get_size()
            try:
                new_grid = Grid(rows, cols)
                self.load_grid(new_grid)
                self.statusBar.showMessage(f"已创建 {rows}×{cols} 的点阵", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"创建点阵失败: {str(e)}")