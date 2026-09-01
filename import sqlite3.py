import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "trading_company.db"

# РОБОТА З БАЗОЮ ДАНИХ
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        # таблиця постачальників
        cur.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT
            )
        """)
        # таблиця клієнтів
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT
            )
        """)
        # таблиця товарів (із прив'язкою до постачальника)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                supplier_id INTEGER,
                FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
            )
        """)
        conn.commit()

# ГОЛОВНИЙ ДОДАТОК GUI 
class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система обліку торгівельної компанії")
        self.geometry("900x600")

        # вкладки
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_suppliers = ttk.Frame(notebook)
        self.tab_clients = ttk.Frame(notebook)
        self.tab_products = ttk.Frame(notebook)
        self.tab_orders = ttk.Frame(notebook)

        notebook.add(self.tab_products, text=" Товари та Прив'язка ")
        notebook.add(self.tab_suppliers, text=" Постачальники ")
        notebook.add(self.tab_clients, text=" Клієнти ")
        notebook.add(self.tab_orders, text=" Замовлення та Рахунки ")

        self.setup_suppliers_tab()
        self.setup_clients_tab()
        self.setup_products_tab()
        self.setup_orders_tab()

    # вкладка: постачальники 
    def setup_suppliers_tab(self):
        f = self.tab_suppliers
        ttk.Label(f, text="Назва постачальника:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sup_name = ttk.Entry(f, width=25)
        self.sup_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f, text="Телефон:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sup_phone = ttk.Entry(f, width=25)
        self.sup_phone.grid(row=1, column=1, padx=5, pady=5)

        btn_box = ttk.Frame(f)
        btn_box.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(btn_box, text="Додати", command=self.add_supplier).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_box, text="Видалити", command=self.delete_supplier).pack(side=tk.LEFT, padx=3)

        self.sup_tree = ttk.Treeview(f, columns=("ID", "Назва", "Телефон"), show="headings", height=15)
        for col in ("ID", "Назва", "Телефон"):
            self.sup_tree.heading(col, text=col)
            self.sup_tree.column(col, width=120)
        self.sup_tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.load_suppliers()

    def load_suppliers(self):
        self.sup_tree.delete(*self.sup_tree.get_children())
        with sqlite3.connect(DB_NAME) as conn:
            for row in conn.cursor().execute("SELECT * FROM suppliers"):
                self.sup_tree.insert("", tk.END, values=row)

    def add_supplier(self):
        name, phone = self.sup_name.get().strip(), self.sup_phone.get().strip()
        if not name:
            messagebox.showwarning("Помилка", "Вкажіть назву постачальника!")
            return
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("INSERT INTO suppliers (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
        self.load_suppliers()
        self.refresh_combos()
        self.sup_name.delete(0, tk.END)
        self.sup_phone.delete(0, tk.END)

    def delete_supplier(self):
        sel = self.sup_tree.selection()
        if not sel:
            return
        sup_id = self.sup_tree.item(sel[0])["values"][0]
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("DELETE FROM suppliers WHERE id = ?", (sup_id,))
            conn.commit()
        self.load_suppliers()
        self.load_products()
        self.refresh_combos()

    # вкладка: клієнти 
    def setup_clients_tab(self):
        f = self.tab_clients
        ttk.Label(f, text="ПІБ / Назва клієнта:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cli_name = ttk.Entry(f, width=25)
        self.cli_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f, text="Телефон:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cli_phone = ttk.Entry(f, width=25)
        self.cli_phone.grid(row=1, column=1, padx=5, pady=5)

        btn_box = ttk.Frame(f)
        btn_box.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(btn_box, text="Додати", command=self.add_client).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_box, text="Видалити", command=self.delete_client).pack(side=tk.LEFT, padx=3)

        self.cli_tree = ttk.Treeview(f, columns=("ID", "Клієнт", "Телефон"), show="headings", height=15)
        for col in ("ID", "Клієнт", "Телефон"):
            self.cli_tree.heading(col, text=col)
            self.cli_tree.column(col, width=120)
        self.cli_tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.load_clients()

    def load_clients(self):
        self.cli_tree.delete(*self.cli_tree.get_children())
        with sqlite3.connect(DB_NAME) as conn:
            for row in conn.cursor().execute("SELECT * FROM clients"):
                self.cli_tree.insert("", tk.END, values=row)

    def add_client(self):
        name, phone = self.cli_name.get().strip(), self.cli_phone.get().strip()
        if not name:
            messagebox.showwarning("Помилка", "Вкажіть ім'я клієнта!")
            return
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
        self.load_clients()
        self.refresh_combos()
        self.cli_name.delete(0, tk.END)
        self.cli_phone.delete(0, tk.END)

    def delete_client(self):
        sel = self.cli_tree.selection()
        if not sel:
            return
        cli_id = self.cli_tree.item(sel[0])["values"][0]
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("DELETE FROM clients WHERE id = ?", (cli_id,))
            conn.commit()
        self.load_clients()
        self.refresh_combos()

    # вкладка: товари та прив'язка 
    def setup_products_tab(self):
        f = self.tab_products
        form = ttk.Frame(f)
        form.pack(pady=5, padx=10, fill=tk.X)

        ttk.Label(form, text="Назва товару:").grid(row=0, column=0, padx=3, pady=2)
        self.prod_name = ttk.Entry(form, width=15)
        self.prod_name.grid(row=0, column=1, padx=3, pady=2)

        ttk.Label(form, text="Категорія:").grid(row=0, column=2, padx=3, pady=2)
        self.prod_cat = ttk.Entry(form, width=15)
        self.prod_cat.grid(row=0, column=3, padx=3, pady=2)

        ttk.Label(form, text="Ціна (грн):").grid(row=0, column=4, padx=3, pady=2)
        self.prod_price = ttk.Entry(form, width=10)
        self.prod_price.grid(row=0, column=5, padx=3, pady=2)

        ttk.Label(form, text="Постачальник:").grid(row=1, column=0, padx=3, pady=2)
        self.prod_sup_combo = ttk.Combobox(form, state="readonly", width=18)
        self.prod_sup_combo.grid(row=1, column=1, padx=3, pady=2)

        ttk.Button(form, text="Додати товар", command=self.add_product).grid(row=1, column=2, padx=3, pady=2)
        ttk.Button(form, text="Видалити товар", command=self.delete_product).grid(row=1, column=3, padx=3, pady=2)
        ttk.Button(form, text="Відв'язати постачальника", command=self.unbind_supplier).grid(row=1, column=4, columnspan=2, padx=3, pady=2)

        self.prod_tree = ttk.Treeview(f, columns=("ID", "Назва", "Категорія", "Ціна", "Кількість", "Постачальник"), show="headings", height=15)
        for col in ("ID", "Назва", "Категорія", "Ціна", "Кількість", "Постачальник"):
            self.prod_tree.heading(col, text=col)
            self.prod_tree.column(col, width=110)
        self.prod_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.load_products()

    def load_products(self):
        self.prod_tree.delete(*self.prod_tree.get_children())
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.name, p.category, p.price, p.quantity, COALESCE(s.name, '---')
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
            """)
            for row in cur.fetchall():
                self.prod_tree.insert("", tk.END, values=row)

    def add_product(self):
        name = self.prod_name.get().strip()
        cat = self.prod_cat.get().strip()
        try:
            price = float(self.prod_price.get())
        except ValueError:
            messagebox.showwarning("Помилка", "Введіть коректну ціну!")
            return

        sup_val = self.prod_sup_combo.get()
        sup_id = int(sup_val.split(":")[0]) if sup_val and sup_val != "Не обрано" else None

        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute(
                "INSERT INTO products (name, category, price, quantity, supplier_id) VALUES (?, ?, ?, 0, ?)",
                (name, cat, price, sup_id)
            )
            conn.commit()
        self.load_products()
        self.refresh_combos()

    def delete_product(self):
        sel = self.prod_tree.selection()
        if not sel:
            return
        p_id = self.prod_tree.item(sel[0])["values"][0]
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("DELETE FROM products WHERE id = ?", (p_id,))
            conn.commit()
        self.load_products()
        self.refresh_combos()

    def unbind_supplier(self):
        sel = self.prod_tree.selection()
        if not sel:
            return
        p_id = self.prod_tree.item(sel[0])["values"][0]
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("UPDATE products SET supplier_id = NULL WHERE id = ?", (p_id,))
            conn.commit()
        self.load_products()

    # вкладка: замовлення та рахунки 
    def setup_orders_tab(self):
        f = self.tab_orders
        
        # ліва колонка — отримання/замовлення у постачальника
        left = ttk.LabelFrame(f, text="Замовлення та надходження від постачальника", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(left, text="Товар:").pack(anchor="w")
        self.ord_prod_combo = ttk.Combobox(left, state="readonly")
        self.ord_prod_combo.pack(fill=tk.X, pady=3)

        ttk.Label(left, text="Кількість для отримання:").pack(anchor="w")
        self.ord_qty = ttk.Entry(left)
        self.ord_qty.pack(fill=tk.X, pady=3)

        ttk.Button(left, text="Зафіксувати отримання товарів", command=self.receive_goods).pack(pady=10)

        # права колонка — рахунок для клієнта (замовлення по телефону)
        right = ttk.LabelFrame(f, text="Створення рахунку для клієнта (телефонне замовлення)", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(right, text="Клієнт:").pack(anchor="w")
        self.inv_cli_combo = ttk.Combobox(right, state="readonly")
        self.inv_cli_combo.pack(fill=tk.X, pady=3)

        ttk.Label(right, text="Товар:").pack(anchor="w")
        self.inv_prod_combo = ttk.Combobox(right, state="readonly")
        self.inv_prod_combo.pack(fill=tk.X, pady=3)

        ttk.Label(right, text="Кількість для продажу:").pack(anchor="w")
        self.inv_qty = ttk.Entry(right)
        self.inv_qty.pack(fill=tk.X, pady=3)

        ttk.Button(right, text="Сформувати рахунок", command=self.create_invoice).pack(pady=10)

        self.refresh_combos()

    def receive_goods(self):
        prod_val = self.ord_prod_combo.get()
        if not prod_val:
            return
        p_id = int(prod_val.split(":")[0])
        try:
            qty = int(self.ord_qty.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Помилка", "Введіть ціле додатне число кількості!")
            return

        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (qty, p_id))
            conn.commit()

        messagebox.showinfo("Успіх", f"Товар успішно отримано на склад у кількості {qty} шт.")
        self.load_products()

    def create_invoice(self):
        cli_val = self.inv_cli_combo.get()
        prod_val = self.inv_prod_combo.get()
        if not cli_val or not prod_val:
            messagebox.showwarning("Помилка", "Оберіть клієнта та товар!")
            return

        p_id = int(prod_val.split(":")[0])
        try:
            qty = int(self.inv_qty.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Помилка", "Введіть ціле додатне число кількості!")
            return

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, price, quantity FROM products WHERE id = ?", (p_id,))
            p_name, price, stock = cur.fetchone()

            if stock < qty:
                messagebox.showerror("Недостатньо товару", f"На складі лише {stock} шт.")
                return

            # списуємо зі складу
            cur.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, p_id))
            conn.commit()

        total = price * qty
        invoice_text = (
            f"РАХУНОК-ФАКТУРА\n"
            f"---------------------------\n"
            f"Клієнт: {cli_val}\n"
            f"Товар: {p_name}\n"
            f"Ціна за од.: {price:.2f} грн\n"
            f"Кількість: {qty} шт.\n"
            f"---------------------------\n"
            f"ЗАГАЛЬНА СУМА: {total:.2f} грн"
        )
        messagebox.showinfo("Рахунок створено", invoice_text)
        self.load_products()

    def refresh_combos(self):
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            # оновлення списку постачальників
            cur.execute("SELECT id, name FROM suppliers")
            sups = ["Не обрано"] + [f"{r[0]}: {r[1]}" for r in cur.fetchall()]
            self.prod_sup_combo["values"] = sups

            # оновлення списку клієнтів
            cur.execute("SELECT id, name, phone FROM clients")
            self.inv_cli_combo["values"] = [f"{r[0]}: {r[1]} ({r[2]})" for r in cur.fetchall()]

            # оновлення списку товарів
            cur.execute("SELECT id, name FROM products")
            prods = [f"{r[0]}: {r[1]}" for r in cur.fetchall()]
            self.ord_prod_combo["values"] = prods
            self.inv_prod_combo["values"] = prods

if __name__ == "__main__":
    init_db()
    app = TradingApp()
    app.mainloop()