from database.connection import create_connection


def get_setting(key):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT [value] FROM settings WHERE [key] = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error getting setting: {e}")
        return None
    finally:
        conn.close()


def get_available_menu_items():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                mi.item_id,
                mi.item_name,
                mc.category_name,
                mi.price,
                mi.description
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 1
            ORDER BY mc.category_name, mi.item_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching menu items: {e}")
        return []
    finally:
        conn.close()


def get_categories_with_items():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT mc.category_name
            FROM menu_categories mc
            JOIN menu_items mi ON mc.category_id = mi.category_id
            WHERE mi.is_available = 1
            ORDER BY mc.category_name
        """)
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []
    finally:
        conn.close()


def save_order(user_id, customer_name, cart, discount_pct,
               payment_method, reference_no=None):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()

        # Get tax rate
        tax_rate    = float(get_setting('tax_rate') or 0)
        tax_enabled = get_setting('tax_enabled') == '1'

        # Calculate totals
        subtotal = sum(
            item['price'] * item['quantity'] for item in cart
        )
        discount_amount = round(subtotal * (discount_pct / 100), 2)
        taxable         = subtotal - discount_amount
        tax_amount      = round(taxable * (tax_rate / 100), 2) if tax_enabled else 0
        total_amount    = round(taxable + tax_amount, 2)

        # Insert order
        cursor.execute("""
            INSERT INTO orders (
                customer_name, served_by, subtotal,
                discount_amount, tax_amount, total_amount,
                payment_method, payment_status, order_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Paid', 'Completed')
        """, (
            customer_name or "Guest",
            user_id, subtotal, discount_amount,
            tax_amount, total_amount, payment_method
        ))

        cursor.execute("SELECT @@IDENTITY")
        order_id = int(cursor.fetchone()[0])

        # Insert order items
        for item in cart:
            item_subtotal = item['price'] * item['quantity']
            cursor.execute("""
                INSERT INTO order_items (
                    order_id, menu_item_id, item_name,
                    quantity, unit_price, subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id, item['item_id'], item['name'],
                item['quantity'], item['price'], item_subtotal
            ))

        # Insert payment
        cursor.execute("""
            INSERT INTO payments (
                order_id, amount_paid, payment_method, reference_no
            )
            VALUES (?, ?, ?, ?)
        """, (order_id, total_amount, payment_method, reference_no))

        conn.commit()
        return {
            "order_id":        order_id,
            "subtotal":        subtotal,
            "discount_amount": discount_amount,
            "tax_amount":      tax_amount,
            "total_amount":    total_amount,
        }

    except Exception as e:
        print(f"Error saving order: {e}")
        return None
    finally:
        conn.close()


def get_recent_orders(limit=20):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP (?)
                o.order_id,
                o.customer_name,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at,
                u.full_name AS served_by
            FROM orders o
            JOIN users u ON o.served_by = u.user_id
            ORDER BY o.created_at DESC
        """, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching recent orders: {e}")
        return []
    finally:
        conn.close()