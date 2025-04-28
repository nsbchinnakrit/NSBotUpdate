import tkinter as tk
child = tk.Tk()
def on_closing():
    child.destroy()

def handle_click(event):
    child.after_idle(on_closing)

def move(event):
    child.geometry(f'+{event.x_child-137}+{event.y_child-33}')

def run_window(content):
    child = tk.Tk()
    child.title("NSBot Update")
    child.geometry('272x62')
    child.config(bg='#00BCFF')
    nofity_frame = tk.LabelFrame(child)
    nofity_frame.grid(padx=(15), pady=(15))
    nofity_Label = tk.Label(nofity_frame, text=f"\n{content}\n", font=("Segoe UI",  12))
    nofity_frame.pack(padx=(5), pady=(5))
    nofity_Label.pack(padx=(10), pady=(5))
    child.update()
    child.minsize(child.winfo_width(), child.winfo_height())
    x_cordinate = int((child.winfo_screenwidth() / 2) - (child.winfo_width() / 2))
    y_cordinate = int((child.winfo_screenheight() / 2) - (child.winfo_height() / 2))
    child.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))
    child.overrideredirect(1)
    child.attributes('-topmost', True)
    child.bind('<Button-1>', handle_click)
    child.mainloop()

if __name__ == "__main__":
    content = "ระบบได้ Accept co-op quest โปรดตรวจสอบเควสของคุณ"
    # run_window(content)
