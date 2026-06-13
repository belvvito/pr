import pymysql
import os
from PyQt6.QtGui import QPixmap
from models.user import User
from models.menu_item import MenuItem


class DBService:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = pymysql.connect(
            host="localhost", user="root", password="root",
            db="pizza3", autocommit=True, charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    # ==================== АВТОРИЗАЦИЯ ====================
    def get_user(self, login, password):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT u.id_user, u.username, u.password, u.contact_info, u.id_role, r.name_role
                FROM users u JOIN roles r ON u.id_role = r.id_role
                WHERE u.username=%s AND u.password=%s
            """, (login, password))
            row = cur.fetchone()
            return User(**row) if row else None

    def get_all_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id_user, username, contact_info FROM users WHERE id_role = 3")
            return cur.fetchall()

    # ==================== МЕНЮ ====================
    def get_menu(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id_menu, name_item, description, price, category, quantity, discount, manufacturer, supplier, photo FROM menu")
            items = []
            for row in cur.fetchall():
                photo_name = row.get('photo', 'menu.png')
                photo_path = os.path.join("data", photo_name)
                if os.path.exists(photo_path):
                    pix = QPixmap(photo_path)
                else:
                    default_path = os.path.join("data", "menu.png")
                    pix = QPixmap(default_path) if os.path.exists(default_path) else QPixmap()
                row['photo'] = pix
                row['photo_path'] = photo_name
                items.append(MenuItem(**row))
            return items

    def add_item(self, name, desc, price, category, quantity, discount, photo_name="menu.png"):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO menu (name_item, description, price, category, quantity, discount, photo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, desc, price, category, quantity, discount, photo_name))

    def update_item(self, id_menu, name, price, desc, quantity, discount, photo_name=None):
        with self.conn.cursor() as cur:
            if photo_name:
                cur.execute("""
                    UPDATE menu 
                    SET name_item=%s, price=%s, description=%s, quantity=%s, discount=%s, photo=%s 
                    WHERE id_menu=%s
                """, (name, price, desc, quantity, discount, photo_name, id_menu))
            else:
                cur.execute("""
                    UPDATE menu 
                    SET name_item=%s, price=%s, description=%s, quantity=%s, discount=%s 
                    WHERE id_menu=%s
                """, (name, price, desc, quantity, discount, id_menu))

    def delete_item(self, id_menu):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM order_item WHERE id_menu=%s", (id_menu,))
                if cur.fetchone()['cnt'] > 0:
                    return False, "Нельзя удалить блюдо, которое есть в заказах!"
                cur.execute("DELETE FROM menu WHERE id_menu=%s", (id_menu,))
                return True, ""
        except Exception as e:
            return False, str(e)

    def get_suppliers(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT supplier FROM menu WHERE supplier IS NOT NULL AND supplier != ''")
            return [row['supplier'] for row in cur.fetchall()]

    # ==================== ЗАКАЗЫ ====================
    def create_order(self, id_user, id_menu, qty, price, address):
        total = price * qty
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders (id_user, total_amount, address, status) 
                VALUES (%s, %s, %s, 'Ожидает приготовления')
            """, (id_user, total, address))
            order_id = cur.lastrowid
            cur.execute("""
                INSERT INTO order_item (id_order, id_menu, quantity) 
                VALUES (%s, %s, %s)
            """, (order_id, id_menu, qty))
            return order_id

    def get_all_orders(self, status_filter="Все"):
        with self.conn.cursor() as cur:
            sql = """
                SELECT o.id_order, u.username, u.contact_info, o.order_date, 
                       o.total_amount, o.status, o.address
                FROM orders o
                JOIN users u ON o.id_user = u.id_user
            """
            params = ()
            if status_filter != "Все":
                sql += " WHERE o.status = %s"
                params = (status_filter,)
            sql += " ORDER BY o.id_order DESC"
            cur.execute(sql, params)
            return cur.fetchall()

    def get_order_items(self, id_order):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT oi.id_order_item, m.name_item, oi.quantity, m.price
                FROM order_item oi
                JOIN menu m ON oi.id_menu = m.id_menu
                WHERE oi.id_order = %s
            """, (id_order,))
            return cur.fetchall()

    def update_order_status(self, id_order, status):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE orders SET status=%s WHERE id_order=%s", (status, id_order))

    def update_order(self, id_order, address, status):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE orders SET address=%s, status=%s WHERE id_order=%s", (address, status, id_order))

    def delete_order(self, id_order):
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM order_item WHERE id_order=%s", (id_order,))
                cur.execute("DELETE FROM orders WHERE id_order=%s", (id_order,))
                return True, "Заказ удалён"
        except Exception as e:
            return False, str(e)