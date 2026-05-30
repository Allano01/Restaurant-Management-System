import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QGridLayout, QDialog,
    QDialogButtonBox, QComboBox, QMessageBox, QSizePolicy,
    QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from services.pos_service import (
    get_available_menu_items, get_categories_with_items,
    save_order, get_setting
)
from assets.styles import COLORS, primary_button, outline_button


# ── Menu item card ────────────────────────────────────────────
class MenuItemCard(QFrame):
    def __init__(self, item, on_click, parent=None):
        super().__init__(parent)
        self.item     = item
        self.on_click = on_click
        self.setFixedSize(150, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1.5px solid {COLORS['border']};
            }}
            QFrame:hover {{
                border: 1.5px solid {COLORS['accent']};
                background-color: {COLORS['accent_light']};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        name_lbl = QLabel(item[1])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        name_lbl.setWordWrap(True)

        price_lbl = QLabel(f"${item[3]:.2f}")
        price_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        price_lbl.setStyleSheet(f"color: {COLORS['accent']};")

        cat_lbl = QLabel(item[2])
        cat_lbl.setFont(QFont("Segoe UI", 9))
        cat_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        layout.addWidget(name_lbl)
        layout.addWidget(price_lbl)
        layout.addWidget(cat_lbl)

    def mousePressEvent(self, event):
        self.on_click(self.item)


# ── Payment dialog ────────────────────────────────────────────
class PaymentDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.total = total
        self.setWindowTitle("Process Payment")
        self.setFixedSize(400, 340)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: Segoe UI;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        title = QLabel("Process Payment")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {COLORS['border']}; border: none;")

        # Total amount display
        total_frame = QFrame()
        total_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent_light']};
                border-radius: 10px;
                border: none;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(16, 12, 16, 12)

        total_lbl = QLabel("Amount Due")
        total_lbl.setFont(QFont("Segoe UI", 11))
        total_lbl.setStyleSheet(f"color: {COLORS['accent_text']};")

        amount_lbl = QLabel(f"${self.total:.2f}")
        amount_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        amount_lbl.setStyleSheet(f"color: {COLORS['accent']};")

        total_layout.addWidget(total_lbl)
        total_layout.addStretch()
        total_layout.addWidget(amount_lbl)

        # Payment method
        method_lbl = QLabel("Payment Method")
        method_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        method_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.method_row = QHBoxLayout()
        self.method_row.setSpacing(8)
        self.method_btns = {}
        self.selected_method = "Cash"

        for method in ["Cash", "MPESA", "Card"]:
            btn = QPushButton(method)
            btn.setFixedHeight(38)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_secondary']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: Segoe UI;
                }}
                QPushButton:checked {{
                    background-color: {COLORS['accent']};
                    color: white;
                    border-color: {COLORS['accent']};
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                }}
            """)
            btn.clicked.connect(
                lambda _, m=method: self.select_method(m)
            )
            self.method_btns[method] = btn
            self.method_row.addWidget(btn)

        self.method_btns["Cash"].setChecked(True)

        # Reference number (for MPESA/Card)
        self.ref_lbl = QLabel("Reference Number (optional)")
        self.ref_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.ref_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("e.g. MPESA transaction code")
        self.ref_input.setFixedHeight(40)
        self.ref_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """)

        # Confirm button
        confirm_btn = QPushButton("✓  Confirm Payment")
        confirm_btn.setFixedHeight(44)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(primary_button())
        confirm_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)

        layout.addWidget(title)
        layout.addWidget(div)
        layout.addWidget(total_frame)
        layout.addWidget(method_lbl)
        layout.addLayout(self.method_row)
        layout.addWidget(self.ref_lbl)
        layout.addWidget(self.ref_input)
        layout.addLayout(btn_row)

    def select_method(self, method):
        self.selected_method = method
        for m, btn in self.method_btns.items():
            btn.setChecked(m == method)

    def get_data(self):
        return {
            "method":    self.selected_method,
            "reference": self.ref_input.text().strip()
        }


# ── Receipt dialog ────────────────────────────────────────────
class ReceiptDialog(QDialog):
    def __init__(self, order_data, cart, customer_name,
                 payment_method, user, parent=None):
        super().__init__(parent)
        self.order_data     = order_data
        self.cart           = cart
        self.customer_name  = customer_name
        self.payment_method = payment_method
        self.user           = user
        self.setWindowTitle(f"Receipt — Order #{order_data['order_id']}")
        self.setFixedSize(380, 580)
        self.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(8)

        rest_name = get_setting('restaurant_name') or "Restaurant"
        rest_addr = get_setting('restaurant_address') or ""
        rest_phone= get_setting('restaurant_phone') or ""
        now       = datetime.datetime.now().strftime("%d %b %Y  %H:%M")

        def lbl(text, font_size=11, bold=False, color=None, align=Qt.AlignmentFlag.AlignLeft):
            l = QLabel(text)
            l.setFont(QFont("Courier New", font_size,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            l.setStyleSheet(
                f"color: {color or COLORS['text_primary']}; "
                f"background: transparent; border: none;"
            )
            l.setAlignment(align)
            return l

        def divider(dashed=True):
            d = QLabel("- " * 22 if dashed else "─" * 36)
            d.setFont(QFont("Courier New", 9))
            d.setStyleSheet(f"color: {COLORS['border_strong']}; background: transparent; border: none;")
            return d

        layout.addWidget(lbl(rest_name, 15, True, COLORS['accent'],
                             Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(lbl(rest_addr, 9, False, COLORS['text_secondary'],
                             Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(lbl(rest_phone, 9, False, COLORS['text_secondary'],
                             Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(divider(False))

        layout.addWidget(lbl(f"Order #:   {self.order_data['order_id']}", 10))
        layout.addWidget(lbl(f"Customer:  {self.customer_name or 'Guest'}", 10))
        layout.addWidget(lbl(f"Served by: {self.user['full_name']}", 10))
        layout.addWidget(lbl(f"Date:      {now}", 10))
        layout.addWidget(lbl(f"Payment:   {self.payment_method}", 10))

        layout.addWidget(divider())

        for item in self.cart:
            item_total = item['price'] * item['quantity']
            row = QHBoxLayout()
            name_qty = QLabel(
                f"{item['name']} x{item['quantity']}"
            )
            name_qty.setFont(QFont("Courier New", 10))
            name_qty.setStyleSheet(
                f"color: {COLORS['text_primary']}; background: transparent; border: none;"
            )
            price_lbl = QLabel(f"${item_total:.2f}")
            price_lbl.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
            price_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            price_lbl.setStyleSheet(
                f"color: {COLORS['text_primary']}; background: transparent; border: none;"
            )
            row.addWidget(name_qty)
            row.addWidget(price_lbl)
            layout.addLayout(row)

        layout.addWidget(divider())

        for label, value in [
            ("Subtotal",   f"${self.order_data['subtotal']:.2f}"),
            ("Discount",   f"-${self.order_data['discount_amount']:.2f}"),
            ("Tax",        f"${self.order_data['tax_amount']:.2f}"),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl(label, 10, False, COLORS['text_secondary']))
            val = QLabel(value)
            val.setFont(QFont("Courier New", 10))
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            val.setStyleSheet(
                f"color: {COLORS['text_secondary']}; background: transparent; border: none;"
            )
            row.addWidget(val)
            layout.addLayout(row)

        layout.addWidget(divider(False))

        total_row = QHBoxLayout()
        total_row.addWidget(lbl("TOTAL", 13, True, COLORS['text_primary']))
        total_val = QLabel(f"${self.order_data['total_amount']:.2f}")
        total_val.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        total_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_val.setStyleSheet(
            f"color: {COLORS['accent']}; background: transparent; border: none;"
        )
        total_row.addWidget(total_val)
        layout.addLayout(total_row)

        layout.addWidget(divider(False))
        layout.addWidget(lbl(
            "Thank you for your order!",
            10, False, COLORS['text_muted'],
            Qt.AlignmentFlag.AlignCenter
        ))

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        print_btn = QPushButton("🖨  Print")
        print_btn.setFixedHeight(40)
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.setStyleSheet(outline_button())
        print_btn.clicked.connect(self.print_receipt)

        close_btn = QPushButton("New Order")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(primary_button())
        close_btn.clicked.connect(self.accept)

        btn_row.addWidget(print_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def print_receipt(self):
        import tempfile, subprocess
        lines = []
        rest_name  = get_setting('restaurant_name') or "Restaurant"
        rest_addr  = get_setting('restaurant_address') or ""
        rest_phone = get_setting('restaurant_phone') or ""
        now        = datetime.datetime.now().strftime("%d %b %Y  %H:%M")
        w = 40
        lines += [
            "=" * w,
            rest_name.center(w),
            rest_addr.center(w),
            rest_phone.center(w),
            "=" * w,
            f"  Order #:   {self.order_data['order_id']}",
            f"  Customer:  {self.customer_name or 'Guest'}",
            f"  Served by: {self.user['full_name']}",
            f"  Date:      {now}",
            f"  Payment:   {self.payment_method}",
            "-" * w,
        ]
        for item in self.cart:
            lines.append(
                f"  {item['name']} x{item['quantity']}"
                f"{'':>10}${item['price'] * item['quantity']:.2f}"
            )
        lines += [
            "-" * w,
            f"  Subtotal:{'':>18}${self.order_data['subtotal']:.2f}",
            f"  Discount:{'':>18}-${self.order_data['discount_amount']:.2f}",
            f"  Tax:{'':>23}${self.order_data['tax_amount']:.2f}",
            "=" * w,
            f"  TOTAL:{'':>21}${self.order_data['total_amount']:.2f}",
            "=" * w,
            "     Thank you for your order!".center(w),
            "=" * w,
            "\n\n\n",
        ]
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt", mode="w", encoding="utf-8"
            )
            tmp.write("\n".join(lines))
            tmp.close()
            subprocess.run(["notepad.exe", "/p", tmp.name], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Print Error", str(e))


# ── Main POS widget ───────────────────────────────────────────
class POSWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user        = user
        self.cart        = []
        self.all_items   = []
        self.categories  = []
        self.active_cat  = "All"
        self.discount_pct = 0
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()
        self.load_menu()

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left: menu browser ────────────────────────────────
        left = QWidget()
        left.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 24, 12, 24)
        left_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Point of Sale")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.item_count_lbl = QLabel("")
        self.item_count_lbl.setFont(QFont("Segoe UI", 11))
        self.item_count_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.item_count_lbl)

        # Search
        search_frame = QFrame()
        search_frame.setFixedHeight(42)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1.5px solid {COLORS['border']};
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent; border: none; font-size: 14px;")

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
        self.search_input.textChanged.connect(self.filter_items)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        # Category tabs
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(44)
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.cat_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.cat_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self.cat_widget = QWidget()
        self.cat_widget.setStyleSheet("background: transparent;")
        self.cat_layout = QHBoxLayout(self.cat_widget)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.setSpacing(8)
        self.cat_scroll.setWidget(self.cat_widget)

        # Menu grid scroll area
        self.menu_scroll = QScrollArea()
        self.menu_scroll.setWidgetResizable(True)
        self.menu_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                width: 6px; background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 3px;
            }
        """)

        self.menu_widget = QWidget()
        self.menu_widget.setStyleSheet("background: transparent;")
        self.menu_grid = QGridLayout(self.menu_widget)
        self.menu_grid.setSpacing(12)
        self.menu_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.menu_scroll.setWidget(self.menu_widget)

        left_layout.addLayout(header)
        left_layout.addWidget(search_frame)
        left_layout.addWidget(self.cat_scroll)
        left_layout.addWidget(self.menu_scroll)

        # ── Right: order panel ────────────────────────────────
        right = QFrame()
        right.setFixedWidth(360)
        right.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-left: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 24, 20, 20)
        right_layout.setSpacing(14)

        # Order header
        order_title = QLabel("Current Order")
        order_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        order_title.setStyleSheet(f"color: {COLORS['text_primary']};")

        # Customer name
        cust_lbl = QLabel("Customer Name (optional)")
        cust_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cust_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("e.g. John Doe")
        self.customer_input.setFixedHeight(38)
        self.customer_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """)

        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet(f"background: {COLORS['border']}; border: none;")

        # Cart items scroll
        self.cart_scroll = QScrollArea()
        self.cart_scroll.setWidgetResizable(True)
        self.cart_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self.cart_widget = QWidget()
        self.cart_widget.setStyleSheet("background: transparent;")
        self.cart_inner = QVBoxLayout(self.cart_widget)
        self.cart_inner.setContentsMargins(0, 0, 0, 0)
        self.cart_inner.setSpacing(6)
        self.cart_inner.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cart_scroll.setWidget(self.cart_widget)

        # Empty cart label
        self.empty_lbl = QLabel("🛒\n\nCart is empty\nTap items to add them")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setFont(QFont("Segoe UI", 12))
        self.empty_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet(f"background: {COLORS['border']}; border: none;")

        # Discount row
        disc_row = QHBoxLayout()
        disc_lbl = QLabel("Discount %")
        disc_lbl.setFont(QFont("Segoe UI", 11))
        disc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setValue(0)
        self.discount_spin.setSuffix("%")
        self.discount_spin.setFixedHeight(34)
        self.discount_spin.setFixedWidth(80)
        self.discount_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 8px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QSpinBox:focus {{ border-color: {COLORS['accent']}; }}
        """)
        self.discount_spin.valueChanged.connect(self.update_totals)

        disc_row.addWidget(disc_lbl)
        disc_row.addStretch()
        disc_row.addWidget(self.discount_spin)

        # Totals
        totals_frame = QFrame()
        totals_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 10px;
                border: none;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        totals_layout = QVBoxLayout(totals_frame)
        totals_layout.setContentsMargins(14, 12, 14, 12)
        totals_layout.setSpacing(6)

        self.subtotal_lbl  = self.total_row_lbl("Subtotal", "$0.00")
        self.discount_lbl  = self.total_row_lbl("Discount", "-$0.00", COLORS['danger'])
        self.tax_lbl       = self.total_row_lbl("Tax (16%)", "$0.00")

        div_total = QFrame()
        div_total.setFixedHeight(1)
        div_total.setStyleSheet(f"background: {COLORS['border_strong']}; border: none;")

        total_row_widget = QHBoxLayout()
        total_title = QLabel("TOTAL")
        total_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        total_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.grand_total_lbl = QLabel("$0.00")
        self.grand_total_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.grand_total_lbl.setStyleSheet(f"color: {COLORS['accent']};")
        self.grand_total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row_widget.addWidget(total_title)
        total_row_widget.addWidget(self.grand_total_lbl)

        totals_layout.addLayout(self.subtotal_lbl)
        totals_layout.addLayout(self.discount_lbl)
        totals_layout.addLayout(self.tax_lbl)
        totals_layout.addWidget(div_total)
        totals_layout.addLayout(total_row_widget)

        # Action buttons
        self.charge_btn = QPushButton("⚡  Charge Customer")
        self.charge_btn.setFixedHeight(48)
        self.charge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.charge_btn.setStyleSheet(primary_button())
        self.charge_btn.setEnabled(False)
        self.charge_btn.clicked.connect(self.process_payment)

        self.clear_btn = QPushButton("Clear Order")
        self.clear_btn.setFixedHeight(38)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger_light']};
                color: {COLORS['danger']};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """)
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.clear_cart)

        right_layout.addWidget(order_title)
        right_layout.addWidget(cust_lbl)
        right_layout.addWidget(self.customer_input)
        right_layout.addWidget(div1)
        right_layout.addWidget(self.cart_scroll)
        right_layout.addWidget(self.empty_lbl)
        right_layout.addWidget(div2)
        right_layout.addLayout(disc_row)
        right_layout.addWidget(totals_frame)
        right_layout.addWidget(self.charge_btn)
        right_layout.addWidget(self.clear_btn)

        root.addWidget(left, 1)
        root.addWidget(right)

    def total_row_lbl(self, label, value, value_color=None):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        val.setStyleSheet(
            f"color: {value_color or COLORS['text_primary']};"
        )
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        row.addWidget(lbl)
        row.addWidget(val)
        row._value_lbl = val
        return row

    def load_menu(self):
        self.all_items  = get_available_menu_items()
        self.categories = ["All"] + get_categories_with_items()
        self.build_category_tabs()
        self.render_menu_grid(self.all_items)
        self.item_count_lbl.setText(
            f"{len(self.all_items)} items available"
        )

    def build_category_tabs(self):
        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cat_btn_map = {}
        for cat in self.categories:
            btn = QPushButton(cat)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_secondary']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 17px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: Segoe UI;
                    padding: 0 16px;
                }}
                QPushButton:checked {{
                    background-color: {COLORS['accent']};
                    color: white;
                    border-color: {COLORS['accent']};
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                    color: {COLORS['accent']};
                }}
            """)
            btn.clicked.connect(
                lambda _, c=cat: self.filter_by_category(c)
            )
            self.cat_layout.addWidget(btn)
            self.cat_btn_map[cat] = btn

        self.cat_layout.addStretch()
        self.cat_btn_map["All"].setChecked(True)

    def filter_by_category(self, cat):
        self.active_cat = cat
        for c, btn in self.cat_btn_map.items():
            btn.setChecked(c == cat)
        self.apply_filters()

    def filter_items(self, text):
        self.apply_filters()

    def apply_filters(self):
        search = self.search_input.text().lower()
        filtered = [
            item for item in self.all_items
            if (self.active_cat == "All" or item[2] == self.active_cat)
            and (search in item[1].lower() or not search)
        ]
        self.render_menu_grid(filtered)

    def render_menu_grid(self, items):
        while self.menu_grid.count():
            child = self.menu_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cols = 4
        for idx, item in enumerate(items):
            card = MenuItemCard(item, self.add_to_cart)
            self.menu_grid.addWidget(card, idx // cols, idx % cols)

    def add_to_cart(self, item):
        for cart_item in self.cart:
            if cart_item['item_id'] == item[0]:
                cart_item['quantity'] += 1
                self.refresh_cart()
                return

        self.cart.append({
            "item_id":  item[0],
            "name":     item[1],
            "price":    float(item[3]),
            "quantity": 1,
        })
        self.refresh_cart()

    def refresh_cart(self):
        while self.cart_inner.count():
            child = self.cart_inner.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.cart:
            self.empty_lbl.show()
            self.cart_scroll.hide()
            self.charge_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.update_totals()
            return

        self.empty_lbl.hide()
        self.cart_scroll.show()
        self.charge_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        for idx, item in enumerate(self.cart):
            row_frame = QFrame()
            row_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid {COLORS['border']};
                }}
                QLabel {{ background: transparent; border: none; }}
            """)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(10, 8, 10, 8)
            row_layout.setSpacing(8)

            name_col = QVBoxLayout()
            name_col.setSpacing(0)
            name_lbl = QLabel(item['name'])
            name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            name_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
            unit_lbl = QLabel(f"${item['price']:.2f} each")
            unit_lbl.setFont(QFont("Segoe UI", 9))
            unit_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
            name_col.addWidget(name_lbl)
            name_col.addWidget(unit_lbl)

            # Qty controls
            minus_btn = QPushButton("−")
            minus_btn.setFixedSize(26, 26)
            minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            minus_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 13px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['danger_light']};
                    color: {COLORS['danger']};
                    border-color: {COLORS['danger']};
                }}
            """)
            minus_btn.clicked.connect(
                lambda _, i=idx: self.change_qty(i, -1)
            )

            qty_lbl = QLabel(str(item['quantity']))
            qty_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_lbl.setFixedWidth(28)
            qty_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

            plus_btn = QPushButton("+")
            plus_btn.setFixedSize(26, 26)
            plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            plus_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_light']};
                    color: {COLORS['accent']};
                    border: 1px solid {COLORS['accent']};
                    border-radius: 13px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent']};
                    color: white;
                }}
            """)
            plus_btn.clicked.connect(
                lambda _, i=idx: self.change_qty(i, 1)
            )

            item_total = item['price'] * item['quantity']
            total_lbl = QLabel(f"${item_total:.2f}")
            total_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            total_lbl.setStyleSheet(f"color: {COLORS['accent']};")
            total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            total_lbl.setFixedWidth(60)

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_muted']};
                    border: none;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    color: {COLORS['danger']};
                }}
            """)
            remove_btn.clicked.connect(
                lambda _, i=idx: self.remove_item(i)
            )

            row_layout.addLayout(name_col, 1)
            row_layout.addWidget(minus_btn)
            row_layout.addWidget(qty_lbl)
            row_layout.addWidget(plus_btn)
            row_layout.addWidget(total_lbl)
            row_layout.addWidget(remove_btn)

            self.cart_inner.addWidget(row_frame)

        self.update_totals()

    def change_qty(self, idx, delta):
        self.cart[idx]['quantity'] += delta
        if self.cart[idx]['quantity'] <= 0:
            self.cart.pop(idx)
        self.refresh_cart()

    def remove_item(self, idx):
        self.cart.pop(idx)
        self.refresh_cart()

    def clear_cart(self):
        if self.cart:
            reply = QMessageBox.question(
                self, "Clear Order",
                "Are you sure you want to clear the current order?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.cart.clear()
                self.customer_input.clear()
                self.discount_spin.setValue(0)
                self.refresh_cart()

    def update_totals(self):
        discount_pct    = self.discount_spin.value()
        tax_rate        = float(get_setting('tax_rate') or 16)
        tax_enabled     = get_setting('tax_enabled') == '1'

        subtotal        = sum(
            i['price'] * i['quantity'] for i in self.cart
        )
        discount_amount = round(subtotal * (discount_pct / 100), 2)
        taxable         = subtotal - discount_amount
        tax_amount      = round(taxable * (tax_rate / 100), 2) if tax_enabled else 0
        total           = round(taxable + tax_amount, 2)

        self.subtotal_lbl._value_lbl.setText(f"${subtotal:.2f}")
        self.discount_lbl._value_lbl.setText(f"-${discount_amount:.2f}")
        self.tax_lbl._value_lbl.setText(f"${tax_amount:.2f}")
        self.grand_total_lbl.setText(f"${total:.2f}")

        if total > 0:
            self.charge_btn.setText(f"⚡  Charge  ${total:.2f}")
        else:
            self.charge_btn.setText("⚡  Charge Customer")

    def process_payment(self):
        if not self.cart:
            return

        discount_pct    = self.discount_spin.value()
        tax_rate        = float(get_setting('tax_rate') or 16)
        tax_enabled     = get_setting('tax_enabled') == '1'
        subtotal        = sum(i['price'] * i['quantity'] for i in self.cart)
        discount_amount = round(subtotal * (discount_pct / 100), 2)
        taxable         = subtotal - discount_amount
        tax_amount      = round(taxable * (tax_rate / 100), 2) if tax_enabled else 0
        total           = round(taxable + tax_amount, 2)

        dialog = PaymentDialog(total, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        payment_data    = dialog.get_data()
        customer_name   = self.customer_input.text().strip()

        result = save_order(
            user_id        = self.user['user_id'],
            customer_name  = customer_name,
            cart           = self.cart,
            discount_pct   = discount_pct,
            payment_method = payment_data['method'],
            reference_no   = payment_data['reference']
        )

        if result:
            receipt = ReceiptDialog(
                order_data     = result,
                cart           = self.cart.copy(),
                customer_name  = customer_name,
                payment_method = payment_data['method'],
                user           = self.user,
                parent         = self
            )
            self.cart.clear()
            self.customer_input.clear()
            self.discount_spin.setValue(0)
            self.refresh_cart()
            receipt.exec()
        else:
            QMessageBox.critical(
                self, "Error",
                "Failed to save order. Please try again."
            )