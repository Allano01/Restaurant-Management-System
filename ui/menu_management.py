from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QMessageBox, QHeaderView, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from services.menu_service import (
    get_all_menu_items, get_all_categories, add_menu_item,
    update_menu_item, delete_menu_item, toggle_item_availability
)
from assets.styles import COLORS, primary_button, icon_button


class MenuItemDialog(QDialog):
    def __init__(self, parent=None, item=None, categories=None):
        super().__init__(parent)
        self.item = item
        self.categories = categories or []
        self.setWindowTitle("Edit Item" if item else "Add New Item")
        self.setFixedSize(440, 380)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                font-family: Segoe UI;
                background: transparent;
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Header
        header = QVBoxLayout()
        title = QLabel("Edit Menu Item" if self.item else "Add New Menu Item")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        subtitle = QLabel("Fill in the details below to save the item")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        header.addWidget(title)
        header.addWidget(subtitle)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Grilled Chicken")
        self.name_input.setFixedHeight(38)

        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(38)
        for cat in self.categories:
            self.category_combo.addItem(cat[1], cat[0])

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g. 15.00")
        self.price_input.setFixedHeight(38)

        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("e.g. 6.00  (optional)")
        self.cost_input.setFixedHeight(38)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Short description  (optional)")
        self.desc_input.setFixedHeight(38)

        for label_text, widget in [
            ("Item Name *",  self.name_input),
            ("Category *",   self.category_combo),
            ("Selling Price *", self.price_input),
            ("Cost Price",   self.cost_input),
            ("Description",  self.desc_input),
        ]:
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            form.addRow(lbl, widget)

        if self.item:
            self.name_input.setText(self.item[1])
            self.price_input.setText(str(self.item[3]))
            self.cost_input.setText(str(self.item[4]) if self.item[4] else "")
            self.desc_input.setText(self.item[5] if self.item[5] else "")
            for i in range(self.category_combo.count()):
                if self.category_combo.itemText(i) == self.item[2]:
                    self.category_combo.setCurrentIndex(i)
                    break

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Item")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(primary_button())
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout.addLayout(header)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def save(self):
        name      = self.name_input.text().strip()
        cat_id    = self.category_combo.currentData()
        price_str = self.price_input.text().strip()
        cost_str  = self.cost_input.text().strip()
        desc      = self.desc_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation", "Item name is required.")
            return
        try:
            price = float(price_str)
        except ValueError:
            QMessageBox.warning(self, "Validation", "Please enter a valid price.")
            return
        try:
            cost = float(cost_str) if cost_str else None
        except ValueError:
            QMessageBox.warning(self, "Validation", "Please enter a valid cost price.")
            return

        self.result_data = {
            "category_id": cat_id,
            "item_name":   name,
            "description": desc,
            "price":       price,
            "cost_price":  cost,
        }
        self.accept()


class MenuManagementWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user       = user
        self.menu_items = []
        self.categories = []
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # ── Page header ───────────────────────────────────────
        header_row = QHBoxLayout()

        title_col = QVBoxLayout()
        page_title = QLabel("Menu Management")
        page_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        page_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        page_subtitle = QLabel("Add, edit, and manage your restaurant menu items")
        page_subtitle.setFont(QFont("Segoe UI", 11))
        page_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        title_col.addWidget(page_title)
        title_col.addWidget(page_subtitle)

        add_btn = QPushButton("＋  Add Menu Item")
        add_btn.setFixedHeight(42)
        add_btn.setFixedWidth(160)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button(COLORS['accent']))
        add_btn.clicked.connect(self.add_item)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(add_btn)

        # ── Stats bar ─────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        self.stat_cards_widgets = []

        # ── Search bar ────────────────────────────────────────
        search_frame = QFrame()
        search_frame.setFixedHeight(52)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 0, 16, 0)

        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI", 14))
        search_icon.setStyleSheet("background: transparent; border: none;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search menu items...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
        """)
        self.search_input.textChanged.connect(self.filter_table)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "ITEM NAME", "CATEGORY", "PRICE", "COST", "STATUS", "ACTIONS"
        ])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 12px;
                gridline-color: {COLORS['border']};
                font-family: Segoe UI;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_muted']};
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: bold;
                font-size: 11px;
                font-family: Segoe UI;
                letter-spacing: 1px;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_primary']};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border']};
                border-radius: 3px;
            }}
        """)

        # Column widths
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 130)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)

        # Shadow on table
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.table.setGraphicsEffect(shadow)

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addWidget(search_frame)
        layout.addWidget(self.table)

    def build_stat_pill(self, label, value, color):
        frame = QFrame()
        frame.setFixedHeight(40)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {color};
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 0, 16, 0)

        val_lbl = QLabel(str(value))
        val_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")

        txt_lbl = QLabel(label)
        txt_lbl.setFont(QFont("Segoe UI", 11))
        txt_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none;")

        row.addWidget(val_lbl)
        row.addWidget(txt_lbl)
        row.addStretch()
        return frame

    def load_data(self):
        self.categories = get_all_categories()
        self.menu_items = get_all_menu_items()

        # Clear and rebuild stats
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total     = len(self.menu_items)
        available = sum(1 for i in self.menu_items if i[6])
        unavail   = total - available

        for label, value, color in [
            ("Total Items",   total,     COLORS['accent']),
            ("Available",     available, COLORS['success']),
            ("Unavailable",   unavail,   COLORS['danger']),
            ("Categories",    len(self.categories), COLORS['warning']),
        ]:
            self.stats_row.addWidget(self.build_stat_pill(label, value, color))
        self.stats_row.addStretch()

        self.populate_table(self.menu_items)

    def populate_table(self, items):
        self.table.setRowCount(0)
        self.table.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            self.table.setRowHeight(row_idx, 52)

            # ID
            id_item = QTableWidgetItem(str(item[0]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setForeground(QColor(COLORS['text_muted']))
            self.table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(item[1])
            name_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            name_item.setForeground(QColor(COLORS['text_primary']))
            self.table.setItem(row_idx, 1, name_item)

            # Category
            cat_item = QTableWidgetItem(item[2])
            cat_item.setForeground(QColor(COLORS['text_secondary']))
            self.table.setItem(row_idx, 2, cat_item)

            # Price
            price_item = QTableWidgetItem(f"${item[3]:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            price_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            price_item.setForeground(QColor(COLORS['success']))
            self.table.setItem(row_idx, 3, price_item)

            # Cost
            cost_val = f"${item[4]:.2f}" if item[4] else "—"
            cost_item = QTableWidgetItem(cost_val)
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cost_item.setForeground(QColor(COLORS['text_muted']))
            self.table.setItem(row_idx, 4, cost_item)

            # Status badge
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 0, 8, 0)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            badge = QLabel("● Available" if item[6] else "● Unavailable")
            badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(26)
            badge.setStyleSheet(f"""
                color: {'#10b981' if item[6] else '#ef4444'};
                background-color: {'rgba(16,185,129,0.12)' if item[6] else 'rgba(239,68,68,0.12)'};
                border-radius: 12px;
                padding: 0 10px;
                font-size: 11px;
            """)
            status_layout.addWidget(badge)
            self.table.setCellWidget(row_idx, 5, status_widget)

            # Action buttons
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(6, 0, 6, 0)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(34, 34)
            edit_btn.setToolTip("Edit item")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet(icon_button(COLORS['accent']))
            edit_btn.clicked.connect(lambda _, i=item: self.edit_item(i))

            toggle_color = COLORS['warning'] if item[6] else COLORS['success']
            toggle_tip   = "Disable item" if item[6] else "Enable item"
            toggle_btn   = QPushButton("🔄")
            toggle_btn.setFixedSize(34, 34)
            toggle_btn.setToolTip(toggle_tip)
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.setStyleSheet(icon_button(toggle_color))
            toggle_btn.clicked.connect(
                lambda _, iid=item[0], s=item[6]: self.toggle_item(iid, s)
            )

            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(34, 34)
            delete_btn.setToolTip("Delete item")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet(icon_button(COLORS['danger']))
            delete_btn.clicked.connect(lambda _, iid=item[0]: self.delete_item(iid))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(toggle_btn)
            action_layout.addWidget(delete_btn)
            self.table.setCellWidget(row_idx, 6, action_widget)

    def filter_table(self, text):
        filtered = [
            item for item in self.menu_items
            if text.lower() in item[1].lower() or text.lower() in item[2].lower()
        ]
        self.populate_table(filtered)

    def add_item(self):
        dialog = MenuItemDialog(self, categories=self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.result_data
            success = add_menu_item(
                d["category_id"], d["item_name"],
                d["description"], d["price"], d["cost_price"]
            )
            if success:
                QMessageBox.information(self, "Success", "Menu item added successfully.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to add menu item.")

    def edit_item(self, item):
        dialog = MenuItemDialog(self, item=item, categories=self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.result_data
            success = update_menu_item(
                item[0], d["category_id"], d["item_name"],
                d["description"], d["price"], d["cost_price"]
            )
            if success:
                QMessageBox.information(self, "Success", "Item updated successfully.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to update item.")

    def toggle_item(self, item_id, current_status):
        success = toggle_item_availability(item_id, current_status)
        if success:
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update item status.")

    def delete_item(self, item_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this item?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_menu_item(item_id)
            if success:
                QMessageBox.information(self, "Deleted", "Item deleted successfully.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete item.")