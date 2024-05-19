import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import sqlite3


class Veritabani:
    def __init__(self):
        self.conn = sqlite3.connect("seyahat.db")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS rotalar (id INTEGER PRIMARY KEY, sehir TEXT, details TEXT)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS konaklamalar (id INTEGER PRIMARY KEY, rota_id INTEGER, name TEXT, tur TEXT, price INTEGER, rating REAL, address TEXT, website TEXT, image TEXT)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS yorumlar (id INTEGER PRIMARY KEY, konaklama_id INTEGER, kullanici_adi TEXT, yorum TEXT)")
        self.conn.commit()

    def sehir_ekle(self, sehir):
        self.cur.execute("INSERT INTO rotalar VALUES (NULL, ?, ?)", (sehir, ""))
        self.conn.commit()

    def sehirler_getir(self):
        self.cur.execute("SELECT sehir FROM rotalar")
        return [row[0] for row in self.cur.fetchall()]

    def konaklama_ekle(self, rota_id, name, tur, price, rating, address, website, image):
        self.cur.execute("INSERT INTO konaklamalar VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (rota_id, name, tur, price, rating, address, website, image))
        self.conn.commit()

    def konaklama_getir(self, sehir, tur=None, fiyat_min=None, fiyat_max=None, rating_min=None, rating_max=None):
        query = "SELECT * FROM konaklamalar WHERE rota_id IN (SELECT id FROM rotalar WHERE sehir=?)"
        params = [sehir]

        if tur and tur != "Tümü":
            query += " AND tur=?"
            params.append(tur)

        if fiyat_min:
            query += " AND price>=?"
            params.append(fiyat_min)

        if fiyat_max:
            query += " AND price<=?"
            params.append(fiyat_max)

        if rating_min:
            query += " AND rating>=?"
            params.append(rating_min)

        if rating_max:
            query += " AND rating<=?"
            params.append(rating_max)

        self.cur.execute(query, params)
        return self.cur.fetchall()

    def yorum_ekle(self, konaklama_id, kullanici_adi, yorum):
        self.cur.execute("INSERT INTO yorumlar VALUES (NULL, ?, ?, ?)", (konaklama_id, kullanici_adi, yorum))
        self.conn.commit()

    def yorumlar_getir(self, konaklama_id):
        self.cur.execute("SELECT * FROM yorumlar WHERE konaklama_id=?", (konaklama_id,))
        return self.cur.fetchall()


class KonaklamaEklemePenceresi:
    def __init__(self, master, veritabani, sehir, uygulama):
        self.master = master
        self.veritabani = veritabani
        self.sehir = sehir
        self.uygulama = uygulama

        self.pencere = tk.Toplevel(master)
        self.pencere.title("Konaklama Ekle")
        self.pencere.geometry("400x400")

        self.label_konaklama = tk.Label(self.pencere, text="Konaklama Adı:")
        self.label_konaklama.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_konaklama = tk.Entry(self.pencere, width=30)
        self.entry_konaklama.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.label_tur = tk.Label(self.pencere, text="Konaklama Türü:")
        self.label_tur.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.combobox_tur = ttk.Combobox(self.pencere, width=27, state="readonly")
        self.combobox_tur['values'] = ('Otel', 'Pansiyon', 'Apart', 'Kamp Alanı', 'Diğer')
        self.combobox_tur.current(0)
        self.combobox_tur.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.label_fiyat = tk.Label(self.pencere, text="Fiyat (TL):")
        self.label_fiyat.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry_fiyat = tk.Entry(self.pencere, width=30)
        self.entry_fiyat.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.label_rating = tk.Label(self.pencere, text="Rating:")
        self.label_rating.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.entry_rating = tk.Entry(self.pencere, width=30)
        self.entry_rating.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.label_adres = tk.Label(self.pencere, text="Adres:")
        self.label_adres.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.entry_adres = tk.Entry(self.pencere, width=30)
        self.entry_adres.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.label_website = tk.Label(self.pencere, text="Website URL:")
        self.label_website.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.entry_website = tk.Entry(self.pencere, width=30)
        self.entry_website.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.label_resim = tk.Label(self.pencere, text="Resim URL:")
        self.label_resim.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.entry_resim = tk.Entry(self.pencere, width=30)
        self.entry_resim.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.button_ekle = tk.Button(self.pencere, text="Konaklama Ekle", command=self.konaklama_ekle)
        self.button_ekle.grid(row=7, column=1, padx=10, pady=10, sticky="w")

    def konaklama_ekle(self):
        konaklama_bilgileri = self.entry_konaklama.get()
        tur = self.combobox_tur.get()
        fiyat = self.entry_fiyat.get()
        rating = self.entry_rating.get()
        adres = self.entry_adres.get()
        website = self.entry_website.get()
        resim = self.entry_resim.get()

        if konaklama_bilgileri and tur and fiyat and rating and adres and website and resim:
            rota_id = self.veritabani.cur.execute("SELECT id FROM rotalar WHERE sehir=?", (self.sehir,)).fetchone()[0]
            self.veritabani.konaklama_ekle(rota_id, konaklama_bilgileri, tur, int(fiyat), float(rating), adres, website,
                                           resim)
            messagebox.showinfo("Başarılı", "Konaklama başarıyla eklendi.")
            self.pencere.destroy()
            self.uygulama.konaklama_goster()
        else:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")


class KonaklamaAramaPenceresi:
    def __init__(self, master, veritabani, sehir, uygulama):
        self.master = master
        self.veritabani = veritabani
        self.sehir = sehir
        self.uygulama = uygulama

        self.pencere = tk.Toplevel(master)
        self.pencere.title("Konaklama Arama")
        self.pencere.geometry("400x400")

        self.label_tur = tk.Label(self.pencere, text="Konaklama Türü:")
        self.label_tur.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.combobox_tur = ttk.Combobox(self.pencere, width=27, state="readonly")
        self.combobox_tur['values'] = ('Tümü', 'Otel', 'Pansiyon', 'Apart', 'Kamp Alanı', 'Diğer')
        self.combobox_tur.current(0)
        self.combobox_tur.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.label_fiyat_min = tk.Label(self.pencere, text="Min Fiyat (TL):")
        self.label_fiyat_min.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry_fiyat_min = tk.Entry(self.pencere, width=15)
        self.entry_fiyat_min.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.label_fiyat_max = tk.Label(self.pencere, text="Max Fiyat (TL):")
        self.label_fiyat_max.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry_fiyat_max = tk.Entry(self.pencere, width=15)
        self.entry_fiyat_max.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.label_rating_min = tk.Label(self.pencere, text="Min Rating:")
        self.label_rating_min.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.entry_rating_min = tk.Entry(self.pencere, width=15)
        self.entry_rating_min.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.label_rating_max = tk.Label(self.pencere, text="Max Rating:")
        self.label_rating_max.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.entry_rating_max = tk.Entry(self.pencere, width=15)
        self.entry_rating_max.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.label_arama = tk.Label(self.pencere, text="Aranacak Konaklama:")
        self.label_arama.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.entry_arama = tk.Entry(self.pencere, width=30)
        self.entry_arama.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.button_ara = tk.Button(self.pencere, text="Ara", command=self.konaklama_ara)
        self.button_ara.grid(row=6, column=1, padx=10, pady=10, sticky="w")

    def konaklama_ara(self):
        tur = self.combobox_tur.get()
        fiyat_min = self.entry_fiyat_min.get()
        fiyat_max = self.entry_fiyat_max.get()
        rating_min = self.entry_rating_min.get()
        rating_max = self.entry_rating_max.get()
        keyword = self.entry_arama.get()
        if keyword:
            konaklamalar = self.veritabani.konaklama_getir(self.sehir, tur, fiyat_min, fiyat_max, rating_min,
                                                           rating_max)
            self.goster(konaklamalar)

    def goster(self, konaklamalar):
        self.liste = ttk.Treeview(self.pencere)
        self.liste["columns"] = ("Type", "Price", "Rating")
        self.liste.heading("#0", text="Konaklama Adı", anchor="w")
        self.liste.heading("Type", text="Tür", anchor="w")
        self.liste.heading("Price", text="Fiyat (TL)", anchor="w")
        self.liste.heading("Rating", text="Rating", anchor="w")
        self.liste.column("#0", width=200, stretch=tk.NO)
        self.liste.column("Type", width=100, stretch=tk.NO)
        self.liste.column("Price", width=100, stretch=tk.NO)
        self.liste.column("Rating", width=100, stretch=tk.NO)
        self.liste.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        for konaklama in konaklamalar:
            self.liste.insert("", "end", text=konaklama[2], values=(konaklama[3], konaklama[4], konaklama[5]))


class SeyahatUygulamasi:
    def __init__(self, master):
        self.master = master
        self.master.title("Seyahat Planlama Uygulaması")
        self.master.geometry("800x600")

        self.veritabani = Veritabani()

        self.frame_filtre = ttk.Frame(master)
        self.frame_filtre.pack(side=tk.LEFT, fill=tk.Y)

        self.label_sehir = tk.Label(self.frame_filtre, text="Şehir:")
        self.label_sehir.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.combobox_sehir = ttk.Combobox(self.frame_filtre, width=27, state="readonly")
        self.combobox_sehir['values'] = self.veritabani.sehirler_getir()
        self.combobox_sehir.current(0)
        self.combobox_sehir.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.label_konaklama = tk.Label(self.frame_filtre, text="Konaklama Türü:")
        self.label_konaklama.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.combobox_konaklama = ttk.Combobox(self.frame_filtre, width=27, state="readonly")
        self.combobox_konaklama['values'] = ('Tümü', 'Otel', 'Pansiyon', 'Apart', 'Kamp Alanı', 'Diğer')
        self.combobox_konaklama.current(0)
        self.combobox_konaklama.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.label_fiyat_min = tk.Label(self.frame_filtre, text="Min Fiyat (TL):")
        self.label_fiyat_min.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry_fiyat_min = tk.Entry(self.frame_filtre, width=15)
        self.entry_fiyat_min.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.label_fiyat_max = tk.Label(self.frame_filtre, text="Max Fiyat (TL):")
        self.label_fiyat_max.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.entry_fiyat_max = tk.Entry(self.frame_filtre, width=15)
        self.entry_fiyat_max.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.label_rating_min = tk.Label(self.frame_filtre, text="Min Rating:")
        self.label_rating_min.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.entry_rating_min = tk.Entry(self.frame_filtre, width=15)
        self.entry_rating_min.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.label_rating_max = tk.Label(self.frame_filtre, text="Max Rating:")
        self.label_rating_max.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.entry_rating_max = tk.Entry(self.frame_filtre, width=15)
        self.entry_rating_max.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.button_ara = tk.Button(self.frame_filtre, text="Konaklama Ara", command=self.konaklama_goster)
        self.button_ara.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.button_ekle = tk.Button(self.frame_filtre, text="Konaklama Ekle", command=self.konaklama_ekle)
        self.button_ekle.grid(row=7, column=1, padx=10, pady=10, sticky="w")

        self.button_yorum = tk.Button(self.frame_filtre, text="Yorum Ekle", command=self.yorum_ekle)
        self.button_yorum.grid(row=8, column=1, padx=10, pady=10, sticky="w")

        self.frame_icerik = ttk.Frame(master)
        self.frame_icerik.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        self.scrolled_text = scrolledtext.ScrolledText(self.frame_icerik, wrap=tk.WORD, width=60, height=20)
        self.scrolled_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.konaklama_goster()

        self.button_kilavuz = tk.Button(master, text="Uygulama Kılavuzu", command=self.kilavuz_goster)
        self.button_kilavuz.place(relx=1.0, rely=1.0, anchor=tk.SE)

    def konaklama_goster(self):
        sehir = self.combobox_sehir.get()
        tur = self.combobox_konaklama.get()
        fiyat_min = self.entry_fiyat_min.get()
        fiyat_max = self.entry_fiyat_max.get()
        rating_min = self.entry_rating_min.get()
        rating_max = self.entry_rating_max.get()

        konaklamalar = self.veritabani.konaklama_getir(sehir, tur, fiyat_min, fiyat_max, rating_min, rating_max)

        self.scrolled_text.delete(1.0, tk.END)
        for konaklama in konaklamalar:
            self.scrolled_text.insert(tk.END,
                                      f"Konaklama Adı: {konaklama[2]}\nTür: {konaklama[3]}\nFiyat: {konaklama[4]} TL\nRating: {konaklama[5]}\nAdres: {konaklama[6]}\nWebsite: {konaklama[7]}\n\n")

    def konaklama_ekle(self):
        sehir = self.combobox_sehir.get()
        pencere = KonaklamaEklemePenceresi(self.master, self.veritabani, sehir, self)

    def yorum_ekle(self):
        pencere = simpledialog.askstring("Yorum Ekle", "Yorumunuzu buraya yazın:", parent=self.master)
        if pencere is not None:
            sehir = self.combobox_sehir.get()
            self.veritabani.yorum_ekle(sehir, pencere)
            self.konaklama_goster()

    def kilavuz_goster(self):
        kilavuz = """
        Uygulama Kılavuzu

        1. Şehir seçin: Şehir seçim kutusundan bir şehir seçin.

        2. Türü seçin: Konaklamak istediğiniz türü seçin veya "Tümü" seçeneğini bırakın.

        3. Fiyat aralığını belirleyin: Minimum ve maksimum fiyatları girin veya boş bırakın.

        4. Rating aralığını belirleyin: Minimum ve maksimum rating'i girin veya boş bırakın.

        5. "Konaklama Ara" butonuna tıklayın: Belirlediğiniz kriterlere göre konaklama yerlerini filtreleyin.

        6. "Konaklama Ekle" butonuna tıklayarak yeni bir konaklama yeri ekleyin.

        7. "Yorum Ekle" butonuna tıklayarak bir konaklama yeri için yorum ekleyin.
        """
        messagebox.showinfo("Uygulama Kılavuzu", kilavuz)


root = tk.Tk()
uygulama = SeyahatUygulamasi(root)
root.mainloop()
