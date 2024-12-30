from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QPushButton)

class RegionSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置分割区域大小")
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 宽度输入
        width_layout = QHBoxLayout()
        width_label = QLabel("宽度:")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 100)  # 设置合理的范围
        self.width_spinbox.setValue(10)  # 默认宽度
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_spinbox)
        
        # 高度输入
        height_layout = QHBoxLayout()
        height_label = QLabel("高度:")
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 100)  # 设置合理的范围
        self.height_spinbox.setValue(10)  # 默认高度
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_spinbox)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加到主布局
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
    
    def get_size(self):
        """获取设置的宽度和高度"""
        return (self.width_spinbox.value(), self.height_spinbox.value()) 