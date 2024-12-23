from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QPushButton)

class GridSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置点阵大小")
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 行数输入
        row_layout = QHBoxLayout()
        row_label = QLabel("行数:")
        self.row_spinbox = QSpinBox()
        self.row_spinbox.setRange(1, 1000)  # 设置范围
        self.row_spinbox.setValue(318)  # 默认23k芯片的行数
        row_layout.addWidget(row_label)
        row_layout.addWidget(self.row_spinbox)
        
        # 列数输入
        col_layout = QHBoxLayout()
        col_label = QLabel("列数:")
        self.col_spinbox = QSpinBox()
        self.col_spinbox.setRange(1, 1000)
        self.col_spinbox.setValue(74)  # 默认23k芯片的列数
        col_layout.addWidget(col_label)
        col_layout.addWidget(self.col_spinbox)
        
        # 预设按钮
        preset_layout = QHBoxLayout()
        btn_23k = QPushButton("23k (318×74)")
        btn_680k = QPushButton("680k (1000×680)")
        preset_layout.addWidget(btn_23k)
        preset_layout.addWidget(btn_680k)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加到主布局
        layout.addLayout(row_layout)
        layout.addLayout(col_layout)
        layout.addLayout(preset_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        btn_23k.clicked.connect(lambda: self.set_preset(318, 74))
        btn_680k.clicked.connect(lambda: self.set_preset(1000, 680))
    
    def set_preset(self, rows, cols):
        """设置预设值"""
        self.row_spinbox.setValue(rows)
        self.col_spinbox.setValue(cols)
    
    def get_size(self):
        """获取设置的大小"""
        return (self.row_spinbox.value(), self.col_spinbox.value()) 