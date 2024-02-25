from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QDialog, QLabel, QLineEdit, QRadioButton, QHBoxLayout
from PySide6.QtGui import QIntValidator

LineEdit = 0
RadioButton = 1


class settings(QDialog):
    def __init__(self, title: str, x: int, y: int, w: int, h: int, args: tuple):
        super().__init__()

        self.setWindowTitle(title)
        self.setGeometry(x, y, w, h)
        layout = QVBoxLayout()

        self.labels = []
        self.lineEdits = []
        self.radio_groups = []

        for arg in args:
            if arg[0] == LineEdit:
                label = QLabel(arg[1] + ":")
                layout.addWidget(label)
                self.labels.append(label)

                lineEdit = QLineEdit(str(arg[2]))
                lineEdit.setValidator(QIntValidator(arg[3], arg[4]))
                layout.addWidget(lineEdit)
                self.lineEdits.append(lineEdit)
            elif arg[0] == RadioButton:
                tmp = []
                label = QLabel(arg[1] + ":")
                layout.addWidget(label)
                self.labels.append(label)

                radio_group = QHBoxLayout()
                for i in range(arg[2]):
                    radio = QRadioButton(str(arg[i + 3]))
                    if not i:
                        radio.setChecked(True)
                    radio_group.addWidget(radio)
                    tmp.append(radio)
                self.radio_groups.append([radio_group, tmp])
                layout.addLayout(radio_group)

        button = QPushButton("OK")
        button.clicked.connect(self.on_ok_clicked)
        layout.addWidget(button)

        self.setLayout(layout)

    def on_ok_clicked(self):
        for lineEdit in self.lineEdits:
            if lineEdit.text() == "":
                QMessageBox.warning(self, "Warning", "Please enter a setting value.")
                return
        self.accept()

    def get_settings(self):
        res = [int(lineEdit.text()) for lineEdit in self.lineEdits]

        for radio_children in self.radio_groups:
            check = 0
            for radio in radio_children[1]:
                if radio.isChecked():
                    res.append(int(radio.text()))
                    check += 1
            assert check == 1
        return res
