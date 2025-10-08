import os
import sys
import asyncio
import random
import time
import json
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from colorama import init, Fore, Style
from aiohttp import ClientSession, ClientTimeout, ClientResponseError
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from typing import List, Tuple

# Initialize colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://testnet-rpc.irys.xyz/v1/execution-rpc"
CHAIN_ID = 1270
EXPLORER_URL = "https://testnet-explorer.irys.xyz/tx/0x"
BASE_API = "https://play.irys.xyz/api"
IP_CHECK_URL = "https://api.ipify.org?format=json"
BORDER_WIDTH = 80
MAX_WAIT_TIME = 180  # Timeout 3 minutes
ARCADE_BANK_ADDRESS = Web3.to_checksum_address("0xBC41F2B6BdFCB3D87c3d5E8b37fD02C56B69ccaC")
NATIVE_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"
CONTRACT_ABI = [
    {
        "type": "function",
        "name": "getUserBalance",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]
HEADERS = {
    "User-Agent": FakeUserAgent().random,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://play.irys.xyz",
    "Referer": "https://play.irys.xyz/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_ACTIONS": [5, 15],
    "PAUSE_GAME_COMPLETION": [25, 30],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # IRYS for game cost
    "GAME_SCORE": 500000,  # Default score for Asteroids
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'CHƠI GAME ASTEROIDS - IRYS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'starting_game': 'Đang bắt đầu game Asteroids...',
        'completing_game': 'Đang hoàn thành game Asteroids...',
        'game_success': '✅ Chơi game thành công!',
        'game_failed': '❌ Game thất bại',
        'address': 'Địa chỉ ví',
        'block': 'Khối',
        'tx_hash': 'Tx Hash',
        'explorer': 'Explorer',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} LƯỢT CHƠI THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với Irys Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'game_count_prompt': 'Nhập số lượt chơi Asteroids',
        'invalid_game_count': 'Số không hợp lệ, vui lòng nhập số nguyên không âm',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': 'PLAY ASTEROIDS GAME - IRYS TESTNET',
        'info': 'Information',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (requires at least {required:.6f})',
        'starting_game': 'Starting Asteroids game...',
        'completing_game': 'Completing Asteroids game...',
        'game_success': '✅ Game played successfully!',
        'game_failed': '❌ Game failed',
        'address': 'Wallet address',
        'block': 'Block',
        'tx_hash': 'Tx Hash',
        'explorer': 'Explorer',
        'balance': 'Balance',
        'balance_info': 'Wallet balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} GAMES SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Irys Testnet',
        'connect_error': '❌ Cannot connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Cannot read pvkey.txt',
        'invalid_key': 'invalid, skipped',
        'warning_line': 'Warning: Line',
        'game_count_prompt': 'Enter number of Asteroids games to play',
        'invalid_game_count': 'Invalid number, please enter a non-negative integer',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or inactive proxy: {proxy}',
        'ip_check_failed': '⚠ Cannot check public IP: {error}',
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

def display_all_wallets_balances(w3: Web3, private_keys: List[Tuple[int, str]], language: str = 'vi'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'IRYS':<10} | {'Arcade IRYS':<12}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 12}{Style.RESET_ALL}")
    
    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        irys_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
        arcade_balance = check_balance(w3, address, ARCADE_BANK_ADDRESS, 18, language)
        print(f"{Fore.YELLOW}  {i:<6} | {irys_balance:>10.6f} | {arcade_balance:>12.6f}{Style.RESET_ALL}")
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
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
        else:
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}", Fore.YELLOW)
                    return LANG[language]['unknown']
    except Exception as e:
        print_message(f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}", Fore.YELLOW)
        return LANG[language]['unknown']

def connect_web3(language: str = 'vi'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        try:
            block_number = w3.eth.get_block_number()
            chain_id = w3.eth.chain_id
            print_message(f"✔ {LANG[language]['connect_success']} │ Chain ID: {chain_id} │ Block: {block_number}", Fore.GREEN)
            return w3
        except Exception:
            print_message(f"✖ {LANG[language]['connect_error']}", Fore.RED)
            sys.exit(1)
    except Exception as e:
        print_message(f"✖ {LANG[language]['web3_error']}: {str(e)}", Fore.RED)
        sys.exit(1)

def check_balance(w3: Web3, address: str, token_address: str, decimals: int, language: str = 'vi') -> float:
    if token_address == NATIVE_TOKEN_ADDRESS:
        try:
            balance = w3.eth.get_balance(address)
            return float(w3.from_wei(balance, 'ether'))
        except Exception as e:
            print_message(f"⚠ {LANG[language]['error']}: {str(e)}", Fore.YELLOW)
            return -1
    else:
        token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=CONTRACT_ABI)
        try:
            balance = token_contract.functions.getUserBalance(address).call()
            return balance / (10 ** decimals)
        except Exception as e:
            print_message(f"⚠ {LANG[language]['error']}: {str(e)}", Fore.YELLOW)
            return -1

def generate_random_string(length: int = 9) -> str:
    import string
    import secrets
    characters = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_game_payload(account: str, address: str, game_id: str, score: int, start_timestamp: int, game_type: str, payload_type: str):
    try:
        if payload_type == "Start":
            message = f"I authorize payment of 0.001 IRYS to play a game on Irys Arcade.\n    \nPlayer: {address}\nAmount: 0.001 IRYS\nTimestamp: {start_timestamp}\n\nThis signature confirms I own this wallet and authorize the payment."
        elif payload_type == "Complete":
            complete_timestamp = int(time.time()) * 1000
            message = f"I completed a {game_type} game on Irys Arcade.\n    \nPlayer: {address}\nGame: {game_type}\nScore: {score}\nSession: game_{start_timestamp}_{game_id}\nTimestamp: {complete_timestamp}\n\nThis signature confirms I own this wallet and completed this game."

        encoded_message = encode_defunct(text=message)
        signed_message = Account.sign_message(encoded_message, private_key=account)
        signature = to_hex(signed_message.signature)

        if payload_type == "Start":
            return {
                "playerAddress": address,
                "gameCost": 0.001,
                "signature": signature,
                "message": message,
                "timestamp": start_timestamp,
                "sessionId": f"game_{start_timestamp}_{game_id}",
                "gameType": game_type
            }
        elif payload_type == "Complete":
            return {
                "playerAddress": address,
                "gameType": game_type,
                "score": score,
                "signature": signature,
                "message": message,
                "timestamp": complete_timestamp,
                "sessionId": f"game_{start_timestamp}_{game_id}"
            }
    except Exception as e:
        print_message(f"✖ Lỗi tạo payload: {str(e)}", Fore.RED)
        raise

async def start_game(account: str, address: str, game_id: str, score: int, start_timestamp: int, game_type: str, proxy: str = None, language: str = 'vi'):
    url = f"{BASE_API}/game/start"
    try:
        payload = generate_game_payload(account, address, game_id, score, start_timestamp, game_type, "Start")
        data = json.dumps(payload)
        headers = {
            **HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=180)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy if not connector else None) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result
            except (Exception, ClientResponseError) as e:
                print_message(f"Thử {attempt+1}/{CONFIG['MAX_RETRIES']}: Lỗi - {str(e)}", Fore.RED)
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    delay = random.uniform(5, 15)
                    print_message(f"Thử lại sau {delay:.2f} giây...", Fore.YELLOW)
                    await asyncio.sleep(delay)
                continue
        print_message(f"✖ {LANG[language]['game_failed']}: Thất bại sau {CONFIG['MAX_RETRIES']} lần thử", Fore.RED)
        return None
    except Exception as e:
        print_message(f"✖ {LANG[language]['game_failed']}: Lỗi không mong đợi - {str(e)}", Fore.RED)
        return None

async def complete_game(account: str, address: str, game_id: str, score: int, start_timestamp: int, game_type: str, proxy: str = None, language: str = 'vi'):
    url = f"{BASE_API}/game/complete"
    try:
        payload = generate_game_payload(account, address, game_id, score, start_timestamp, game_type, "Complete")
        data = json.dumps(payload)
        headers = {
            **HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                connector = ProxyConnector.from_url(proxy) if proxy and proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')) else None
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=180)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy if not connector else None) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result
            except (Exception, ClientResponseError) as e:
                print_message(f"Thử {attempt+1}/{CONFIG['MAX_RETRIES']}: Lỗi - {str(e)}", Fore.RED)
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    delay = random.uniform(5, 15)
                    print_message(f"Thử lại sau {delay:.2f} giây...", Fore.YELLOW)
                    await asyncio.sleep(delay)
                continue
        print_message(f"✖ {LANG[language]['game_failed']}: Thất bại sau {CONFIG['MAX_RETRIES']} lần thử", Fore.RED)
        return None
    except Exception as e:
        print_message(f"✖ {LANG[language]['game_failed']}: Lỗi không mong đợi - {str(e)}", Fore.RED)
        return None

async def play_asteroids_game(w3: Web3, private_key: str, wallet_index: int, game_count: int, language: str = 'vi', proxy: str = None):
    account = Account.from_key(private_key)
    address = account.address
    game_type = "asteroids"
    score = CONFIG['GAME_SCORE']
    successful_games = 0
    total_games = 0
    
    print_message(f"Bắt đầu xử lý ví {wallet_index}: {address}", Fore.CYAN)
    for i in range(game_count):
        total_games += 1
        print_border(f"Game Asteroids {i+1}/{game_count}", Fore.YELLOW)
        print_message(f"> {LANG[language]['checking_balance']}", Fore.CYAN)
        
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        print_message(f"🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)
        
        arcade_balance = check_balance(w3, address, ARCADE_BANK_ADDRESS, 18, language)
        if arcade_balance < CONFIG['MINIMUM_BALANCE']:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=arcade_balance, symbol='Arcade IRYS', required=CONFIG['MINIMUM_BALANCE'])}", Fore.RED)
            break
        
        game_id = generate_random_string()
        start_timestamp = int(time.time()) * 1000
        print_message(f"> {LANG[language]['starting_game']}", Fore.CYAN)
        
        start = await start_game(private_key, address, game_id, score, start_timestamp, game_type, proxy, language)
        
        if start is None:
            print_message(f"✖ {LANG[language]['game_failed']}: Không nhận được phản hồi từ API", Fore.RED)
            continue
        if not start.get("success", False):
            print_message(f"✖ {LANG[language]['game_failed']}: {start.get('message', 'Lỗi không xác định')}", Fore.RED)
            continue
        
        message = start.get("message")
        tx_hash = start.get("data", {}).get("transactionHash")
        print_message(f"✔ {message}! Số dư Arcade IRYS: {arcade_balance:.6f}", Fore.GREEN)
        print_message(f"    - {LANG[language]['tx_hash']}: {tx_hash}", Fore.YELLOW)
        print_message(f"    - {LANG[language]['explorer']}: {EXPLORER_URL}{tx_hash}", Fore.YELLOW)
        
        delay = random.uniform(CONFIG['PAUSE_GAME_COMPLETION'][0], CONFIG['PAUSE_GAME_COMPLETION'][1])
        await asyncio.sleep(delay)
        
        print_message(f"> {LANG[language]['completing_game']}", Fore.CYAN)
        complete = await complete_game(private_key, address, game_id, score, start_timestamp, game_type, proxy, language)
        
        if complete is None:
            print_message(f"✖ {LANG[language]['game_failed']}: Không nhận được phản hồi từ API", Fore.RED)
            continue
        if not complete.get("success", False):
            print_message(f"✖ {LANG[language]['game_failed']}: {complete.get('message', 'Lỗi không xác định')}", Fore.RED)
            continue
        
        reward = complete.get("data", {}).get("rewardAmount", 0)
        tx_hash = complete.get("data", {}).get("transactionHash")
        arcade_balance_after = check_balance(w3, address, ARCADE_BANK_ADDRESS, 18, language)
        
        successful_games += 1
        print_message(f"✔ {LANG[language]['game_success']} Tx Hash: {tx_hash}", Fore.GREEN)
        print_message(f"    - {LANG[language]['address']}: {address}", Fore.YELLOW)
        print_message(f"    - Điểm {score} | Phần thưởng {float(reward):.6f} IRYS", Fore.YELLOW)
        print_message(f"    - {LANG[language]['balance']}: Arcade IRYS: {arcade_balance_after:.6f}", Fore.YELLOW)
        print_message(f"    - Tổng số lượt chơi thử: {total_games} | Thành công: {successful_games}", Fore.YELLOW)
        print_message(f"    - {LANG[language]['tx_hash']}: {tx_hash}", Fore.YELLOW)
        
        if i < game_count - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ACTIONS'][0], CONFIG['PAUSE_BETWEEN_ACTIONS'][1])
            print_message(f"{LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
            await asyncio.sleep(delay)
    
    return successful_games, total_games

async def run_asteroids(language: str = 'vi'):
    try:
        print()
        print_border(LANG[language]['title'], Fore.CYAN)
        print()

        proxies = load_proxies('proxies.txt', language)
        private_keys = load_private_keys('pvkey.txt', language)
        print_message(f"ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}", Fore.YELLOW)
        print()

        if not private_keys:
            return

        w3 = connect_web3(language)
        print()

        display_all_wallets_balances(w3, private_keys, language)
        print_separator()

        min_arcade_balance = float('inf')
        for _, key in private_keys:
            account = Account.from_key(key)
            arcade_balance = check_balance(w3, account.address, ARCADE_BANK_ADDRESS, 18, language)
            min_arcade_balance = min(min_arcade_balance, arcade_balance)

        print()
        while True:
            print(f"{Fore.CYAN}{LANG[language]['game_count_prompt']} {Fore.YELLOW}(Cần ít nhất {CONFIG['MINIMUM_BALANCE']:.4f} Arcade IRYS mỗi lượt){Style.RESET_ALL}")
            try:
                game_count = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
                if game_count >= 0 and min_arcade_balance >= CONFIG['MINIMUM_BALANCE'] * game_count:
                    break
                print_message(f"✖ {LANG[language]['invalid_game_count']} hoặc số dư Arcade IRYS không đủ", Fore.RED)
            except ValueError:
                print_message(f"✖ {LANG[language]['invalid_game_count']}", Fore.RED)

        print_separator()
        random.shuffle(private_keys)
        print_wallets_summary(len(private_keys), language)

        async def process_wallet(index, profile_num, private_key):
            nonlocal successful_games, total_games
            proxy = proxies[index % len(proxies)] if proxies else None
            
            async with semaphore:
                games, attempted = await play_asteroids_game(w3, private_key, profile_num, game_count, language, proxy)
                successful_games += games
                total_games += attempted
                if index < len(private_keys) - 1:
                    delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                    print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                    await asyncio.sleep(delay)

        semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
        successful_games = 0
        total_games = 0
        tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
        await asyncio.gather(*tasks, return_exceptions=True)

        print()
        print_border(f"{LANG[language]['completed'].format(successful=successful_games, total=total_games)}", Fore.GREEN)
        print()
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN}[ {time.strftime('%m/%d/%y %H:%M:%S')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE} | {Style.RESET_ALL}"
        )
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_asteroids('vi'))
    

