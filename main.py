import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from datetime import datetime


connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT, ISSUE_DATE TEXT)'
)


def issuer_card():
    return sd.askstring('Issuer Card ID', 'Enter the Issuer\'s Card ID:')

def display_records():
    tree.delete(*tree.get_children())
    cursor.execute('SELECT * FROM Library')
    for record in cursor.fetchall():
        tree.insert('', END, values=record)

def clear_fields():
    bk_status.set('Available')
    bk_id.set(''); bk_name.set(''); author_name.set(''); card_id.set('')
    bk_id_entry.config(state='normal')

def add_record():
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    
    try:
        connector.execute('INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                          (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
        connector.commit()
        clear_fields(); display_records()
        mb.showinfo('Success', 'Record added successfully')
    except sqlite3.IntegrityError:
        mb.showerror('Error', 'Book ID already exists')

def view_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to view')
        return

    current = tree.item(tree.focus())['values']
    bk_name.set(current[0]); bk_id.set(current[1])
    author_name.set(current[2]); bk_status.set(current[3])
    card_id.set(current[4])

def update_record():
    cursor.execute('UPDATE Library SET BK_NAME=?, AUTHOR_NAME=?, BK_STATUS=?, CARD_ID=? WHERE BK_ID=?',
                   (bk_name.get(), author_name.get(), bk_status.get(), card_id.get(), bk_id.get()))
    connector.commit()
    clear_fields(); display_records()

def remove_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to delete')
        return

    current = tree.item(tree.focus())['values'][1]
    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (current,))
    connector.commit()
    clear_fields(); display_records()


def change_availability():
    if not tree.selection():
        mb.showerror('Error', 'Please select a book')
        return

    current_item = tree.item(tree.focus())['values']
    bk_id = current_item[1]; status = current_item[3]

    if status == 'Issued':
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=?, ISSUE_DATE=? WHERE BK_ID=?',
                       ('Available', 'N/A', 'N/A', bk_id))
        mb.showinfo('Returned', 'Book returned successfully')
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=?, ISSUE_DATE=? WHERE BK_ID=?',
                       ('Issued', issuer_card(), datetime.now().strftime('%Y-%m-%d'), bk_id))
        mb.showinfo('Issued', 'Book issued successfully')

    connector.commit()
    display_records()


def calculate_fine():
    if not tree.selection():
        mb.showerror('Error', 'Please select a book')
        return

    current_item = tree.item(tree.focus())['values']
    issue_date = current_item[5]

    if issue_date == 'N/A':
        mb.showinfo('Fine', 'No fine, book is available')
        return

    days_overdue = (datetime.now() - datetime.strptime(issue_date, '%Y-%m-%d')).days - 14
    if days_overdue > 0:
        fine = days_overdue * 2
        mb.showinfo('Fine', f'Total fine: ₹{fine}')
    else:
        mb.showinfo('Fine', 'No fine applicable')


def search_book():
    search_term = sd.askstring('Search Book', 'Enter Book Name or Book ID:')
    tree.delete(*tree.get_children())
    cursor.execute('SELECT * FROM Library WHERE BK_NAME LIKE ? OR BK_ID LIKE ?', (f'%{search_term}%', f'%{search_term}%'))
    for record in cursor.fetchall():
        tree.insert('', END, values=record)


root = Tk()
root.title('Library Management System')
root.geometry('1010x600')
root.config(bg='CadetBlue')

# Define StringVar for inputs
bk_status = StringVar(); bk_name = StringVar()
bk_id = StringVar(); author_name = StringVar()
card_id = StringVar()

# Header
header_frame = Frame(root, bg='Teal')
header_frame.pack(side=TOP, fill=X)
Label(header_frame, text='Library Management System', bg='Teal', fg='white', font=('Helvetica', 20, 'bold')).pack(pady=10)

# Left frame for book details
left_frame = Frame(root, bg='LightCyan')
left_frame.place(x=20, y=70, width=320, height=500)

# Right frame for buttons and tree view
right_frame = Frame(root, bg='PowderBlue')
right_frame.place(x=360, y=70, width=600, height=500)

# Entry fields
Label(left_frame, text='Book ID:', font=('Arial', 12), bg='LightCyan').pack(pady=10)
bk_id_entry = Entry(left_frame, textvariable=bk_id, font=('Arial', 12))
bk_id_entry.pack(pady=5)

Label(left_frame, text='Book Name:', font=('Arial', 12), bg='LightCyan').pack(pady=10)
Entry(left_frame, textvariable=bk_name, font=('Arial', 12)).pack(pady=5)

Label(left_frame, text='Author Name:', font=('Arial', 12), bg='LightCyan').pack(pady=10)
Entry(left_frame, textvariable=author_name, font=('Arial', 12)).pack(pady=5)

Label(left_frame, text='Status:', font=('Arial', 12), bg='LightCyan').pack(pady=10)
OptionMenu(left_frame, bk_status, 'Available', 'Issued').pack(pady=5)

# Buttons
button_frame = Frame(left_frame, bg='LightCyan')
button_frame.pack(pady=20)

Button(button_frame, text='Add Record', bg='MediumSeaGreen', fg='white', font=('Arial', 12), command=add_record).grid(row=0, column=0, padx=5)
Button(button_frame, text='Update Record', bg='DodgerBlue', fg='white', font=('Arial', 12), command=update_record).grid(row=0, column=1, padx=5)
Button(button_frame, text='Delete Record', bg='Tomato', fg='white', font=('Arial', 12), command=remove_record).grid(row=0, column=2, padx=5)
Button(button_frame, text='Clear Fields', bg='Gold', fg='black', font=('Arial', 12), command=clear_fields).grid(row=0, column=3, padx=5)

# Action Buttons
Button(right_frame, text='Search Book', bg='MediumBlue', fg='white', font=('Arial', 12), command=search_book).pack(pady=10)
Button(right_frame, text='Change Availability', bg='MediumBlue', fg='white', font=('Arial', 12), command=change_availability).pack(pady=10)
Button(right_frame, text='Calculate Fine', bg='MediumBlue', fg='white', font=('Arial', 12), command=calculate_fine).pack(pady=10)

# Treeview for displaying records
tree = ttk.Treeview(right_frame, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID', 'Issue Date'), show='headings')
tree.heading('Book Name', text='Book Name')
tree.heading('Book ID', text='Book ID')
tree.heading('Author', text='Author')
tree.heading('Status', text='Status')
tree.heading('Card ID', text='Card ID')
tree.heading('Issue Date', text='Issue Date')
tree.pack(fill=BOTH, expand=True, pady=20)

display_records()

root.mainloop()