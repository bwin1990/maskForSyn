from PyQt6.QtWidgets import (QMainWindow, QToolBar, QPushButton, 
                            QStatusBar, QMessageBox, QDialog, QLabel, QHBoxLayout, QWidget, QSizePolicy,
                            QFileDialog)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from gui.grid_view import GridView
from gui.grid_size_dialog import GridSizeDialog
from core.grid import Grid
from .region_control_panel import RegionControlPanel

class MainWindow(QMainWindow):
    def __init__(self, grid=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("点阵分割工具")
        
        # 创建工具栏
        toolbar = self._create_toolbar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 添加永久显示的缩放比例标签
        self.zoom_label = QLabel("缩放: 1.00x")
        self.statusBar.addPermanentWidget(self.zoom_label)
        
        # 创建主窗口的中心部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建水平布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # 减少边距
        main_widget.setLayout(main_layout)
        
        # 创建并添加GridView
        self.grid_view = GridView(self)
        self.grid_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # 允许GridView扩展
        main_layout.addWidget(self.grid_view)
        
        # 创建并添加RegionControlPanel
        self.region_panel = RegionControlPanel()
        self.region_panel.setFixedWidth(150)  # 固定控制面板宽度
        main_layout.addWidget(self.region_panel)
        
        # 连接信号
        self.grid_view.region_manager.region_added.connect(self.region_panel.add_region)
        self.grid_view.region_manager.region_removed.connect(self.region_panel.remove_region)
        self.region_panel.region_deleted.connect(self.delete_region)
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
    
    def _toggle_region_creation(self, checked: bool):
        """切换区域创建模式"""
        if checked:
            try:
                self.grid_view.start_region_creation()
            except ValueError as e:
                QMessageBox.warning(self, "错误", str(e))
                self.create_region_action.setChecked(False)
        else:
            self.grid_view.cancel_region_creation()
    
    def delete_region(self, name: str):
        """删除区域"""
        self.grid_view.delete_region(name)
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 新建点阵按钮
        new_grid_action = QAction("新建点阵", self)
        new_grid_action.triggered.connect(self._create_new_grid)
        toolbar.addAction(new_grid_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 创建分割框按钮
        self.create_region_action = QAction("创建分割框", self)
        self.create_region_action.setCheckable(True)
        self.create_region_action.toggled.connect(self._toggle_region_creation)
        toolbar.addAction(self.create_region_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 导出Mask按钮
        export_mask_action = QAction("导出Mask", self)
        export_mask_action.triggered.connect(self._export_mask)
        toolbar.addAction(export_mask_action)
        
        return toolbar
    
    def _export_mask(self):
        """导出mask文件"""
        # 获取保存文件的路径
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存Mask文件",
            "mask.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                # 调用grid的导出方法
                self.grid_view.grid.export_mask(
                    self.grid_view.region_manager.regions,
                    filename
                )
                self.statusBar.showMessage(f"Mask已成功导出到: {filename}", 3000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出Mask文件失败: {str(e)}")