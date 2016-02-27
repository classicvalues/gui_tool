#
# Copyright (C) 2016  UAVCAN Development Team  <uavcan.org>
#
# This software is distributed under the terms of the MIT License.
#
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

import uavcan
import datetime
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QHeaderView, QPushButton, QLabel
from PyQt5.QtCore import Qt
from logging import getLogger
from helpers import UAVCANStructInspector
from . import BasicTable, map_7bit_to_color, RealtimeLogWidget

logger = getLogger(__name__)


def log_level_to_color(level):
    return {
        level.DEBUG: None,
        level.INFO: Qt.green,
        level.WARNING: Qt.yellow,
        level.ERROR: Qt.red,
    }.get(level.value)


class LogMessageDisplayWidget(QGroupBox):
    COLUMNS = [
        BasicTable.Column('Node',
                          lambda e: (e.transfer.source_node_id, map_7bit_to_color(e.transfer.source_node_id))),
        BasicTable.Column('Local Time',
                          lambda e: datetime.datetime.fromtimestamp(e.transfer.ts_real)
                          .strftime('%H:%M:%S.%f')[:-3],
                          searchable=False),
        BasicTable.Column('Level',
                          lambda e: (UAVCANStructInspector(e.message.level).field_to_string('value'),
                                     log_level_to_color(e.message.level))),
        BasicTable.Column('Source',
                          lambda e: e.message.source),
        BasicTable.Column('Text',
                          lambda e: e.message.text,
                          resize_mode=QHeaderView.Stretch),
    ]

    def __init__(self, parent, node):
        super(LogMessageDisplayWidget, self).__init__(parent)
        self.setTitle('Log messages (uavcan.protocol.debug.LogMessage)')

        self._log_widget = RealtimeLogWidget(self, columns=self.COLUMNS, multi_line_rows=True, started_by_default=True)

        self._subscriber = node.add_handler(uavcan.protocol.debug.LogMessage, self._log_widget.add_item_async)

        layout = QVBoxLayout(self)
        layout.addWidget(self._log_widget, 1)
        self.setLayout(layout)

    def close(self):
        self._subscriber.remove()
