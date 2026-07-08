import tkinter as tk
def click_button(text):
    current = entry.get()
    if text == '=':
        try:
            result = eval(current)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except Exception as e:
            entry.delete(0, tk.END)
            entry.insert(0, 'Error')
    elif text == 'C':
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, text)
root = tk.Tk()
root.title("CALCULATOR")
entry = tk.Entry(root, width=50, borderwidth=10)
entry.grid(row=0, column=0, columnspan=4)
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    'C', '0', '=', '+'
]

row, col = 1, 0
for button in buttons:
    tk.Button(root, text=button, padx=40, pady=20, command=lambda b=button: click_button(b)).grid(row=row,
column=col)
    col += 1
    if col > 3:
        row += 1
        col = 0

root.mainloop()