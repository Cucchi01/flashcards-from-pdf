from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence, QMouseEvent

from functools import partial

from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout


class PDFWindowVisualizationControl:
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        # change the CursorShape while loading the pdf
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__pdf_window_model: PDFWindowVisualizationModel = (
            PDFWindowVisualizationModel(path_of_pdf)
        )
        self.__pdf_window_layout: PDFWindowVisualizationLayout = (
            self.__pdf_window_model.get_pdf_window_visualization()
        )
        self.__set_controls_window_layout()
        QApplication.restoreOverrideCursor()

    def get_pdf_window_visualization_layout(self) -> PDFWindowVisualizationLayout:
        return self.__pdf_window_layout

    def __set_controls_window_layout(self) -> None:
        self.__set_controls_header_widget()
        self.__set_controls_left_panel_widget()
        self.__set_controls_right_panel_widget()
        self.__set_controls_bottom_widget()

    def __set_controls_header_widget(self) -> None:
        # header
        self.__pdf_window_layout.get_shuffle_button().clicked.connect(
            self.__pdf_window_model.shuffle_button_pressed
        )

        self.__set_controls_page_position_layout()

    def __set_controls_page_position_layout(self) -> None:
        self.__pdf_window_layout.get_pdf_page_num_spinbox().valueChanged.connect(
            self.__pdf_window_model.update_page_spinbox_change
        )

        self.__pdf_window_layout.get_previous_page_button().clicked.connect(
            self.__pdf_window_model.previous_page
        )
        self.__pdf_window_layout.get_next_page_button().clicked.connect(
            self.__pdf_window_model.next_page
        )

    def __set_controls_left_panel_widget(self) -> None:
        self.shortcut_zoom_increase = QShortcut(
            QKeySequence("Ctrl++"), self.__pdf_window_layout
        )
        self.shortcut_zoom_increase.activated.connect(
            self.__pdf_window_layout.increase_zoom
        )
        self.shortcut_zoom_decrease = QShortcut(
            QKeySequence("Ctrl+-"), self.__pdf_window_layout
        )
        self.shortcut_zoom_decrease.activated.connect(
            self.__pdf_window_layout.decrease_zoom
        )
        self.__pdf_window_layout.get_flashcard_label().set_method_to_call(
            self.__pdf_window_model.modify_current_flashcard
        )

    def __set_controls_right_panel_widget(self) -> None:
        self.__set_controls_flashcard_button_layout()

    def __set_controls_flashcard_button_layout(self) -> None:
        self.__pdf_window_layout.get_page_flashcard_button().clicked.connect(
            partial(self.__pdf_window_model.add_page_flashcard, flag_generic=False)
        )
        self.__pdf_window_layout.get_generic_flashcard_button().clicked.connect(
            partial(self.__pdf_window_model.add_page_flashcard, flag_generic=True)
        )
        self.__pdf_window_layout.get_remove_flashcard_button().clicked.connect(
            self.__pdf_window_model.remove_current_flashcard
        )

    def __set_controls_bottom_widget(self) -> None:
        # bottom
        self.__set_controls_current_card_bottom_layout()
        self.__set_controls_current_flashcard_bottom_layout()

    def __set_controls_current_card_bottom_layout(self) -> None:
        self.__pdf_window_layout.get_previous_card_button().clicked.connect(
            self.__pdf_window_model.previous_card
        )
        self.__pdf_window_layout.get_next_card_button().clicked.connect(
            self.__pdf_window_model.next_card
        )

    def __set_controls_current_flashcard_bottom_layout(self) -> None:
        # TODO: manage correct and mistake answers
        self.__pdf_window_layout.get_previous_flashcard_button().clicked.connect(
            self.__pdf_window_model.previous_flashcard
        )

        self.__pdf_window_layout.get_next_flashcard_button().clicked.connect(
            self.__pdf_window_model.next_flashcard
        )
        pass
