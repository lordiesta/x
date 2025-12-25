from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

# ==============================
# SINIFLAR (AYNI MANTIK KORUNDU)
# ==============================

class Kargo:
    def __init__(self, takip_no, gonderici, alici, desi):
        self.takip_no = takip_no
        self.gonderici = gonderici
        self.alici = alici
        self.desi = int(desi)
        self.durum = "Oluşturuldu"
        self.gecmis = [f"[{time.strftime('%H:%M')}] Kayıt açıldı."]

    def ucret_hesapla(self):
        return 0

    def durum_guncelle(self, yeni_durum):
        self.durum = yeni_durum
        self.gecmis.append(f"[{time.strftime('%H:%M')}] Durum: {yeni_durum}")

class StandartKargo(Kargo):
    def ucret_hesapla(self):
        return self.desi * 15  # 15 TL birim fiyat

class EkspresKargo(Kargo):
    def __init__(self, takip_no, gonderici, alici, desi, kurye_var_mi):
        super().__init__(takip_no, gonderici, alici, desi)
        self.kurye_var_mi = kurye_var_mi

    def ucret_hesapla(self):
        fiyat = (self.desi * 25) + 60
        if self.kurye_var_mi:
            fiyat += 40
        return fiyat

# ==============================
# VERİ DEPOSU (DATABASE SİMÜLASYONU)
# ==============================
# Veriler burada tutulacak
kargolar_db = {} 

# ==============================
# WEB SAYFALARI (ROUTES)
# ==============================

@app.route('/')
def anasayfa():
    # Tüm kargoları listele
    return render_template('anasayfa.html', kargolar=kargolar_db.values())

@app.route('/ekle', methods=['GET', 'POST'])
def kargo_ekle():
    if request.method == 'POST':
        # Formdan verileri al
        takip_no = request.form.get('takip_no')
        gonderici = request.form.get('gonderici')
        alici = request.form.get('alici')
        desi = int(request.form.get('desi'))
        tip = request.form.get('tip') # standart veya ekspres

        if takip_no in kargolar_db:
            return "HATA: Bu takip numarası zaten var!"

        # Factory Pattern Mantığı (Hangi sınıfı oluşturayım?)
        if tip == 'standart':
            yeni_kargo = StandartKargo(takip_no, gonderici, alici, desi)
        else:
            kurye = request.form.get('kurye') == 'on' # Checkbox seçili mi?
            yeni_kargo = EkspresKargo(takip_no, gonderici, alici, desi, kurye)

        # Sözlüğe kaydet
        kargolar_db[takip_no] = yeni_kargo
        return redirect(url_for('anasayfa'))
    
    return render_template('ekle.html')

@app.route('/takip', methods=['GET', 'POST'])
def kargo_takip():
    kargo = None
    if request.method == 'POST':
        no = request.form.get('takip_no')
        kargo = kargolar_db.get(no)
        
        # Eğer durum güncelleme isteği geldiyse
        yeni_durum = request.form.get('yeni_durum')
        if kargo and yeni_durum:
            kargo.durum_guncelle(yeni_durum)

    return render_template('takip.html', kargo=kargo)

if __name__ == '__main__':
    app.run(debug=True)