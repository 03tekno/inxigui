import gi
import subprocess
import os
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib

class InxiSadePanel(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.debian.inxi.final')
        self.aktif_buton = None 

    def do_activate(self):
        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("Sistem Bilgi Merkezi (Inxi Gui)")

        width, height = 1000, 700
            
        self.win.set_default_size(width, height)

        ana_kutu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.win.set_content(ana_kutu)

        # Üst Araç Çubuğu
        header = Adw.HeaderBar()
        self.spinner = Gtk.Spinner()
        header.pack_end(self.spinner)
        ana_kutu.append(header)

        # İçerik Düzeni
        paned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        ana_kutu.append(paned)

        # SOL MENÜ
        self.sol_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.sol_menu.set_size_request(240, -1)
        self.sol_menu.set_margin_start(15)
        self.sol_menu.set_margin_end(15)
        self.sol_menu.set_margin_top(15)
        self.sol_menu.set_margin_bottom(15)
        
        paned.append(self.sol_menu)

        kategoriler = [
            ("🏠 Sistem Özeti", "-b"), ("💻 İşlemci (CPU)", "-C"),
            ("🖼️ Ekran Kartı (GPU)", "-G"), ("💾 Bellek (RAM)", "-m"),
            ("💽 Disk Bilgisi", "-D"), ("🌐 Ağ Kartları", "-N"),
            ("🔊 Ses Sistemi", "-A"), ("🌡️ Sıcaklıklar", "-s"),
            ("📦 Yazılım Depoları", "-r"), ("🔋 Pil Durumu", "-B"),
            ("📑 Tam Rapor", "-F")
        ]

        for isim, param in kategoriler:
            # Butonu oluştur
            btn = Gtk.Button(label=isim)
            btn.add_css_class("pill") # Yuvarlak stil
            
            # Metni sola yasla
            label = btn.get_child()
            if isinstance(label, Gtk.Label):
                label.set_xalign(0)
                label.set_margin_start(10)
            
            btn.param = param
            btn.connect('clicked', self.on_button_clicked)
            self.sol_menu.append(btn)
            
            # Başlangıçta "Sistem Özeti" butonunu seçili yap
            if param == "-b":
                self.vurgula_butonu(btn)

        # SAĞ PANEL (Metin Çıktısı)
        vbox_sag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_sag.set_hexpand(True)
        vbox_sag.set_margin_top(15)
        vbox_sag.set_margin_bottom(15)
        vbox_sag.set_margin_end(15)
        paned.append(vbox_sag)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_has_frame(True)
        
        self.metin_alani = Gtk.TextView(editable=False, monospace=True)
        self.metin_alani.set_left_margin(12)
        self.metin_alani.set_top_margin(12)
        self.metin_alani.set_wrap_mode(Gtk.WrapMode.WORD_CHAR) # Uzun satırları böl
        
        scrolled.set_child(self.metin_alani)
        vbox_sag.append(scrolled)

        self.win.present()
        self.islem_baslat("-b")

    def vurgula_butonu(self, buton):
        """Tıklanan butonu mavi yapar ve eski butonu normale döndürür."""
        if self.aktif_buton:
            # Önceki butonun vurgusunu kaldır
            self.aktif_buton.remove_css_class("suggested-action")
        
        # Yeni butonu vurgula
        self.aktif_buton = buton
        self.aktif_buton.add_css_class("suggested-action")

    def on_button_clicked(self, btn):
        self.vurgula_butonu(btn)
        self.islem_baslat(btn.param)

    def islem_baslat(self, param):
        self.spinner.start()
        # Veri çekilirken butonlara tekrar basılmasını engellemek isteyebilirsiniz
        # Ancak kullanıcı deneyimi için menüyü kapatmak yerine sadece spinner göstermek daha iyidir
        
        thread = threading.Thread(target=self.arkaplan_islem, args=(param,))
        thread.daemon = True
        thread.start()

    def arkaplan_islem(self, param):
        # Türkçe karakter desteği ve renksiz çıktı (-c 0)
        env = os.environ.copy()
        env["LC_ALL"] = "tr_TR.UTF-8"
        env["LANG"] = "tr_TR.UTF-8"
        try:
            res = subprocess.run(['inxi', param, '-c', '0'], capture_output=True, text=True, env=env)
            cikti = res.stdout if res.stdout else "Veri bulunamadı veya bu donanım mevcut değil."
        except Exception as e:
            cikti = f"Hata: inxi yüklü mü? \nDetay: {str(e)}"
        
        GLib.idle_add(self.metni_yaz, cikti)

    def metni_yaz(self, metin):
        buffer = self.metin_alani.get_buffer()
        buffer.set_text(metin)
        self.spinner.stop()
        return False

if __name__ == "__main__":
    app = InxiSadePanel()
    app.run(None)