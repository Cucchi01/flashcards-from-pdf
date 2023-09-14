from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
)


class AdvancedOptionsLayout(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Advanced Options")

        self.__window_layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.__window_layout)

        self.__info_label_left: QLabel
        self.__shift_left_button_till_here: QPushButton
        self.__shift_right_button_till_here: QPushButton
        self.__shift_custom_layout_till_here: QHBoxLayout = QHBoxLayout()
        self.__shift_custom_button_till_here: QPushButton
        self.__shift_custom_spinbox_till_here: QSpinBox

        self.__info_label_right: QLabel
        self.__shift_left_button_from_here: QPushButton
        self.__shift_right_button_from_here: QPushButton
        self.__shift_custom_layout_from_here: QHBoxLayout = QHBoxLayout()
        self.__shift_custom_button_from_here: QPushButton
        self.__shift_custom_spinbox_from_here: QSpinBox

        self.__set_layout()

    def __set_layout(self) -> None:
        self.__set_till_here_actions()
        self.__set_from_here_actions()

    def __set_till_here_actions(self) -> None:
        self.__info_label_left = QLabel("These actions modify till this card")
        self.__shift_left_button_till_here = QPushButton(
            "Shift flashcards one page left"
        )
        self.__shift_right_button_till_here = QPushButton(
            "Shift flashcards one page right"
        )

        self.__shift_custom_button_till_here = QPushButton("Shift custom till here")
        self.__shift_custom_spinbox_till_here = QSpinBox()
        self.__shift_custom_spinbox_till_here.setMinimum(-1000)
        self.__shift_custom_spinbox_till_here.setMaximum(1000)

        self.__shift_custom_layout_till_here.addWidget(
            self.__shift_custom_button_till_here
        )
        self.__shift_custom_layout_till_here.addWidget(
            self.__shift_custom_spinbox_till_here
        )

        self.__window_layout.addWidget(self.__info_label_left)
        self.__window_layout.addWidget(self.__shift_left_button_till_here)
        self.__window_layout.addWidget(self.__shift_right_button_till_here)
        self.__window_layout.addLayout(self.__shift_custom_layout_till_here)

    def __set_from_here_actions(self) -> None:
        self.__info_label_right = QLabel("These actions modify from this card on")
        self.__shift_left_button_from_here = QPushButton(
            "Shift flashcards one page left"
        )
        self.__shift_right_button_from_here = QPushButton(
            "Shift flashcards one page right"
        )

        self.__shift_custom_button_from_here = QPushButton("Shift custom from here")
        self.__shift_custom_spinbox_from_here = QSpinBox()
        self.__shift_custom_spinbox_from_here.setMinimum(-1000)
        self.__shift_custom_spinbox_from_here.setMaximum(1000)

        self.__shift_custom_layout_from_here.addWidget(
            self.__shift_custom_button_from_here
        )
        self.__shift_custom_layout_from_here.addWidget(
            self.__shift_custom_spinbox_from_here
        )

        self.__window_layout.addWidget(self.__info_label_right)
        self.__window_layout.addWidget(self.__shift_left_button_from_here)
        self.__window_layout.addWidget(self.__shift_right_button_from_here)
        self.__window_layout.addLayout(self.__shift_custom_layout_from_here)

    def get_shift_left_button_till_here(self) -> QPushButton:
        return self.__shift_left_button_till_here

    def get_shift_right_button_till_here(self) -> QPushButton:
        return self.__shift_right_button_till_here

    def get_shift_custom_button_till_here(self) -> QPushButton:
        return self.__shift_custom_button_till_here

    def get_shift_custom_spinbox_till_here(self) -> QSpinBox:
        return self.__shift_custom_spinbox_till_here

    def get_shift_left_button_from_here(self) -> QPushButton:
        return self.__shift_left_button_from_here

    def get_shift_right_button_from_here(self) -> QPushButton:
        return self.__shift_right_button_from_here

    def get_shift_custom_button_from_here(self) -> QPushButton:
        return self.__shift_custom_button_from_here

    def get_shift_custom_spinbox_from_here(self) -> QSpinBox:
        return self.__shift_custom_spinbox_from_here
