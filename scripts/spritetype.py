import os
import sys
import asyncio
import random
import time
from datetime import datetime
from eth_account import Account
from colorama import init, Fore, Style
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
import hashlib
import json
import re
from typing import List, Tuple

# Initialize colorama
init(autoreset=True)

# Constants
EXPLORER_URL = "https://testnet-explorer.irys.xyz/tx/0x"
IP_CHECK_URL = "https://api.ipify.org?format=json"
BORDER_WIDTH = 80
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_ACTIONS": [25, 35],
    "MAX_RETRIES": 3,
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'SPRITETYPE - IRYS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'error': 'Lỗi',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} TRÒ CHƠI THÀNH CÔNG',
        'game_status': 'Trạng thái trò chơi {current}/{total}',
        'game_success': '✅ Gửi trò chơi thành công: {message}',
        'game_failed': '❌ Gửi trò chơi thất bại: {error}',
        'receipt': 'Mã giao dịch',
        'games_prompt': 'Nhập số lượng trò chơi',
        'game_stats_info': 'Thông tin trò chơi',
        'wpm': 'WPM',
        'accuracy': 'Độ chính xác (%)',
        'time': 'Thời gian (s)',
        'correct_chars': 'Ký tự đúng',
        'incorrect_chars': 'Ký tự sai',
        'next_game': 'Chơi lại',
    },
    'en': {
        'title': 'SPRITETYPE - IRYS TESTNET',
        'info': 'Information',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'error': 'Error',
        'pvkey_not_found': '❌ File pvkey.txt not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Cannot read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} GAMES SUCCESSFUL',
        'game_status': 'Game status {current}/{total}',
        'game_success': '✅ Game submitted successfully: {message}',
        'game_failed': '❌ Game submission failed: {error}',
        'receipt': 'Receipt ID',
        'games_prompt': 'Enter number of games',
        'game_stats_info': 'Game Information',
        'wpm': 'WPM',
        'accuracy': 'Accuracy (%)',
        'time': 'Time (s)',
        'correct_chars': 'Correct Chars',
        'incorrect_chars': 'Incorrect Chars',
        'next_game': 'Play Again',
    },
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}  {message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'vi'):
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA
    )
    print()

def print_game_stats(game_stats: dict, language: str = 'vi'):
    print_border(LANG[language]['game_stats_info'], Fore.CYAN)
    headers = [
        LANG[language]['wpm'],
        LANG[language]['accuracy'],
        LANG[language]['time'],
        LANG[language]['correct_chars'],
        LANG[language]['incorrect_chars']
    ]
    col_widths = [8, 16, 13, 13, 12]
    header_row = "  " + " | ".join(f"{header:<{width}}" for header, width in zip(headers, col_widths))
    print(f"{Fore.CYAN}{header_row}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * col_widths[0]} | {'-' * col_widths[1]} | {'-' * col_widths[2]} | {'-' * col_widths[3]} | {'-' * col_widths[4]}{Style.RESET_ALL}")

    wpm = game_stats['wpm']
    accuracy = game_stats['accuracy']
    time = game_stats['time']
    correct_chars = game_stats['correctChars']
    incorrect_chars = game_stats['incorrectChars']
    print(f"{Fore.YELLOW}  {wpm:<8} | {accuracy:<16} | {time:<13} | {correct_chars:<13} | {incorrect_chars:<12}{Style.RESET_ALL}")
    print()

# Utility functions
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'vi') -> List[Tuple[int, str]]:
    try:
        if not os.path.exists(file_path):
            print_message(f"✖ {LANG[language]['pvkey_not_found']}", Fore.RED)
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print_message(f"⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}", Fore.YELLOW)
        
        if not valid_keys:
            print_message(f"✖ {LANG[language]['pvkey_empty']}", Fore.RED)
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print_message(f"✖ {LANG[language]['pvkey_error']}: {str(e)}", Fore.RED)
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'vi') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print_message(f"⚠ {LANG[language]['no_proxies']}. Using no proxy.", Fore.YELLOW)
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print_message(f"⚠ {LANG[language]['no_proxies']}. Using no proxy.", Fore.YELLOW)
            return []
        
        print_message(f"ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}", Fore.YELLOW)
        return proxies
    except Exception as e:
        print_message(f"✖ {LANG[language]['error']}: {str(e)}", Fore.RED)
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'vi') -> str:
    try:
        if proxy:
            if proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                connector = ProxyConnector.from_url(proxy)
            else:
                parts = proxy.split(':')
                if len(parts) == 4:  # host:port:user:pass
                    proxy_url = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                    connector = ProxyConnector.from_url(proxy_url)
                elif len(parts) == 3 and '@' in proxy:  # user:pass@host:port
                    connector = ProxyConnector.from_url(f"socks5://{proxy}")
                else:
                    print_message(f"⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}", Fore.YELLOW)
                    return LANG[language]['unknown']
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
        else:
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
    except Exception as e:
        print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}", Fore.YELLOW)
        return LANG[language]['unknown']

class Irys:
    def __init__(self) -> None:
        self.BASE_API = "https://spritetype.irys.xyz/api"
        self.HEADERS = {
            "User-Agent": FakeUserAgent().random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.game_count = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    async def load_proxies(self, language: str = 'vi'):
        self.proxies = load_proxies('proxies.txt', language)

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None
        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None
        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None
        raise Exception("Unsupported Proxy Type.")

    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            return account.address
        except Exception:
            return None

    def mask_account(self, account):
        try:
            return account[:6] + '*' * 6 + account[-6:]
        except Exception:
            return None

    def generate_random_game_stats(self):
        time = random.choice([15, 30, 60, 120])
        wpm_target = int(random.choices(
            [random.randint(20, 50), random.randint(50, 80), random.randint(80, 120)],
            weights=[0.4, 0.4, 0.2]
        )[0])
        total_chars = int(wpm_target * 5 * (time / 60))
        total_chars += random.randint(-10, 10)
        total_chars = max(50, total_chars)
        incorrect_chars = int(total_chars * random.choices(
            [random.uniform(0, 0.03), random.uniform(0.03, 0.08), random.uniform(0.08, 0.15)],
            weights=[0.7, 0.2, 0.1]
        )[0])
        correct_chars = max(1, total_chars - incorrect_chars)
        wpm = round(correct_chars / 5 / (time / 60))
        wpm = max(0, min(wpm, 300))
        accuracy = round(correct_chars / total_chars * 100)
        return {
            "wpm": wpm,
            "accuracy": accuracy,
            "time": time,
            "correctChars": correct_chars,
            "incorrectChars": incorrect_chars,
            "progressData": []
        }

    def generate_anti_cheat_hash(self, address: str, game_stats: dict):
        wpm = game_stats["wpm"]
        accuracy = game_stats["accuracy"]
        time = game_stats["time"]
        correct_chars = game_stats["correctChars"]
        incorrect_chars = game_stats["incorrectChars"]
        l = correct_chars + incorrect_chars
        n = (
            0 + 23 * wpm + 89 * accuracy + 41 * time +
            67 * correct_chars + 13 * incorrect_chars + 97 * l
        )
        char_sum = sum(ord(c) * (i + 1) for i, c in enumerate(address))
        n += 31 * char_sum
        multiplier = float(int("178ba57548d", 16))
        max_safe_integer = float(2**53 - 1)
        checksum = int((multiplier * n) % max_safe_integer)
        base_string = f"{address.lower()}_{wpm}_{accuracy}_{time}_{correct_chars}_{incorrect_chars}_{checksum}"
        hash_result = hashlib.sha256(base_string.encode()).hexdigest()
        return hash_result[:32]

    def generate_payload(self, address: str, game_stats: dict):
        try:
            anti_cheat_hash = self.generate_anti_cheat_hash(address, game_stats)
            payload = {
                "walletAddress": address,
                "gameStats": game_stats,
                "antiCheatHash": anti_cheat_hash,
                "timestamp": int(time.time() * 1000)
            }
            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")

    async def print_timer(self, delay: int, language: str = 'vi'):
        for remaining in range(delay, 0, -1):
            print(
            f"{Fore.CYAN}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE} | {Style.RESET_ALL}"
            f"{Fore.BLUE}{LANG[language]['pausing']} {remaining} {LANG[language]['seconds']} {LANG[language]['next_game']}...{Style.RESET_ALL}",
            end="\r",
            flush=True
            )
            await asyncio.sleep(1)

    def print_question(self, language: str = 'vi'):
        while True:
            print(f"{Fore.CYAN}{LANG[language]['games_prompt']}:{Style.RESET_ALL}")
            try:
                game_count = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}").strip())
                if game_count > 0:
                    self.game_count = game_count
                    break
                print_message(f"✖ {LANG[language]['invalid_games']}", Fore.RED)
            except ValueError:
                print_message(f"✖ {LANG[language]['invalid_games']}", Fore.RED)
        return 1, False  # Default: use proxy, no rotation

    async def check_connection(self, proxy_url=None, language: str = 'vi'):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url=IP_CHECK_URL, proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}", Fore.RED)
            return False

    async def submit_result(self, address: str, game_stats: dict, proxy_url=None, retries=CONFIG['MAX_RETRIES'], language: str = 'vi'):
        url = f"{self.BASE_API}/submit-result"
        data = json.dumps(self.generate_payload(address, game_stats))
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 400:
                            result = await response.json()
                            err_msg = result.get("error")
                            return {"success": False, "message": err_msg}
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                print_message(f"✖ {LANG[language]['game_failed'].format(error=str(e))}", Fore.RED)
                return None

    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool, language: str = 'vi'):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print_message(f"🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)
            is_valid = await self.check_connection(proxy, language)
            if not is_valid and rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                await asyncio.sleep(1)
                continue
            return is_valid

    async def process_accounts(self, index: int, profile_num: int, private_key: str, use_proxy: bool, rotate_proxy: bool, language: str = 'vi'):
        address = self.generate_address(private_key)
        if not address:
            print_message(f"✖ {LANG[language]['error']}: Invalid Private Key", Fore.RED)
            return 0
        
        print_border(f"Tài khoản {profile_num}: {self.mask_account(address)}", Fore.YELLOW)
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy, language)
        if not is_valid:
            return 0

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        successful_games = 0

        for i in range(self.game_count):
            print_border(LANG[language]['game_status'].format(current=i+1, total=self.game_count), Fore.YELLOW)
            game_stats = self.generate_random_game_stats()
            submit = await self.submit_result(address, game_stats, proxy, language=language)
            if submit is None:
                continue
            if submit.get("success"):
                successful_games += 1
                message = submit.get("message")
                receipt = submit.get("data", {}).get("receiptId")
                print_message(f"✔ {LANG[language]['game_success'].format(message=message)}", Fore.GREEN)
                print_game_stats(game_stats, language)  # Print game stats here
                print_message(f"{LANG[language]['receipt']}: {receipt}", Fore.YELLOW)
            else:
                err_msg = submit.get("message")
                print_message(f"✖ {LANG[language]['game_failed'].format(error=err_msg)}", Fore.RED)
                if err_msg == "Hourly submission limit reached. Try again later.":
                    break
            if i < self.game_count - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ACTIONS'][0], CONFIG['PAUSE_BETWEEN_ACTIONS'][1])
                await self.print_timer(int(delay), language)
        
        if index < self.game_count - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
            print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
            await asyncio.sleep(delay)
        
        return successful_games

async def run_spritetype(language: str = 'vi'):
    try:
        print()
        print_border(LANG[language]['title'], Fore.CYAN)
        print()

        private_keys = load_private_keys('pvkey.txt', language)
        print_message(f"ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}", Fore.YELLOW)
        print()

        if not private_keys:
            return

        bot = Irys()
        await bot.load_proxies(language)
        print_separator()

        proxy_choice, rotate_proxy = bot.print_question(language)
        use_proxy = proxy_choice == 1

        print_separator()
        random.shuffle(private_keys)
        print_wallets_summary(len(private_keys), language)

        total_games = len(private_keys) * bot.game_count
        successful_games = 0

        for index, (profile_num, private_key) in enumerate(private_keys):
            successful_games += await bot.process_accounts(index, profile_num, private_key, use_proxy, rotate_proxy, language)

        print()
        print_border(
            f"{LANG[language]['completed'].format(successful=successful_games, total=total_games)}",
            Fore.GREEN
        )
        print()
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE} | {Style.RESET_ALL}"
        )
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_spritetype('en'))

