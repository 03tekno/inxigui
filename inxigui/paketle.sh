#!/bin/bash

# Değişkenler
APP_NAME="inxigui"
VERSION="1.0.0"
MAINTAINER="Adınız Soyadınız <eposta@adresiniz.com>"
DESCRIPTION="inxi aracı için modern GTK4/Libadwaita arayüzü."

# Çalışma dizinini temizle ve oluştur
BUILD_DIR="build_pkg"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/DEBIAN
mkdir -p $BUILD_DIR/usr/bin
mkdir -p $BUILD_DIR/usr/share/$APP_NAME
mkdir -p $BUILD_DIR/usr/share/applications

# 1. Uygulama dosyasını kopyala
cp inxigui.py $BUILD_DIR/usr/share/$APP_NAME/

# 2. Çalıştırılabilir bir "wrapper" oluştur (/usr/bin/inxigui)
cat <<EOF > $BUILD_DIR/usr/bin/$APP_NAME
#!/bin/bash
python3 /usr/share/$APP_NAME/inxigui.py "\$@"
EOF
chmod +x $BUILD_DIR/usr/bin/$APP_NAME

# 3. Masaüstü kısayolu oluştur (.desktop dosyası)
cat <<EOF > $BUILD_DIR/usr/share/applications/$APP_NAME.desktop
[Desktop Entry]
Name=Sistem Bilgi Merkezi
Comment=inxi tabanlı sistem bilgi paneli
Exec=$APP_NAME
Icon=system-search
Terminal=false
Type=Application
Categories=System;Settings;
EOF

# 4. Control dosyasını oluştur (Paket meta verileri)
cat <<EOF > $BUILD_DIR/DEBIAN/control
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: $MAINTAINER
Depends: python3, python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, inxi
Description: $DESCRIPTION
 inxi komut satırı aracını görsel bir arayüze taşır.
 GTK4 ve Libadwaita kullanılarak geliştirilmiştir.
EOF

# 5. Paketi derle
dpkg-deb --build $BUILD_DIR "${APP_NAME}_${VERSION}_all.deb"

echo "✅ Paket başarıyla oluşturuldu: ${APP_NAME}_${VERSION}_all.deb"