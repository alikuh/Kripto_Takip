import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime


class CryptoTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Kripto Para Takip Uygulaması")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # Ana frame
        self.main_frame = tk.Frame(root, bg='#1a1a1a')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Başlık
        title_label = tk.Label(
            self.main_frame,
            text="🚀 Kripto Para Takip",
            font=("Arial", 20, "bold"),
            bg='#1a1a1a',
            fg='#00d4aa'
        )
        title_label.pack(pady=(0, 20))

        # Arama bölümü
        self.create_search_section()

        # Ana tablo bölümü
        self.create_main_table()

        # Güncelleme butonu
        self.create_update_button()

        # İlk veri yüklemesi
        self.load_top_coins()

    def create_search_section(self):
        search_frame = tk.Frame(self.main_frame, bg='#1a1a1a')
        search_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            search_frame,
            text="Kripto Para Ara (İsim veya Sembol):",
            font=("Arial", 12, "bold"),
            bg='#1a1a1a',
            fg='#ffffff'
        ).pack(anchor=tk.W)

        search_input_frame = tk.Frame(search_frame, bg='#1a1a1a')
        search_input_frame.pack(fill=tk.X, pady=(5, 0))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_input_frame,
            textvariable=self.search_var,
            font=("Arial", 11),
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT,
            bd=5
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        search_button = tk.Button(
            search_input_frame,
            text="🔍 Ara",
            command=self.search_crypto,
            bg='#00d4aa',
            fg='#000000',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2"
        )
        search_button.pack(side=tk.RIGHT)

        # Enter tuşu ile arama
        self.search_entry.bind('<Return>', lambda e: self.search_crypto())

    def create_main_table(self):
        # Tablo frame
        table_frame = tk.Frame(self.main_frame, bg='#1a1a1a')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Tablo başlığı
        table_title = tk.Label(
            table_frame,
            text="📊 Top 10 Kripto Para",
            font=("Arial", 14, "bold"),
            bg='#1a1a1a',
            fg='#00d4aa'
        )
        table_title.pack(anchor=tk.W, pady=(0, 10))

        # Treeview oluşturma
        columns = ('Sıra', 'İsim', 'Sembol', 'Fiyat ($)', 'Market Cap', '24s Değişim (%)')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        # Sütun başlıkları
        self.tree.heading('Sıra', text='Sıra')
        self.tree.heading('İsim', text='İsim')
        self.tree.heading('Sembol', text='Sembol')
        self.tree.heading('Fiyat ($)', text='Fiyat ($)')
        self.tree.heading('Market Cap', text='Market Cap')
        self.tree.heading('24s Değişim (%)', text='24s Değişim (%)')

        # Sütun genişlikleri ve hizalama
        self.tree.column('Sıra', width=60, anchor='center')
        self.tree.column('İsim', width=150, anchor='center')
        self.tree.column('Sembol', width=100, anchor='center')
        self.tree.column('Fiyat ($)', width=150, anchor='center')
        self.tree.column('Market Cap', width=180, anchor='center')
        self.tree.column('24s Değişim (%)', width=150, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tablo stilini ayarla
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#2a2a2a",
                        foreground="white",
                        fieldbackground="#2a2a2a",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#00d4aa",
                        foreground="black",
                        font=("Arial", 10, "bold"))

    def create_update_button(self):
        button_frame = tk.Frame(self.main_frame, bg='#1a1a1a')
        button_frame.pack(pady=(20, 0))

        update_button = tk.Button(
            button_frame,
            text="🔄 Verileri Güncelle",
            command=self.load_top_coins,
            bg='#4a90e2',
            fg='#ffffff',
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        update_button.pack()

        # Son güncelleme zamanı
        self.last_update_label = tk.Label(
            button_frame,
            text="",
            font=("Arial", 9),
            bg='#1a1a1a',
            fg='#888888'
        )
        self.last_update_label.pack(pady=(5, 0))

    def format_number(self, num):
        """Sayıları formatla"""
        if num is None:
            return "N/A"

        if num >= 1e12:
            return f"${num / 1e12:.2f}T"
        elif num >= 1e9:
            return f"${num / 1e9:.2f}B"
        elif num >= 1e6:
            return f"${num / 1e6:.2f}M"
        elif num >= 1e3:
            return f"${num / 1e3:.2f}K"
        else:
            return f"${num:.2f}"

    def format_percentage(self, percentage):
        """Yüzdelik değerleri formatla"""
        if percentage is None:
            return "N/A"

        if percentage >= 0:
            return f"↗️ +{percentage:.2f}%"
        else:
            return f"↘️ {percentage:.2f}%"

    def load_top_coins(self):
        """Top 10 kripto paraları yükle (stablecoin'ler hariç)"""

        def fetch_data():
            try:
                # Filtrelenecek token'lar (stablecoin'ler ve wrapped token'lar)
                excluded_tokens = {
                    'tether', 'usd-coin', 'binance-usd', 'dai', 'terrausd',
                    'frax', 'trueusd', 'paxos-standard', 'gemini-dollar',
                    'steth', 'weth', 'wbtc', 'wrapped-bitcoin', 'lido-staked-ether',
                    'rocket-pool-eth', 'frax-ether', 'cbeth', 'reth'
                }

                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 50,  # Daha fazla coin çek ki filtreleyebilelim
                    'page': 1,
                    'sparkline': 'false',
                    'price_change_percentage': '24h'
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # Stablecoin'leri ve wrapped token'ları filtrele
                filtered_coins = []
                for coin in data:
                    coin_id = coin.get('id', '').lower()
                    coin_name = coin.get('name', '').lower()
                    coin_symbol = coin.get('symbol', '').lower()

                    # Filtreleme koşulları
                    if (coin_id not in excluded_tokens and
                            'usd' not in coin_symbol and
                            'usdt' not in coin_symbol and
                            'usdc' not in coin_symbol and
                            'busd' not in coin_symbol and
                            'dai' not in coin_symbol and
                            'wrapped' not in coin_name and
                            'staked' not in coin_name and
                            not coin_symbol.startswith('w') or coin_symbol in ['woo', 'waves', 'wax']):

                        filtered_coins.append(coin)

                        # 10 tane bulunca dur
                        if len(filtered_coins) >= 10:
                            break

                # Tabloyu temizle
                for item in self.tree.get_children():
                    self.tree.delete(item)

                # Filtrelenmiş verileri ekle
                for i, coin in enumerate(filtered_coins, 1):
                    name = coin.get('name', 'N/A')
                    symbol = coin.get('symbol', 'N/A').upper()
                    price = coin.get('current_price')
                    market_cap = coin.get('market_cap')
                    price_change = coin.get('price_change_percentage_24h')

                    formatted_price = self.format_number(price) if price else "N/A"
                    formatted_market_cap = self.format_number(market_cap) if market_cap else "N/A"
                    formatted_change = self.format_percentage(price_change)

                    # Tabloya ekle ve renk ayarla
                    item_id = self.tree.insert('', 'end', values=(
                        i, name, symbol, formatted_price,
                        formatted_market_cap, formatted_change
                    ))

                    # Değişim sütunu için renk ayarla
                    if price_change is not None:
                        if price_change >= 0:
                            self.tree.set(item_id, '24s Değişim (%)', f"↗️ +{price_change:.2f}%")
                            # Ana tabloda da renk kullanmak için treeview tag'leri ekleyebiliriz
                        else:
                            self.tree.set(item_id, '24s Değişim (%)', f"↘️ {price_change:.2f}%")

                # Son güncelleme zamanını göster
                now = datetime.now().strftime("%H:%M:%S")
                self.last_update_label.config(text=f"Son güncelleme: {now}")

            except requests.exceptions.RequestException as e:
                messagebox.showerror("Hata", f"Veri alınırken hata oluştu:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Hata", f"Beklenmeyen hata:\n{str(e)}")

        # Arka planda veri çek
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()

    def search_crypto(self):
        """Kripto para ara"""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Uyarı", "Lütfen aranacak kripto para ismini veya sembolünü girin.")
            return

        def fetch_search_data():
            try:
                # Önce arama yap
                search_url = "https://api.coingecko.com/api/v3/search"
                search_params = {'query': search_term}

                search_response = requests.get(search_url, params=search_params, timeout=10)
                search_response.raise_for_status()
                search_data = search_response.json()

                if not search_data.get('coins'):
                    messagebox.showinfo("Sonuç Bulunamadı", f"'{search_term}' için sonuç bulunamadı.")
                    return

                # İlk sonucu al
                coin_id = search_data['coins'][0]['id']

                # Detaylı bilgileri al
                detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                detail_params = {
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false',
                    'sparkline': 'false'
                }

                detail_response = requests.get(detail_url, params=detail_params, timeout=10)
                detail_response.raise_for_status()
                detail_data = detail_response.json()

                # Sonuç penceresini göster
                self.show_search_result(detail_data)

            except requests.exceptions.RequestException as e:
                messagebox.showerror("Hata", f"Arama sırasında hata oluştu:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Hata", f"Beklenmeyen hata:\n{str(e)}")

        # Arka planda ara
        thread = threading.Thread(target=fetch_search_data, daemon=True)
        thread.start()

    def show_search_result(self, coin_data):
        """Arama sonucunu yeni pencerede göster"""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"{coin_data.get('name', 'N/A')} - Detaylı Bilgi")
        result_window.geometry("600x500")
        result_window.configure(bg='#1a1a1a')
        result_window.transient(self.root)
        result_window.grab_set()
        result_window.resizable(False, False)

        # Ana container
        main_container = tk.Frame(result_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Başlık bölümü
        header_frame = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        coin_name = coin_data.get('name', 'N/A')
        coin_symbol = coin_data.get('symbol', 'N/A').upper()

        title_label = tk.Label(
            header_frame,
            text=f"💰 {coin_name} ({coin_symbol})",
            font=("Arial", 18, "bold"),
            bg='#2a2a2a',
            fg='#00d4aa',
            pady=15
        )
        title_label.pack()

        # İçerik çerçevesi
        content_frame = tk.Frame(main_container, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Market verileri
        market_data = coin_data.get('market_data', {})

        # Sol ve sağ kolon için frame'ler
        columns_frame = tk.Frame(content_frame, bg='#1a1a1a')
        columns_frame.pack(fill=tk.BOTH, expand=True)

        left_column = tk.Frame(columns_frame, bg='#1a1a1a')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = tk.Frame(columns_frame, bg='#1a1a1a')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Sol kolon bilgileri
        left_info = [
            ("💵 Güncel Fiyat", self.format_number(market_data.get('current_price', {}).get('usd'))),
            ("📊 Market Cap", self.format_number(market_data.get('market_cap', {}).get('usd'))),
            ("📈 24s Değişim", self.format_percentage(market_data.get('price_change_percentage_24h'))),
            ("📉 7g Değişim", self.format_percentage(market_data.get('price_change_percentage_7d'))),
            ("⭐ Market Sırası", f"#{market_data.get('market_cap_rank', 'N/A')}")
        ]

        # Sağ kolon bilgileri
        right_info = [
            ("🎯 24s En Yüksek", self.format_number(market_data.get('high_24h', {}).get('usd'))),
            ("📉 24s En Düşük", self.format_number(market_data.get('low_24h', {}).get('usd'))),
            ("🔢 Dolaşımdaki Arz",
             f"{market_data.get('circulating_supply', 0):,.0f}" if market_data.get('circulating_supply') else "N/A"),
            ("🔄 Toplam Hacim", self.format_number(market_data.get('total_volume', {}).get('usd'))),
            ("⏰ Son Güncelleme", market_data.get('last_updated', 'N/A')[:19].replace('T', ' ') if market_data.get(
                'last_updated') else 'N/A')
        ]

        # Sol kolon oluştur
        self.create_info_section(left_column, left_info)

        # Sağ kolon oluştur
        self.create_info_section(right_column, right_info)

        # Alt buton çerçevesi
        button_frame = tk.Frame(main_container, bg='#1a1a1a')
        button_frame.pack(pady=(20, 0))

        # Kapatma butonu
        close_button = tk.Button(
            button_frame,
            text="✖️ Kapat",
            command=result_window.destroy,
            bg='#ff4757',
            fg='#ffffff',
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            activebackground='#ff3838',
            activeforeground='#ffffff'
        )
        close_button.pack()

        # Pencereyi ortala
        result_window.update_idletasks()
        x = (result_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (result_window.winfo_screenheight() // 2) - (500 // 2)
        result_window.geometry(f"600x500+{x}+{y}")

    def create_info_section(self, parent, info_list):
        """Bilgi bölümü oluştur"""
        for i, (label, value) in enumerate(info_list):
            info_container = tk.Frame(parent, bg='#2a2a2a', relief=tk.FLAT, bd=1)
            info_container.pack(fill=tk.X, pady=3)

            # Etiktet
            label_frame = tk.Frame(info_container, bg='#2a2a2a')
            label_frame.pack(fill=tk.X, padx=10, pady=8)

            tk.Label(
                label_frame,
                text=label,
                font=("Arial", 10, "bold"),
                bg='#2a2a2a',
                fg='#888888',
                anchor='w'
            ).pack(anchor='w')

            # Değer - renk kontrolü
            value_color = '#ffffff'
            if 'Değişim' in label and str(value) != 'N/A':
                if '↗️' in str(value):
                    value_color = '#00ff88'  # Yeşil
                elif '↘️' in str(value):
                    value_color = '#ff4757'  # Kırmızı

            tk.Label(
                label_frame,
                text=str(value),
                font=("Arial", 11, "bold"),
                bg='#2a2a2a',
                fg=value_color,
                anchor='w'
            ).pack(anchor='w', pady=(2, 0))


def main():
    root = tk.Tk()
    app = CryptoTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()