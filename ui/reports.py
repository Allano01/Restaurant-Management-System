import csv
import os
import datetime
import tempfile
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QComboBox, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from services.reports_service import (
    get_sales_summary, get_daily_sales,
    get_sales_by_payment_method, get_top_selling_items,
    get_sales_by_category, get_top_customers,
    get_staff_performance, get_low_stock_report,
    get_hourly_sales
)
from assets.styles import COLORS, primary_button, outline_button


class ReportsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user   = user
        self.period = "month"
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_all()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Reports & Analytics")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Business insights and performance reports"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.setFixedHeight(40)
        self.period_combo.setFixedWidth(160)
        self.period_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)
        for label, value in [
            ("Today",      "today"),
            ("This Week",  "week"),
            ("This Month", "month"),
        ]:
            self.period_combo.addItem(label, value)
        self.period_combo.setCurrentIndex(2)
        self.period_combo.currentIndexChanged.connect(
            self.on_period_changed
        )

        export_btn = QPushButton("⬇  Export CSV")
        export_btn.setFixedHeight(40)
        export_btn.setFixedWidth(130)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(outline_button())
        export_btn.clicked.connect(self.export_csv)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_all)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(self.period_combo)
        header_row.addWidget(export_btn)
        header_row.addWidget(refresh_btn)

        # ── Summary cards ─────────────────────────────────────
        self.summary_row = QHBoxLayout()
        self.summary_row.setSpacing(14)

        # ── Tabs ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent']};
                border-bottom: 2px solid {COLORS['accent']};
            }}
            QTabBar::tab:hover {{
                color: {COLORS['accent']};
            }}
        """)

        # Tab 1 — Sales
        self.sales_tab = QWidget()
        self.sales_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_sales_tab()
        self.tabs.addTab(self.sales_tab, "💰  Sales")

        # Tab 2 — Menu
        self.menu_tab = QWidget()
        self.menu_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_menu_tab()
        self.tabs.addTab(self.menu_tab, "🍽  Menu")

        # Tab 3 — Customers
        self.cust_tab = QWidget()
        self.cust_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_customers_tab()
        self.tabs.addTab(self.cust_tab, "👥  Customers")

        # Tab 4 — Staff
        self.staff_tab = QWidget()
        self.staff_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_staff_tab()
        self.tabs.addTab(self.staff_tab, "👨‍💼  Staff")

        # Tab 5 — Inventory
        self.inv_tab = QWidget()
        self.inv_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_inventory_tab()
        self.tabs.addTab(self.inv_tab, "📦  Inventory")

        layout.addLayout(header_row)
        layout.addLayout(self.summary_row)
        layout.addWidget(self.tabs)

    # ── Tab setup methods ─────────────────────────────────────
    def setup_sales_tab(self):
        layout = QVBoxLayout(self.sales_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Daily sales table
        lbl = QLabel("Daily Sales Breakdown")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.daily_table = self.make_table(
            ["DATE", "ORDERS", "REVENUE"]
        )

        # Payment method table
        lbl2 = QLabel("Sales by Payment Method")
        lbl2.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl2.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.payment_table = self.make_table(
            ["PAYMENT METHOD", "ORDERS", "REVENUE"]
        )

        # Hourly sales table
        lbl3 = QLabel("Today's Hourly Sales")
        lbl3.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl3.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.hourly_table = self.make_table(
            ["HOUR", "ORDERS", "REVENUE"]
        )

        layout.addWidget(lbl)
        layout.addWidget(self.daily_table)
        layout.addWidget(lbl2)
        layout.addWidget(self.payment_table)
        layout.addWidget(lbl3)
        layout.addWidget(self.hourly_table)

    def setup_menu_tab(self):
        layout = QVBoxLayout(self.menu_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Top Selling Items")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.items_table = self.make_table(
            ["RANK", "ITEM NAME", "QTY SOLD", "REVENUE"]
        )

        lbl2 = QLabel("Revenue by Category")
        lbl2.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl2.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.cat_table = self.make_table(
            ["CATEGORY", "QTY SOLD", "REVENUE", "SHARE %"]
        )

        layout.addWidget(lbl)
        layout.addWidget(self.items_table)
        layout.addWidget(lbl2)
        layout.addWidget(self.cat_table)

    def setup_customers_tab(self):
        layout = QVBoxLayout(self.cust_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Top Customers by Spend")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.cust_table = self.make_table(
            ["RANK", "CUSTOMER", "ORDERS", "TOTAL SPENT", "AVG ORDER"]
        )

        layout.addWidget(lbl)
        layout.addWidget(self.cust_table)

    def setup_staff_tab(self):
        layout = QVBoxLayout(self.staff_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Staff Sales Performance")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.staff_table = self.make_table(
            ["STAFF NAME", "ORDERS", "REVENUE", "AVG ORDER"]
        )

        layout.addWidget(lbl)
        layout.addWidget(self.staff_table)

    def setup_inventory_tab(self):
        layout = QVBoxLayout(self.inv_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Low Stock & Reorder Alerts")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.low_stock_table = self.make_table([
            "INGREDIENT", "UNIT", "CURRENT",
            "MINIMUM", "UNIT COST",
            "VALUE", "SUPPLIER", "ALERT"
        ])

        layout.addWidget(lbl)
        layout.addWidget(self.low_stock_table)

    # ── Data loading ──────────────────────────────────────────
    def on_period_changed(self):
        self.period = self.period_combo.currentData()
        self.load_all()

    def load_all(self):
        self.period = self.period_combo.currentData()
        self.load_summary()
        self.load_sales_tab()
        self.load_menu_tab()
        self.load_customers_tab()
        self.load_staff_tab()
        self.load_inventory_tab()

    def load_summary(self):
        summary = get_sales_summary(self.period)

        while self.summary_row.count():
            item = self.summary_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for title, value, sub, color in [
            ("Total Revenue",
             f"${summary.get('total_revenue', 0):.2f}",
             "Gross sales",
             COLORS['accent']),
            ("Total Orders",
             str(summary.get('total_orders', 0)),
             "Completed orders",
             COLORS['blue']),
            ("Avg Order Value",
             f"${summary.get('avg_order', 0):.2f}",
             "Per transaction",
             COLORS['warning']),
            ("Total Discounts",
             f"${summary.get('total_discount', 0):.2f}",
             "Discounts given",
             COLORS['danger']),
            ("Tax Collected",
             f"${summary.get('total_tax', 0):.2f}",
             "VAT collected",
             "#7c3aed"),
        ]:
            card = self.make_summary_card(
                title, value, sub, color
            )
            self.summary_row.addWidget(card)

    def load_sales_tab(self):
        # Daily sales
        daily = get_daily_sales(
            7 if self.period == "week" else
            30 if self.period == "month" else 1
        )
        self.daily_table.setRowCount(len(daily))
        for idx, row in enumerate(daily):
            self.daily_table.setRowHeight(idx, 44)
            date_str = (
                row[0].strftime("%d %b %Y")
                if hasattr(row[0], 'strftime')
                else str(row[0])
            )
            self.set_cell(self.daily_table, idx, 0, date_str)
            self.set_cell(
                self.daily_table, idx, 1, str(row[1]),
                align=True
            )
            self.set_cell(
                self.daily_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )

        # Payment methods
        payments = get_sales_by_payment_method(self.period)
        self.payment_table.setRowCount(len(payments))
        for idx, row in enumerate(payments):
            self.payment_table.setRowHeight(idx, 44)
            self.set_cell(
                self.payment_table, idx, 0, row[0], bold=True
            )
            self.set_cell(
                self.payment_table, idx, 1, str(row[1]),
                align=True
            )
            self.set_cell(
                self.payment_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )

        # Hourly sales
        hourly = get_hourly_sales()
        self.hourly_table.setRowCount(len(hourly))
        for idx, row in enumerate(hourly):
            self.hourly_table.setRowHeight(idx, 44)
            hour     = int(row[0])
            suffix   = "AM" if hour < 12 else "PM"
            hour_12  = hour % 12 or 12
            self.set_cell(
                self.hourly_table, idx, 0,
                f"{hour_12}:00 {suffix}", align=True
            )
            self.set_cell(
                self.hourly_table, idx, 1, str(row[1]),
                align=True
            )
            self.set_cell(
                self.hourly_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )

    def load_menu_tab(self):
        # Top items
        items = get_top_selling_items(
            limit=10, period=self.period
        )
        self.items_table.setRowCount(len(items))
        for idx, row in enumerate(items):
            self.items_table.setRowHeight(idx, 44)
            self.set_cell(
                self.items_table, idx, 0,
                f"#{idx+1}", align=True,
                color=COLORS['accent']
            )
            self.set_cell(
                self.items_table, idx, 1,
                row[0], bold=True
            )
            self.set_cell(
                self.items_table, idx, 2,
                str(int(row[1])), align=True
            )
            self.set_cell(
                self.items_table, idx, 3,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )

        # Categories
        cats       = get_sales_by_category(self.period)
        total_rev  = sum(float(r[2]) for r in cats) or 1
        self.cat_table.setRowCount(len(cats))
        for idx, row in enumerate(cats):
            self.cat_table.setRowHeight(idx, 44)
            share = float(row[2]) / total_rev * 100
            self.set_cell(
                self.cat_table, idx, 0, row[0], bold=True
            )
            self.set_cell(
                self.cat_table, idx, 1,
                str(int(row[1])), align=True
            )
            self.set_cell(
                self.cat_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )
            self.set_cell(
                self.cat_table, idx, 3,
                f"{share:.1f}%", align=True
            )

    def load_customers_tab(self):
        customers = get_top_customers(
            limit=10, period=self.period
        )
        self.cust_table.setRowCount(len(customers))
        for idx, row in enumerate(customers):
            self.cust_table.setRowHeight(idx, 44)
            orders    = row[1]
            spent     = float(row[2])
            avg_order = spent / orders if orders > 0 else 0
            self.set_cell(
                self.cust_table, idx, 0,
                f"#{idx+1}", align=True,
                color=COLORS['accent']
            )
            self.set_cell(
                self.cust_table, idx, 1,
                row[0], bold=True
            )
            self.set_cell(
                self.cust_table, idx, 2,
                str(orders), align=True
            )
            self.set_cell(
                self.cust_table, idx, 3,
                f"${spent:.2f}",
                bold=True, color=COLORS['accent']
            )
            self.set_cell(
                self.cust_table, idx, 4,
                f"${avg_order:.2f}", align=True
            )

    def load_staff_tab(self):
        staff = get_staff_performance(self.period)
        self.staff_table.setRowCount(len(staff))
        for idx, row in enumerate(staff):
            self.staff_table.setRowHeight(idx, 44)
            self.set_cell(
                self.staff_table, idx, 0,
                row[0], bold=True
            )
            self.set_cell(
                self.staff_table, idx, 1,
                str(row[1]), align=True
            )
            self.set_cell(
                self.staff_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, color=COLORS['accent']
            )
            self.set_cell(
                self.staff_table, idx, 3,
                f"${float(row[3]):.2f}", align=True
            )

    def load_inventory_tab(self):
        items = get_low_stock_report()
        self.low_stock_table.setRowCount(len(items))

        alert_colors = {
            "Out of Stock": COLORS['danger'],
            "Critical":     "#dc2626",
            "Low Stock":    COLORS['warning'],
        }

        for idx, row in enumerate(items):
            self.low_stock_table.setRowHeight(idx, 44)
            self.set_cell(
                self.low_stock_table, idx, 0,
                row[0], bold=True,
                color=COLORS['accent']
            )
            self.set_cell(
                self.low_stock_table, idx, 1, row[1]
            )
            self.set_cell(
                self.low_stock_table, idx, 2,
                f"{float(row[2]):.2f}",
                bold=True,
                color=(
                    COLORS['danger']
                    if float(row[2]) <= float(row[3])
                    else COLORS['text_primary']
                )
            )
            self.set_cell(
                self.low_stock_table, idx, 3,
                f"{float(row[3]):.2f}"
            )
            self.set_cell(
                self.low_stock_table, idx, 4,
                f"${float(row[5]):.2f}"
            )
            self.set_cell(
                self.low_stock_table, idx, 5,
                f"${float(row[6]):.2f}"
            )
            self.set_cell(
                self.low_stock_table, idx, 6, row[7]
            )

            # Alert badge
            alert      = row[8]
            a_color    = alert_colors.get(
                alert, COLORS['warning']
            )
            badge_widget = QWidget()
            badge_widget.setStyleSheet(
                "background: transparent;"
            )
            from PyQt6.QtWidgets import QHBoxLayout as QHL
            bl = QHL(badge_widget)
            bl.setContentsMargins(6, 0, 6, 0)
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge = QLabel(alert)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 10, QFont.Weight.Bold)
            )
            badge.setStyleSheet(f"""
                color: {a_color};
                background-color: transparent;
                border: 1.5px solid {a_color};
                border-radius: 10px;
                padding: 0 8px;
            """)
            bl.addWidget(badge)
            self.low_stock_table.setCellWidget(
                idx, 7, badge_widget
            )

    # ── Export ────────────────────────────────────────────────
    def export_csv(self):
        path = QFileDialog.getSaveFileName(
            self, "Export Report",
            f"sales_report_{self.period}.csv",
            "CSV Files (*.csv)"
        )[0]
        if not path:
            return
        try:
            with open(path, "w", newline="",
                      encoding="utf-8") as f:
                writer = csv.writer(f)

                # Sales summary
                summary = get_sales_summary(self.period)
                writer.writerow(["SALES SUMMARY"])
                writer.writerow([
                    "Period", "Total Orders",
                    "Revenue", "Avg Order",
                    "Discounts", "Tax"
                ])
                writer.writerow([
                    self.period,
                    summary.get("total_orders", 0),
                    f"${summary.get('total_revenue', 0):.2f}",
                    f"${summary.get('avg_order', 0):.2f}",
                    f"${summary.get('total_discount', 0):.2f}",
                    f"${summary.get('total_tax', 0):.2f}",
                ])
                writer.writerow([])

                # Top items
                writer.writerow(["TOP SELLING ITEMS"])
                writer.writerow([
                    "Item", "Qty Sold", "Revenue"
                ])
                for row in get_top_selling_items(
                    period=self.period
                ):
                    writer.writerow([
                        row[0], row[1],
                        f"${float(row[2]):.2f}"
                    ])
                writer.writerow([])

                # Staff
                writer.writerow(["STAFF PERFORMANCE"])
                writer.writerow([
                    "Staff", "Orders",
                    "Revenue", "Avg Order"
                ])
                for row in get_staff_performance(
                    self.period
                ):
                    writer.writerow([
                        row[0], row[1],
                        f"${float(row[2]):.2f}",
                        f"${float(row[3]):.2f}"
                    ])

            QMessageBox.information(
                self, "Exported",
                f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", str(e)
            )

    # ── Helpers ───────────────────────────────────────────────
    def make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border: none;
                gridline-color: transparent;
                font-family: Segoe UI;
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 0px 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['accent_light']};
                color: {COLORS['accent_text']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: bold;
                font-size: 11px;
                font-family: Segoe UI;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_tertiary']};
                width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_strong']};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        table.setShowGrid(False)
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        return table

    def set_cell(self, table, row, col, text,
                 bold=False, align=False, color=None):
        item = QTableWidgetItem(str(text))
        if bold:
            item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
        if align:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        if color:
            item.setForeground(QColor(color))
        table.setItem(row, col, item)

    def make_summary_card(self, title, value,
                          subtitle, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {color};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        val_lbl = QLabel(value)
        val_lbl.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        val_lbl.setStyleSheet(f"color: {color};")

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; "
            f"letter-spacing: 1px;"
        )

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']};"
        )

        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)

        return frame