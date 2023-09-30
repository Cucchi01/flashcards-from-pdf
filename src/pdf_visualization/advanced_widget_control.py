# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
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
