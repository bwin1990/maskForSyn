from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt

class RegionControlPanel(QWidget):
    """分割框控制面板"""
    region_selected = pyqtSignal(str)  # 发送选中的区域名称
    region_deleted = pyqtSignal(str)   # 发送要删除的区域名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        
        # 添加标题
        title = QLabel("分割框控制")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建容器widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(2, 2, 2, 2)  # 减少边距
        self.container_layout.setSpacing(2)  # 减少间距
        self.container.setLayout(self.container_layout)
        
        # 将容器放入滚动区域
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        self.setFixedWidth(150)  # 固定宽度
        
        # 存储按钮字典
        self.region_buttons = {}
    
    def add_region(self, name: str):
        """添加新的区域按钮"""
        if name in self.region_buttons:
            return
            
        # 创建按钮组
        button_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 区域选择按钮
        select_btn = QPushButton(name.upper())
        select_btn.setFixedHeight(30)
        select_btn.clicked.connect(lambda: self.region_selected.emit(name))
        
        # 删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_region(name))
        
        layout.addWidget(select_btn)
        layout.addWidget(delete_btn)
        button_widget.setLayout(layout)
        
        # 保存按钮引用
        self.region_buttons[name] = button_widget
        
        # 添加到容器
        self.container_layout.addWidget(button_widget)
    
    def delete_region(self, name: str):
        """删除区域按钮"""
        if name in self.region_buttons:
            # 移除按钮组件
            button_widget = self.region_buttons[name]
            self.container_layout.removeWidget(button_widget)
            button_widget.deleteLater()
            del self.region_buttons[name]
            # 发送删除信号
            self.region_deleted.emit(name)
    
    def clear(self):
        """清除所有按钮"""
        for button_widget in self.region_buttons.values():
            button_widget.deleteLater()
        self.region_buttons.clear() 