import sys
import subprocess
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QListWidget, QTextEdit, QLabel, 
    QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont

class WorkerSignals(QObject):
    result = pyqtSignal(str)
    error = pyqtSignal(str)

class BalancedModernPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Bilgi Merkezi")
        self.setMinimumSize(1000, 750)
        
        # --- Dengeli (Muted) Renk Paleti ---
        self.COLORS = {
            "bg": "#E2E8F0",        # Orta tonlu gri-mavi (Slate 200)
            "sidebar": "#1E293B",   # Koyu lacivert-gri (Sidebar için derinlik)
            "card": "#F8FAFC",      # Çok hafif gri (Göz yormayan iç alan)
            "accent": "#3B82F6",    # Güven veren mavi
            "text_main": "#0F172A", # Koyu metin
            "text_sidebar": "#CBD5E1", # Sidebar açık metin
            "hover": "#334155",     # Sidebar hover
            "border": "#CBD5E1"     # Yumuşak kenarlık
        }
        
        self.init_ui()

    def init_ui(self):
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        
        ana_layout = QHBoxLayout(ana_widget)
        ana_layout.setContentsMargins(0, 0, 0, 0)
        ana_layout.setSpacing(0)

        # --- SOL MENÜ (Sidebar) ---
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(280)
        sidebar_container.setObjectName("sidebarContainer")
        
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(15, 30, 15, 20)

        title = QLabel("SİSTEM PANELİ")
        title.setStyleSheet(f"color: white; font-weight: bold; font-size: 16px; margin-bottom: 25px; margin-left: 10px;")
        sidebar_layout.addWidget(title)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        
        self.kategoriler = {
            "🏠 Sistem Özeti": "-b",
            "💻 İşlemci (CPU)": "-C",
            "🖼️ Ekran Kartı (GPU)": "-G",
            "💾 Bellek (RAM)": "-m",
            "💽 Disk Bilgisi": "-D",
            "🌐 Ağ Kartları": "-N",
            "🔊 Ses Sistemi": "-A",
            "🌡️ Sıcaklıklar": "-s",
            "📦 Yazılım Depoları": "-r",
            "🔋 Pil Durumu": "-B",
            "📑 Tam Rapor": "-F"
        }

        for isim in self.kategoriler.keys():
            self.sidebar.addItem(isim)
        
        self.sidebar.currentRowChanged.connect(self.kategori_degisti)
        sidebar_layout.addWidget(self.sidebar)
        ana_layout.addWidget(sidebar_container)

        # --- SAĞ PANEL (İçerik) ---
        sag_panel = QWidget()
        sag_layout = QVBoxLayout(sag_panel)
        sag_layout.setContentsMargins(30, 30, 30, 30)
        
        self.card = QFrame()
        self.card.setObjectName("infoCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Kart Başlığı
        self.baslik_label = QLabel("Bilgi Seçiniz")
        self.baslik_label.setStyleSheet(f"color: {self.COLORS['text_main']}; font-size: 20px; font-weight: 600; padding: 20px;")
        card_layout.addWidget(self.baslik_label)

        # İnce Yükleme Barı
        self.yukleme_bar = QProgressBar()
        self.yukleme_bar.setRange(0, 0)
        self.yukleme_bar.setFixedHeight(3)
        self.yukleme_bar.setTextVisible(False)
        self.yukleme_bar.hide()
        card_layout.addWidget(self.yukleme_bar)

        # Metin Alanı
        self.metin_alani = QTextEdit()
        self.metin_alani.setReadOnly(True)
        self.metin_alani.setFont(QFont("Monospace", 10))
        self.metin_alani.setObjectName("metinAlani")
        card_layout.addWidget(self.metin_alani)
        
        sag_layout.addWidget(self.card)
        ana_layout.addWidget(sag_panel)

        # --- DENGELİ TEMA STİLİ (QSS) ---
        self.setStyleSheet(f"""
            #sidebarContainer {{
                background-color: {self.COLORS['sidebar']};
            }}
            #sidebar {{
                background-color: transparent;
                border: none;
                color: {self.COLORS['text_sidebar']};
                outline: none;
            }}
            #sidebar::item {{
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 4px;
            }}
            #sidebar::item:hover {{
                background-color: {self.COLORS['hover']};
            }}
            #sidebar::item:selected {{
                background-color: {self.COLORS['accent']};
                color: white;
            }}
            #anaWidget, QMainWindow {{
                background-color: {self.COLORS['bg']};
            }}
            #infoCard {{
                background-color: {self.COLORS['card']};
                border-radius: 12px;
                border: 1px solid {self.COLORS['border']};
            }}
            #metinAlani {{
                background-color: transparent;
                border: none;
                color: {self.COLORS['text_main']};
                padding: 15px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.COLORS['border']};
                border-radius: 4px;
            }}
        """)

        self.sidebar.setCurrentRow(0)

    def kategori_degisti(self, index):
        if index < 0: return
        item_text = self.sidebar.currentItem().text()
        self.baslik_label.setText(item_text)
        self.islem_baslat(self.kategoriler[item_text])

    def islem_baslat(self, param):
        self.yukleme_bar.show()
        self.signals = WorkerSignals()
        self.signals.result.connect(self.metni_yaz)
        self.signals.error.connect(self.metni_yaz)
        threading.Thread(target=self.arkaplan_islem, args=(param,), daemon=True).start()

    def arkaplan_islem(self, param):
        env = os.environ.copy()
        env["LC_ALL"] = "tr_TR.UTF-8"
        try:
            res = subprocess.run(['inxi', param, '-c', '0'], capture_output=True, text=True, env=env)
            self.signals.result.emit(res.stdout if res.stdout else "Bilgi bulunamadı.")
        except Exception as e:
            self.signals.error.emit(str(e))

    def metni_yaz(self, metin):
        self.metin_alani.setPlainText(metin)
        self.yukleme_bar.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BalancedModernPanel()
    window.show()
    sys.exit(app.exec())