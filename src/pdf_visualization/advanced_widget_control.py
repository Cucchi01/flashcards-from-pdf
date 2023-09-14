from pdf_visualization.advanced_widget_layout import AdvancedOptionsLayout
from pdf_visualization.advanced_widget_model import AdvancedOptionsModel


class AdvancedOptionsControl:
    def __init__(
        self,
        advanced_options_layout: AdvancedOptionsLayout,
        advanced_options_model: AdvancedOptionsModel,
    ) -> None:
        self.__advanced_options_layout: AdvancedOptionsLayout = advanced_options_layout
        self.__advanced_options_model: AdvancedOptionsModel = advanced_options_model

        self.__set_buttons()

    def __set_buttons(self) -> None:
        self.__advanced_options_layout.get_shift_left_button_till_here().clicked.connect(
            self.__advanced_options_model.shift_left_flashcards_till_here
        )
        self.__advanced_options_layout.get_shift_right_button_till_here().clicked.connect(
            self.__advanced_options_model.shift_right_flashcards_till_here
        )
        self.__advanced_options_layout.get_shift_custom_button_till_here().clicked.connect(
            self.__advanced_options_model.shift_custom_button_till_here
        )

        self.__advanced_options_layout.get_shift_left_button_from_here().clicked.connect(
            self.__advanced_options_model.shift_left_flashcards_from_here
        )
        self.__advanced_options_layout.get_shift_right_button_from_here().clicked.connect(
            self.__advanced_options_model.shift_right_flashcards_from_here
        )
        self.__advanced_options_layout.get_shift_custom_button_from_here().clicked.connect(
            self.__advanced_options_model.shift_custom_button_from_here
        )
