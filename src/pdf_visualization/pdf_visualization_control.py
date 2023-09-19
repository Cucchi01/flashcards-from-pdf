from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence

from functools import partial

from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout


class PDFWindowVisualizationControl:
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        self.__shortcut_spin_box_focus: QShortcut
        self.__shortcut_previous_page: QShortcut
        self.__shortcut_next_page: QShortcut
        self.__shortcut_zoom_increase: QShortcut
        self.__shortcut_zoom_decrease: QShortcut
        self.__shortcut_modify_current_flashcard: QShortcut
        self.__shortcut_focus_question_field: QShortcut
        self.__shortcut_manage_page_button_flashcard: QShortcut
        self.__shortcut_manage_generic_button_flashcard: QShortcut
        self.__shortcut_delete_current_flashcard: QShortcut
        self.__shortcut_cancel_current_flashcard_modification: QShortcut
        self.__shortcut_previous_card: QShortcut
        self.__shortcut_next_card: QShortcut
        self.__shortcut_previous_flashcard: QShortcut
        self.__shortcut_next_flashcard: QShortcut
        self.__shortcut_know: QShortcut
        self.__shortcut_stil_learning: QShortcut

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
        self.__pdf_window_layout.get_restart_test_button().clicked.connect(
            self.__pdf_window_model.restart_test_pressed
        )

        self.__pdf_window_layout.get_advanced_options_button().clicked.connect(
            self.__pdf_window_model.advanced_options_button_pressed
        )

        self.__set_controls_page_position_layout()

    def __set_controls_page_position_layout(self) -> None:
        self.__pdf_window_layout.get_pdf_page_num_spinbox().valueChanged.connect(
            self.__pdf_window_model.update_page_spinbox_change
        )

        self.__shortcut_spin_box_focus = QShortcut(
            QKeySequence("Ctrl+G"), self.__pdf_window_layout
        )
        self.__shortcut_spin_box_focus.activated.connect(
            self.__pdf_window_model.focus_spinbox
        )

        self.__pdf_window_layout.get_previous_page_button().clicked.connect(
            self.__pdf_window_model.previous_page
        )
        self.__shortcut_previous_page = QShortcut(
            QKeySequence("Up"), self.__pdf_window_layout
        )
        self.__shortcut_previous_page.activated.connect(
            self.__pdf_window_model.previous_page
        )
        self.__pdf_window_layout.get_next_page_button().clicked.connect(
            self.__pdf_window_model.next_page
        )
        self.__shortcut_next_page = QShortcut(
            QKeySequence("Down"), self.__pdf_window_layout
        )
        self.__shortcut_next_page.activated.connect(self.__pdf_window_model.next_page)

    def __set_controls_left_panel_widget(self) -> None:
        self.__shortcut_zoom_increase = QShortcut(
            QKeySequence("Ctrl++"), self.__pdf_window_layout
        )
        self.__shortcut_zoom_increase.activated.connect(
            self.__pdf_window_layout.increase_zoom
        )
        self.__shortcut_zoom_decrease = QShortcut(
            QKeySequence("Ctrl+-"), self.__pdf_window_layout
        )
        self.__shortcut_zoom_decrease.activated.connect(
            self.__pdf_window_layout.decrease_zoom
        )
        self.__pdf_window_layout.get_flashcard_label().set_method_to_call(
            self.__pdf_window_model.modify_current_flashcard
        )
        self.__shortcut_modify_current_flashcard = QShortcut(
            QKeySequence("Ctrl+E"), self.__pdf_window_layout
        )
        self.__shortcut_modify_current_flashcard.activated.connect(
            self.__pdf_window_model.modify_current_flashcard
        )
        self.__shortcut_focus_question_field = QShortcut(
            QKeySequence("Ctrl+A"), self.__pdf_window_layout
        )
        self.__shortcut_focus_question_field.activated.connect(
            self.__pdf_window_model.focus_question_field
        )

    def __set_controls_right_panel_widget(self) -> None:
        self.__set_controls_flashcard_button_layout()

    def __set_controls_flashcard_button_layout(self) -> None:
        self.__pdf_window_layout.get_page_flashcard_button().clicked.connect(
            partial(
                self.__pdf_window_model.manage_page_button_flashcard, flag_generic=False
            )
        )
        self.__shortcut_manage_page_button_flashcard = QShortcut(
            QKeySequence("Ctrl+S"), self.__pdf_window_layout
        )
        self.__shortcut_manage_page_button_flashcard.activated.connect(
            partial(
                self.__pdf_window_model.manage_page_button_flashcard, flag_generic=False
            )
        )

        self.__pdf_window_layout.get_generic_flashcard_button().clicked.connect(
            partial(
                self.__pdf_window_model.manage_page_button_flashcard, flag_generic=True
            )
        )
        self.__shortcut_manage_generic_button_flashcard = QShortcut(
            QKeySequence("Ctrl+Shift+S"), self.__pdf_window_layout
        )
        self.__shortcut_manage_generic_button_flashcard.activated.connect(
            partial(
                self.__pdf_window_model.manage_page_button_flashcard, flag_generic=True
            )
        )

        self.__pdf_window_layout.get_remove_flashcard_button().clicked.connect(
            self.__pdf_window_model.remove_current_flashcard
        )

        self.__shortcut_delete_current_flashcard = QShortcut(
            QKeySequence("Ctrl+D"), self.__pdf_window_layout
        )
        self.__shortcut_delete_current_flashcard.activated.connect(
            self.__pdf_window_model.remove_current_flashcard
        )

        self.__pdf_window_layout.get_cancel_modification_flashcard_button().clicked.connect(
            self.__pdf_window_model.cancel_current_flashcard_modification
        )

        self.__shortcut_cancel_current_flashcard_modification = QShortcut(
            QKeySequence("Ctrl+R"), self.__pdf_window_layout
        )
        self.__shortcut_cancel_current_flashcard_modification.activated.connect(
            self.__pdf_window_model.cancel_current_flashcard_modification
        )

    def __set_controls_bottom_widget(self) -> None:
        # bottom
        self.__set_controls_current_card_bottom_layout()
        self.__set_controls_current_flashcard_bottom_layout()

    def __set_controls_current_card_bottom_layout(self) -> None:
        self.__pdf_window_layout.get_previous_card_button().clicked.connect(
            self.__pdf_window_model.previous_card
        )

        self.__shortcut_previous_card = QShortcut(
            QKeySequence("Left"), self.__pdf_window_layout
        )
        self.__shortcut_previous_card.activated.connect(
            self.__pdf_window_model.previous_card
        )

        self.__pdf_window_layout.get_next_card_button().clicked.connect(
            self.__pdf_window_model.next_card
        )

        self.__shortcut_next_card = QShortcut(
            QKeySequence("Right"), self.__pdf_window_layout
        )
        self.__shortcut_next_card.activated.connect(self.__pdf_window_model.next_card)

    def __set_controls_current_flashcard_bottom_layout(self) -> None:
        self.__pdf_window_layout.get_previous_flashcard_button().clicked.connect(
            self.__pdf_window_model.previous_flashcard
        )

        self.__shortcut_previous_flashcard = QShortcut(
            QKeySequence("Ctrl+Left"), self.__pdf_window_layout
        )
        self.__shortcut_previous_flashcard.activated.connect(
            self.__pdf_window_model.previous_flashcard
        )

        self.__pdf_window_layout.get_next_flashcard_button().clicked.connect(
            self.__pdf_window_model.next_flashcard
        )

        self.__shortcut_next_flashcard = QShortcut(
            QKeySequence("Ctrl+Right"), self.__pdf_window_layout
        )
        self.__shortcut_next_flashcard.activated.connect(
            self.__pdf_window_model.next_flashcard
        )

        self.__pdf_window_layout.get_still_learning_button().clicked.connect(
            self.__pdf_window_model.get_test_manager().still_learning_answer
        )
        self.__shortcut_stil_learning = QShortcut(
            QKeySequence("1"), self.__pdf_window_layout
        )
        self.__shortcut_stil_learning.activated.connect(
            self.__pdf_window_model.get_test_manager().still_learning_answer
        )

        self.__pdf_window_layout.get_know_button().clicked.connect(
            self.__pdf_window_model.get_test_manager().know_answer
        )
        self.__shortcut_know = QShortcut(QKeySequence("2"), self.__pdf_window_layout)
        self.__shortcut_know.activated.connect(
            self.__pdf_window_model.get_test_manager().know_answer
        )
