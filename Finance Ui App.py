import customtkinter as ctk
import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Настройка внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# База данных
conn = sqlite3.connect('finance.db')
c = conn.cursor()

# Главное окно
app = ctk.CTk()
app.title("Финансовый помощник")
app.geometry("1000x700")

# Основные фреймы
sidebar = ctk.CTkFrame(app, width=200, height=700, corner_radius=0)
sidebar.pack(side="left", fill="y")

content = ctk.CTkFrame(app, width=800, height=700, corner_radius=0)
content.pack(side="right", fill="both", expand=True)

# Функция очистки основной зоны

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

# Функция всплывающего уведомления

def show_alert(message, color="green"):
    alert = ctk.CTkLabel(content, text=message, text_color=color, font=("Arial", 16))
    alert.pack(pady=10)
    app.after(2000, alert.destroy)

# Функции загрузки контента

def load_add_income():
    clear_content()
    label = ctk.CTkLabel(content, text="Добавить доход", font=("Arial", 20))
    label.pack(pady=20)

    entry_amount = ctk.CTkEntry(content, placeholder_text="Введите сумму")
    entry_amount.pack(pady=10)

    def save_income():
        amount = float(entry_amount.get())
        date = datetime.date.today().isoformat()
        c.execute('INSERT INTO incomes (amount, date, category) VALUES (?, ?, ?)', (amount, date, "Доход"))
        conn.commit()
        show_alert("Доход успешно добавлен!")

    button_save = ctk.CTkButton(content, text="Сохранить", command=save_income)
    button_save.pack(pady=10)


def load_add_expense():
    clear_content()
    label = ctk.CTkLabel(content, text="Добавить расход", font=("Arial", 20))
    label.pack(pady=20)

    entry_amount = ctk.CTkEntry(content, placeholder_text="Введите сумму")
    entry_amount.pack(pady=10)

    categories = ["Продукты", "Транспорт", "Развлечения", "Здоровье", "Коммуналка", "Другое"]
    category_box = ctk.CTkComboBox(content, values=categories)
    category_box.pack(pady=10)

    def save_expense():
        amount = float(entry_amount.get())
        category = category_box.get()
        date = datetime.date.today().isoformat()
        c.execute('INSERT INTO expenses (amount, date, category) VALUES (?, ?, ?)', (amount, date, category))
        conn.commit()
        show_alert("Расход успешно добавлен!")

    button_save = ctk.CTkButton(content, text="Сохранить", command=save_expense)
    button_save.pack(pady=10)


def load_expense_chart():
    clear_content()
    c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
    data = c.fetchall()

    if data:
        categories, amounts = zip(*data)
        fig, ax = plt.subplots(figsize=(6,4))
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        ax.set_title("Расходы по категориям")

        canvas = FigureCanvasTkAgg(fig, content)
        canvas.get_tk_widget().pack()
        canvas.draw()
    else:
        label = ctk.CTkLabel(content, text="Нет данных для графика.", font=("Arial", 20))
        label.pack(pady=20)


def load_monthly_history():
    clear_content()
    label = ctk.CTkLabel(content, text="История по месяцу (ГГГГ-ММ)", font=("Arial", 20))
    label.pack(pady=10)

    entry_month = ctk.CTkEntry(content)
    entry_month.pack(pady=10)

    textbox = ctk.CTkTextbox(content, height=300)
    textbox.pack(pady=10)

    def search():
        month = entry_month.get()
        textbox.delete("1.0", "end")
        c.execute("SELECT date, amount, category FROM incomes WHERE date LIKE ?", (month+'%',))
        incomes = c.fetchall()
        c.execute("SELECT date, amount, category FROM expenses WHERE date LIKE ?", (month+'%',))
        expenses = c.fetchall()

        text = "Доходы:\n"
        for item in incomes:
            text += f"{item[0]} | +{item[1]:.2f} € | {item[2]}\n"

        text += "\nРасходы:\n"
        for item in expenses:
            text += f"{item[0]} | -{item[1]:.2f} € | {item[2]}\n"

        textbox.insert("end", text)

    button_search = ctk.CTkButton(content, text="Показать", command=search)
    button_search.pack(pady=10)


def load_budget_analysis():
    clear_content()
    c.execute('SELECT SUM(amount) FROM incomes')
    total_income = c.fetchone()[0] or 0

    c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
    expenses = c.fetchall()

    needs_spent = 0
    wants_spent = 0
    savings_spent = 0

    for category, amount in expenses:
        if category in ("Продукты", "Коммуналка", "Здоровье"):
            needs_spent += amount
        elif category in ("Транспорт", "Развлечения"):
            wants_spent += amount
        else:
            savings_spent += amount

    needs_limit = total_income * 0.5
    wants_limit = total_income * 0.3
    savings_limit = total_income * 0.2

    text = f"Доход: {total_income:.2f} €\n\n"
    text += f"Потрачено на Нужды: {needs_spent:.2f} € (лимит {needs_limit:.2f} €)\n"
    text += f"Потрачено на Желания: {wants_spent:.2f} € (лимит {wants_limit:.2f} €)\n"
    text += f"Потрачено на Другое/Накопления: {savings_spent:.2f} € (лимит {savings_limit:.2f} €)\n"

    label = ctk.CTkLabel(content, text=text, justify="left")
    label.pack(pady=20)


def load_show_credits():
    clear_content()
    c.execute("SELECT name, total_amount, monthly_payment, start_date, months FROM credits")
    credits = c.fetchall()
    text = "Список кредитов:\n\n"
    if credits:
        for credit in credits:
            name, total, monthly, start, months = credit
            text += f"{name}: {total:.2f} €, {monthly:.2f} €/мес, на {months} месяцев\n"
    else:
        text += "Нет активных кредитов."

    label = ctk.CTkLabel(content, text=text, justify="left")
    label.pack(pady=20)
def load_show_balance():
    clear_content()
    c.execute('SELECT SUM(amount) FROM incomes')
    total_income = c.fetchone()[0] or 0
    c.execute('SELECT SUM(amount) FROM expenses')
    total_expense = c.fetchone()[0] or 0
    balance = total_income - total_expense

    text = f"Доходы: {total_income:.2f} €\nРасходы: {total_expense:.2f} €\nБаланс: {balance:.2f} €"
    label = ctk.CTkLabel(content, text=text, justify="left", font=("Arial", 20))
    label.pack(pady=20)


def load_unpaid_payments():
    clear_content()
    c.execute("SELECT id, name, amount FROM monthly_payments WHERE paid = 0")
    payments = c.fetchall()

    text = "Неоплаченные платежи:\n\n"
    if payments:
        for pid, name, amount in payments:
            text += f"ID {pid}: {name} — {amount:.2f} €\n"
    else:
        text += "Нет неоплаченных платежей."

    label = ctk.CTkLabel(content, text=text, justify="left")
    label.pack(pady=20)


def load_mark_payment():
    clear_content()
    label = ctk.CTkLabel(content, text="Отметить платеж как оплаченный (ID)", font=("Arial", 20))
    label.pack(pady=10)

    entry_id = ctk.CTkEntry(content)
    entry_id.pack(pady=10)

    def mark_paid():
        pid = entry_id.get()
        c.execute("UPDATE monthly_payments SET paid = 1 WHERE id = ?", (pid,))
        conn.commit()
        show_alert("Платеж отмечен как оплаченный!")

    button_confirm = ctk.CTkButton(content, text="Отметить оплачено", command=mark_paid)
    button_confirm.pack(pady=10)


def load_show_savings():
    clear_content()
    c.execute('SELECT SUM(amount) FROM incomes')
    total_income = c.fetchone()[0] or 0
    c.execute('SELECT SUM(amount) FROM expenses')
    total_expense = c.fetchone()[0] or 0

    savings = total_income - total_expense
    goal = 5000  # Например, цель накоплений

    progress = min(savings / goal, 1.0)

    label = ctk.CTkLabel(content, text=f"Накопления: {savings:.2f} € из {goal:.2f} €", font=("Arial", 20))
    label.pack(pady=20)

    progress_bar = ctk.CTkProgressBar(content, width=400)
    progress_bar.pack(pady=10)
    progress_bar.set(progress)

# Кнопки на боковой панели
button1 = ctk.CTkButton(sidebar, text="Добавить доход", command=load_add_income)
button1.pack(pady=10, padx=10)

button2 = ctk.CTkButton(sidebar, text="Добавить расход", command=load_add_expense)
button2.pack(pady=10, padx=10)

button3 = ctk.CTkButton(sidebar, text="График расходов", command=load_expense_chart)
button3.pack(pady=10, padx=10)

button4 = ctk.CTkButton(sidebar, text="История по месяцу", command=load_monthly_history)
button4.pack(pady=10, padx=10)

button5 = ctk.CTkButton(sidebar, text="Анализ бюджета", command=load_budget_analysis)
button5.pack(pady=10, padx=10)

button6 = ctk.CTkButton(sidebar, text="Показать кредиты", command=load_show_credits)
button6.pack(pady=10, padx=10)

button7 = ctk.CTkButton(sidebar, text="Показать баланс", command=load_show_balance)
button7.pack(pady=10, padx=10)

button8 = ctk.CTkButton(sidebar, text="Неоплаченные платежи", command=load_unpaid_payments)
button8.pack(pady=10, padx=10)

button9 = ctk.CTkButton(sidebar, text="Оплатить платеж", command=load_mark_payment)
button9.pack(pady=10, padx=10)

button10 = ctk.CTkButton(sidebar, text="Накопления", command=load_show_savings)
button10.pack(pady=10, padx=10)


# Запуск приложения
app.mainloop()

# Закрытие соединения с базой данных
conn.close()
