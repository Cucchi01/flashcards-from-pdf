# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QModelIndex

import pandas as pd

GRADIENT_BACKGROUND: list[list[int]] = [
    [237, 248, 251],
    [237, 248, 251],
    [204, 236, 230],
    [204, 236, 230],
    [153, 216, 201],
    [153, 216, 201],
    [102, 194, 164],
    [102, 194, 164],
    [65, 174, 118],
    [65, 174, 118],
    [35, 139, 69],
    [35, 139, 69],
    [0, 88, 36],
    [0, 88, 36],
    [0, 88, 36],
]


class HeatmapModel(QtCore.QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super(HeatmapModel, self).__init__()
        self.__data = data

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.__data.iloc[index.row(), index.column()]
            return str(value)
        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.__define_color(index)
        elif role == Qt.ItemDataRole.ForegroundRole:
            return self.__define_color(index)

    def __define_color(
        self,
        index: QModelIndex,
    ) -> QtGui.QColor:
        value = self.__data.iloc[index.row(), index.column()]
        if isinstance(value, int) or isinstance(value, float):
            value_int: int = int(round(value, 0))

            value_int = value_int if value_int >= 0 else 0
            value_int = value_int if value_int <= 14 else 14
            r: int = GRADIENT_BACKGROUND[value_int][0]
            g: int = GRADIENT_BACKGROUND[value_int][1]
            b: int = GRADIENT_BACKGROUND[value_int][2]
            return QtGui.QColor.fromRgb(r, g, b)

        return QtGui.QColor.fromRgb(0, 0, 0)

    def rowCount(self, index):
        return self.__data.shape[0]

    def columnCount(self, index):
        return self.__data.shape[1]

    # def headerData(self, section, orientation, role):
    #     # section is the index of the column/row.
    #     if role == Qt.ItemDataRole.DisplayRole:
    #         if orientation == Qt.Orientation.Horizontal:
    #             return str(self.__data.columns[section])

    #         if orientation == Qt.Orientation.Vertical:
    #             return str(self.__data.index[section])
