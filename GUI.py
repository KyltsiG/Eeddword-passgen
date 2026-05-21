import tkinter as tk
from tkinter import ttk, messagebox
import string
import math
import secrets
from zxcvbn import zxcvbn 
from PIL import Image, ImageTk


POOLS = {
    "Uppercase  (A–Ö)":  string.ascii_uppercase + "ÅÄÖ",
    "Lowercase  (a–ö)":  string.ascii_lowercase + "åäö",
    "Digits     (0–9)":  string.digits,
    "Symbols  (!&%$…)":   "!#$%&*+/:=?@~",
    "Minus & underscore (-_)": "-_",
    "Brackets  ([]{}()<>)": "[]{}()<>",
}




def calculate_strength(password: str) -> float:
    charset: set[str] = set()
    for pool in POOLS.values():
        for ch in password:
            if ch in pool:
                charset |= set(pool)
    size = len(charset) if charset else max(len(set(password)), 1)
    return math.log2(size) * len(password) if password else 0.0

def calculate_crack_time(password: str) -> dict[str, str]:
    if not password:
        return {"fast": "-", "slow": "-"}
    elif len(password) > 72:
        return {"fast": "centuries", "slow": "centuries"}
    data = zxcvbn(password)
    data1= data["crack_times_display"]["offline_fast_hashing_1e10_per_second"]
    data2 = data["crack_times_display"]["offline_slow_hashing_1e4_per_second"]
    return {"fast": data1, "slow": data2}

def strength_label(bits: float) -> tuple[str, str]:
    """Return (label, hex-colour) based on bit count."""
    if bits == 0:
        return "—", "#6b7280"
    if bits < 40:
        return f"Weak  ({bits:.0f} bits)", "#ef4444"
    if bits < 72:
        return f"Fair  ({bits:.0f} bits)", "#f97316"
    if bits < 100:
        return f"Strong  ({bits:.0f} bits)", "#eab308"
    if bits < 128:
        return f"Very Strong  ({bits:.0f} bits)", "#22c55e"
    return f"Excellent  ({bits:.0f} bits)", "#06b6d4"




# Main application 

class PasswordGeneratorApp(tk.Tk):
    PAD = 18
    CORNER = 8
    cracktime = {"fast": "ei", "slow": "ei"}
 

    def __init__(self):
        super().__init__()
        self.title("Eeddword")

        try:
            icon_img = Image.open("logo.png")
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(False, icon_photo)
            self._icon_photo = icon_photo
        except Exception as e:
           print(f"Ikonin lataus epäonnistui: {e}")


        self.configure(bg="#0f1117")
        self.minsize(400, 630)
        self._checkbox_vars: dict[str, tk.BooleanVar] = {}
        self._build_ui()

    # UI construction 

    def _build_ui(self):
        root_frame = tk.Frame(self, bg="#0f1117", padx=self.PAD * 2, pady=self.PAD * 2)
        root_frame.pack(fill="both", expand=True)

        # Title
        tk.Label(
            root_frame, text="Eeddword Password Generator",
            font=("Helvetica", 13, "bold"),
            fg="#e2e8f0", bg="#0f1117",
        ).pack(anchor="w", pady=(0, self.PAD))

        # Character options 
        options_frame = tk.LabelFrame(
            root_frame, text=" Character sets ",
            font=("Courier New", 9), fg="#6b7280",
            bg="#1a1d27", bd=1, relief="flat",
            padx=self.PAD, pady=10,
        )
        options_frame.pack(fill="x", pady=(0, self.PAD))

        for label, pool in POOLS.items():
            var = tk.BooleanVar(value=True)
            self._checkbox_vars[label] = var
            cb = tk.Checkbutton(
                options_frame, text=label,
                variable=var, 
                font=("Helvetica", 10),
                fg="#cbd5e1", bg="#1a1d27",
                selectcolor="#0f1117",
                activeforeground="#f8fafc",
                activebackground="#1a1d27",
                bd=0, highlightthickness=0,
                cursor="hand2",
            )
            cb.pack(anchor="w", pady=2)

        # Length slider 
        length_frame = tk.Frame(root_frame, bg="#0f1117")
        length_frame.pack(fill="x", pady=(0, self.PAD))

        self._length_var = tk.IntVar(value=20)

        tk.Label(
            length_frame, text="Length:",
            font=("Helvetica", 10), fg="#6b7280", bg="#0f1117",
        ).pack(side="left")

        self._length_label = tk.Label(
            length_frame, text="20",
            font=("Helvetica", 10, "bold"), fg="#e2e8f0", bg="#0f1117", width=3,
        )
        self._length_label.pack(side="right")

        slider = ttk.Scale(
            length_frame, from_=4, to=72,
            orient="horizontal", variable=self._length_var,
            command=lambda val: self.update_length_label(self._length_var, self._length_label),
        )
        slider.pack(side="left", fill="x", expand=True, padx=(10, 6))

        self._style_slider()

        # Generate button 
        gen_btn = tk.Button(
            root_frame, text="⟳  Generate a Password",
            font=("Helvetica", 11, "bold"),
            fg="#0f1117", bg="#60a5fa",
            activeforeground="#0f1117", activebackground="#93c5fd",
            bd=0, highlightthickness=0,
            pady=12, cursor="hand2", 
            command=self._generate_password,
        )
        
        gen_btn.pack(fill="x", pady=(0, self.PAD))


        self._bar_canvas = tk.Canvas(
            root_frame, height=4, bg="#1a1d27",
            bd=0, highlightthickness=0,
        )
        self._bar_canvas.pack(fill="x", pady=(0, self.PAD))
        root_frame.columnconfigure(0, weight=1)

        self._notif_label = tk.Label(
            root_frame, text="",
            font=("Helvetica", 9, "bold"),
            fg="#22c55e", bg="#0f1117", 
            pady=0,
        )
        self._notif_label.pack()


        # Password field + copy button 
        pw_outer = tk.Frame(root_frame, bg="#1a1d27", bd=1, relief="flat")
        pw_outer.pack(fill="x", pady=(0, 6))

        self._pw_var = tk.StringVar(value="")
        self._pw_var.trace_add("write", self._on_pw_change)

        pw_entry = tk.Entry(
            pw_outer, textvariable=self._pw_var,
            font=("Helvetica", 9),
            fg="#f1f5f9", bg="#1a1d27",
            insertbackground="#60a5fa",
            bd=0, highlightthickness=0,
            relief="flat", 
        )
        pw_entry.pack(side="left", fill="both", expand=True, padx=(12, 0), ipady=10)

        copy_btn = tk.Button(
            pw_outer, text="⎘ Copy",
            font=("Helvetica", 10, "bold"),
            fg="#0f1117", bg="#60a5fa",
            activeforeground="#0f1117", activebackground="#93c5fd",
            bd=0, highlightthickness=0,
            padx=14, pady=10,
            cursor="hand2",
            command=self._copy_to_clipboard,
        )
        copy_btn.pack(side="right")
       
        strength_title = tk.Label(
            root_frame, text="Password strength:",
            font=("Helvetica", 12), fg="#60a5fa", bg="#0f1117",
        )
        strength_title.pack(pady=(0, 4))
       
        # Bit-strength bar 
        self._strength_label = tk.Label(
            root_frame, text="",
            font=("Helvetica", 10, "bold"),
            fg="#6b7280", bg="#0f1117", anchor="w",
        )
        self._strength_label.pack(pady=(0, 4))

   
        
        self.crack_time_label = tk.Label(
            root_frame, 
            text=f"Cracking Times: \nSpecialized breach equipment: {self.cracktime['fast']} \nGaming PC: {self.cracktime['slow']}",
            font=("Helvetica", 10), fg="#6b7280", bg="#0f1117",
            wraplength=350, justify="left",
        )
        self.crack_time_label.pack(fill="x", pady=(0, self.PAD))
   

    def _style_slider(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Horizontal.TScale",
            background="#0f1117",
            troughcolor="#1a1d27",
            sliderthickness=16,
        )
        
    def update_length_label(self, length_var: tk.IntVar, label: tk.Label):
        length = length_var.get()
        label.config(text=str(length))

    # Luo characters mekkijonon jossa on kaikki merkit joita käytetään salasanassa.
    def _get_characters(self):
        characters = ""

        for label, var in self._checkbox_vars.items():
            if var.get():
                characters += POOLS[label]

        return characters


    def _on_pw_change(self, *args):
        """Kutsutaan automaattisesti, kun self._pw_var muuttuu."""
        
        password = self._pw_var.get()
        
    
        times = calculate_crack_time(password)
        self.crack_time_label.config(
            text=f"Cracking Times: \nSpecialized breach equipment: {times['fast']} \nGaming PC: {times['slow']}"
        )
     
        bits = calculate_strength(password)
        label, color = strength_label(bits)
        self._strength_label.config(text=label, fg=color)

    # Luo salasanan
    def _generate_password(self):
        
        characters = self._get_characters()
        length = self._length_var.get()

        if not characters:
            messagebox.showerror("Virhe", "Valitse merkit")
            return

        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        self._pw_var.set(password)

    
    def _copy_to_clipboard(self):
        password = self._pw_var.get()
        if not password:
            return
            
        self.clipboard_clear()
        self.clipboard_append(password)
        
        self._notif_label.config(text="Password copied to clipboard!", fg="#22c55e")
        
        self.after(2500, lambda: self._notif_label.config(text=""))


# Entry point 

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()