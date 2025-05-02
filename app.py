import tkinter as tk
from tkinter import filedialog, ttk
import csv
from datetime import datetime

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer and Search")
        self.data = []

        # Search frame
        search_frame = tk.Frame(root)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search by ID:").grid(row=0, column=0)
        self.search_id = tk.Entry(search_frame)
        self.search_id.grid(row=0, column=1)

        tk.Label(search_frame, text="Search by Ciudad:").grid(row=0, column=2)
        self.search_ciudad = tk.Entry(search_frame)
        self.search_ciudad.grid(row=0, column=3)

        tk.Label(search_frame, text="Search by Edad:").grid(row=0, column=4)
        self.search_edad = tk.Entry(search_frame)
        self.search_edad.grid(row=0, column=5)

        # Bind typing events to trigger search
        self.search_id.bind("<KeyRelease>", lambda e: self.search())
        self.search_ciudad.bind("<KeyRelease>", lambda e: self.search())
        self.search_edad.bind("<KeyRelease>", lambda e: self.search())

        tk.Button(search_frame, text="Reset", command=self.reset).grid(row=0, column=7)
        tk.Button(search_frame, text="Load CSV", command=self.load_csv).grid(row=0, column=8)

        # Table
        self.tree = ttk.Treeview(root, columns=("id", "nombres", "apellidos", "fecha_nacimiento", "fecha_registro", "ciudad", "email"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Log console
        self.log_console = tk.Text(root, height=4, bg="black", fg="lime", font=("Courier", 10))
        self.log_console.pack(fill=tk.X)
        self.log("Application started.")

    def log(self, message):
        self.log_console.insert(tk.END, f"{message}\n")
        self.log_console.see(tk.END)

    def load_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        self.data = []
        self.log(f"Loading CSV from: {filepath}")

        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Validate id
                    row["id"] = int(row["id"])

                    # Validate strings
                    for field in ["nombres", "apellidos", "ciudad", "email"]:
                        if not isinstance(row[field], str):
                            raise ValueError(f"{field} must be a string")

                    # Validate date format MM/DD/YYYY
                    row["fecha_nacimiento"] = self.validate_date(row["fecha_nacimiento"], "fecha_nacimiento")
                    row["fecha_registro"] = self.validate_date(row["fecha_registro"], "fecha_registro")

                    # Calculate edad
                    row["edad"] = self.calculate_age(row["fecha_nacimiento"])
                    self.data.append(row)
                except Exception as e:
                    self.log(f"Invalid row skipped: {row} -> {e}")

        self.populate_table(self.data)
        self.log(f"CSV Loaded. {len(self.data)} valid rows displayed.")

    def validate_date(self, date_str, field_name):
        try:
            return datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            raise ValueError(f"{field_name} must be in m/d/yyyy format")

    def populate_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=(
            row["id"],
            row["nombres"],
            row["apellidos"],
            f"{row['fecha_nacimiento'].strftime('%m/%d/%Y')} (Edad: {row['edad']})",
            row["fecha_registro"].strftime("%m/%d/%Y"),
            row["ciudad"],
            row["email"]
        ))


    def calculate_age(self, birthdate):
        today = datetime.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    def search(self):
        id_search = self.search_id.get().strip().lower()
        ciudad_search = self.search_ciudad.get().strip().lower()
        edad_search = self.search_edad.get().strip()

        filtered = self.data
        if id_search:
            filtered = [row for row in filtered if str(row["id"]) == id_search]
        if ciudad_search:
            filtered = [row for row in filtered if ciudad_search in row["ciudad"].lower()]
        if edad_search.isdigit():
            filtered = [row for row in filtered if row["edad"] == int(edad_search)]

        self.populate_table(filtered)

        if filtered:
            self.log(f"Search successful. {len(filtered)} registries found.")
        else:
            self.log("No registries found for this query.")
    
    def reset(self):
        self.search_id.delete(0, tk.END)
        self.search_ciudad.delete(0, tk.END)
        self.search_edad.delete(0, tk.END)
        self.search()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.geometry("1100x500")
    root.mainloop()
