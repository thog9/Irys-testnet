import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from typing import List, Tuple

# Initialize colorama
init(autoreset=True)

# Constants
NETWORK_URL = "https://testnet-rpc.irys.xyz/v1/execution-rpc"
CHAIN_ID = 1270
EXPLORER_URL = "https://testnet-explorer.irys.xyz/tx/0x"
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
    {
        "type": "function",
        "name": "withdraw",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "amount", "type": "uint256"}],
        "outputs": [],
    },
]
HEADERS = {
    "User-Agent": FakeUserAgent().random,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_ACTIONS": [5, 15],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.0001,  # IRYS
    "DEFAULT_GAS": 600000,
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'RÚT IRYS - IRYS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} (cần ít nhất {required:.6f})',
        'preparing_withdraw': 'Đang chuẩn bị rút...',
        'sending_withdraw': 'Đang gửi giao dịch rút...',
        'withdraw_success': '✅ Rút thành công: {amount:.6f} IRYS',
        'withdraw_failed': '❌ Rút thất bại',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'balance_info': 'Số dư ví',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} GIAO DỊCH RÚT THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với Irys Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'gas_estimation_failed': 'Không thể ước tính gas',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '⚠ Giao dịch bị từ chối bởi hợp đồng hoặc mạng',
        'amount_prompt': 'Nhập số lượng IRYS để rút',
        'invalid_amount': 'Số lượng không hợp lệ, vui lòng nhập số lớn hơn 0',
        'times_prompt': 'Nhập số lần rút',
        'invalid_times': 'Số không hợp lệ, vui lòng nhập số nguyên dương',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': 'WITHDRAW IRYS - IRYS TESTNET',
        'info': 'Information',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} (need at least {required:.6f})',
        'preparing_withdraw': 'Preparing withdraw...',
        'sending_withdraw': 'Sending withdraw transaction...',
        'withdraw_success': '✅ Withdraw successful: {amount:.6f} IRYS',
        'withdraw_failed': '❌ Withdraw failed',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'balance_info': 'Wallet Balances',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} WITHDRAW TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Irys Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'gas_estimation_failed': 'Failed to estimate gas',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '⚠ Transaction rejected by contract or network',
        'amount_prompt': 'Enter amount of IRYS to withdraw',
        'invalid_amount': 'Invalid amount, please enter a number greater than 0',
        'times_prompt': 'Enter number of withdraw transactions',
        'invalid_times': 'Invalid number, please enter a positive integer',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
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

async def withdraw_token(w3: Web3, private_key: str, wallet_index: int, amount: float, times: int, language: str = 'vi', proxy: str = None):
    account = Account.from_key(private_key)
    address = account.address
    contract = w3.eth.contract(address=ARCADE_BANK_ADDRESS, abi=CONTRACT_ABI)
    amount_wei = int(w3.to_wei(amount, 'ether'))
    successful_withdraws = 0
    
    nonce = w3.eth.get_transaction_count(address, 'pending')
    
    for i in range(times):
        print_border(f"Rút {i+1}/{times}: IRYS", Fore.YELLOW)
        print_message(f"> {LANG[language]['checking_balance']}", Fore.CYAN)
        
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        print_message(f"🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)
        
        arcade_balance = check_balance(w3, address, ARCADE_BANK_ADDRESS, 18, language)
        native_balance = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
        if arcade_balance < amount:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=arcade_balance, symbol='Arcade IRYS', required=amount)}", Fore.RED)
            break
        if native_balance < CONFIG['MINIMUM_BALANCE']:
            print_message(f"✖ {LANG[language]['insufficient_balance'].format(balance=native_balance, symbol='IRYS', required=CONFIG['MINIMUM_BALANCE'])}", Fore.RED)
            break
        
        print_message(f"> {LANG[language]['preparing_withdraw']}", Fore.CYAN)
        gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
        
        for attempt in range(CONFIG['MAX_RETRIES']):
            try:
                print_message(f"> {LANG[language]['sending_withdraw']}", Fore.CYAN)
                nonce = w3.eth.get_transaction_count(address, 'pending')
                tx = contract.functions.withdraw(amount_wei).build_transaction({
                    'nonce': nonce,
                    'from': address,
                    'chainId': CHAIN_ID,
                    'gas': CONFIG['DEFAULT_GAS'],
                    'gasPrice': gas_price
                })
                
                try:
                    estimated_gas = w3.eth.estimate_gas(tx)
                    tx['gas'] = int(estimated_gas * 1.2)
                    print_message(f"Gas estimated: {tx['gas']}", Fore.YELLOW)
                except Exception as e:
                    tx['gas'] = CONFIG['DEFAULT_GAS']
                    print_message(f"{LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=CONFIG['DEFAULT_GAS'])}", Fore.YELLOW)
                
                signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                
                receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=MAX_WAIT_TIME))
                
                if receipt.status == 1:
                    successful_withdraws += 1
                    native_balance_after = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
                    arcade_balance_after = check_balance(w3, address, ARCADE_BANK_ADDRESS, 18, language)
                    print_message(f"✔ {LANG[language]['withdraw_success'].format(amount=amount)} │ Tx: {tx_link}", Fore.GREEN)
                    print_message(f"{LANG[language]['address']}: {address}", Fore.YELLOW)
                    print_message(f"{LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                    print_message(f"{LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                    print_message(f"{LANG[language]['balance']}: {native_balance_after:.6f} IRYS | Arcade IRYS: {arcade_balance_after:.6f}", Fore.YELLOW)
                    nonce += 1
                    break
                else:
                    print_message(f"✖ {LANG[language]['withdraw_failed']} │ Tx: {tx_link}", Fore.RED)
                    print_message(f"{LANG[language]['tx_rejected']}", Fore.RED)
                    break
                
            except Exception as e:
                if attempt < CONFIG['MAX_RETRIES'] - 1:
                    delay = random.uniform(5, 15)
                    print_message(f"✖ {LANG[language]['withdraw_failed']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
                    print_message(f"{LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                    await asyncio.sleep(delay)
                    continue
                print_message(f"✖ {LANG[language]['withdraw_failed']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
                break
        
        if i < times - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ACTIONS'][0], CONFIG['PAUSE_BETWEEN_ACTIONS'][1])
            print_message(f"{LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
            await asyncio.sleep(delay)
    
    return successful_withdraws

async def run_withdraw(language: str = 'vi'):
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

    total_withdraws = 0
    successful_withdraws = 0

    min_arcade_balance = float('inf')
    min_native_balance = float('inf')
    for _, key in private_keys:
        account = Account.from_key(key)
        arcade_balance = check_balance(w3, account.address, ARCADE_BANK_ADDRESS, 18, language)
        native_balance = float(w3.from_wei(w3.eth.get_balance(account.address), 'ether'))
        min_arcade_balance = min(min_arcade_balance, arcade_balance)
        min_native_balance = min(min_native_balance, native_balance)

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['amount_prompt']} {Fore.YELLOW}(Max: {min_arcade_balance:.4f} IRYS, cần {CONFIG['MINIMUM_BALANCE']:.4f} IRYS phí gas){Style.RESET_ALL}")
        try:
            amount = float(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if amount > 0 and amount <= min_arcade_balance and min_native_balance >= CONFIG['MINIMUM_BALANCE']:
                break
            print_message(f"✖ {LANG[language]['invalid_amount']} hoặc vượt quá số dư Arcade IRYS hoặc thiếu IRYS cho phí gas", Fore.RED)
        except ValueError:
            print_message(f"✖ {LANG[language]['invalid_amount']}", Fore.RED)

    print()
    while True:
        print(f"{Fore.CYAN}{LANG[language]['times_prompt']}:{Style.RESET_ALL}")
        try:
            times = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if times > 0:
                break
            print_message(f"✖ {LANG[language]['invalid_times']}", Fore.RED)
        except ValueError:
            print_message(f"✖ {LANG[language]['invalid_times']}", Fore.RED)

    print_separator()
    random.shuffle(private_keys)
    print_wallets_summary(len(private_keys), language)

    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_withdraws, total_withdraws
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            withdraws = await withdraw_token(w3, private_key, profile_num, amount, times, language, proxy)
            successful_withdraws += withdraws
            total_withdraws += times
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_withdraws, total=total_withdraws)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_withdraw('vi'))

