import gi
import subprocess
import os
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib

class InxiSadePanel(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.debian.inxi.sade.final')

    def do_activate(self):
        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("Sistem Bilgi Merkezi")

        # Ekran boyutuna göre pencere ölçeklendirme
        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0)
        geo = monitor.get_geometry()
        self.win.set_default_size(int(geo.width * 0.60), int(geo.height * 0.8))

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

        # SOL MENÜ (Butonlar)
        self.sol_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.sol_menu.set_size_request(220, -1)
        
        self.sol_menu.set_margin_top(15)
        self.sol_menu.set_margin_bottom(15)
        self.sol_menu.set_margin_start(15)
        self.sol_menu.set_margin_end(15)
        
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
            btn = Gtk.Button(label=isim)
            btn.add_css_class("pill")
            
            # Buton metnini sola yasla
            label = btn.get_child()
            if isinstance(label, Gtk.Label):
                label.set_xalign(0)  # 0: Sol, 0.5: Orta, 1: Sağ
                label.set_margin_start(10) # Metnin butona çok yapışmaması için küçük boşluk
            
            btn.connect('clicked', self.on_button_clicked, param)
            self.sol_menu.append(btn)

        # SAĞ PANEL (Metin Çıktısı)
        vbox_sag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_sag.set_hexpand(True)
        vbox_sag.set_margin_top(15)
        vbox_sag.set_margin_bottom(15)
        vbox_sag.set_margin_start(5)
        vbox_sag.set_margin_end(15)
        paned.append(vbox_sag)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_has_frame(True)
        
        self.metin_alani = Gtk.TextView(editable=False, monospace=True)
        self.metin_alani.set_left_margin(12)
        self.metin_alani.set_top_margin(12)
        
        scrolled.set_child(self.metin_alani)
        vbox_sag.append(scrolled)

        self.win.present()
        # Başlangıçta sistem özetini getir
        self.on_button_clicked(None, "-b")

    def on_button_clicked(self, btn, param):
        self.spinner.start()
        self.sol_menu.set_sensitive(False)
        
        thread = threading.Thread(target=self.arkaplan_islem, args=(param,))
        thread.daemon = True
        thread.start()

    def arkaplan_islem(self, param):
        env = os.environ.copy()
        env["LC_ALL"] = "tr_TR.UTF-8"
        env["LANG"] = "tr_TR.UTF-8"
        try:
            res = subprocess.run(['inxi', param, '-c', '0'], capture_output=True, text=True, env=env)
            cikti = res.stdout if res.stdout else "Veri bulunamadı."
        except Exception as e:
            cikti = f"Hata: {str(e)}"
        
        GLib.idle_add(self.metni_yaz, cikti)

    def metni_yaz(self, metin):
        buffer = self.metin_alani.get_buffer()
        buffer.set_text(metin)
        
        self.spinner.stop()
        self.sol_menu.set_sensitive(True)
        return False

if __name__ == "__main__":
    app = InxiSadePanel()
    app.run(None)