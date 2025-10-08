import os
import sys
import asyncio
from colorama import init, Fore, Style
import inquirer

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền cố định
BORDER_WIDTH = 80

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị banner
def _banner():
    banner = r"""


██╗██████╗░██╗░░░██╗░██████╗  ████████╗███████╗░██████╗████████╗███╗░░██╗███████╗████████╗
██║██╔══██╗╚██╗░██╔╝██╔════╝  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝████╗░██║██╔════╝╚══██╔══╝
██║██████╔╝░╚████╔╝░╚█████╗░  ░░░██║░░░█████╗░░╚█████╗░░░░██║░░░██╔██╗██║█████╗░░░░░██║░░░
██║██╔══██╗░░╚██╔╝░░░╚═══██╗  ░░░██║░░░██╔══╝░░░╚═══██╗░░░██║░░░██║╚████║██╔══╝░░░░░██║░░░
██║██║░░██║░░░██║░░░██████╔╝  ░░░██║░░░███████╗██████╔╝░░░██║░░░██║░╚███║███████╗░░░██║░░░
╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░  ░░░╚═╝░░░╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝╚══════╝░░░╚═╝░░░


    """
    print(f"{Fore.GREEN}{banner:^80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
    print_border("IRYS TESTNET", Fore.GREEN)
    print(f"{Fore.YELLOW}│ {'Liên hệ / Contact'}: {Fore.CYAN}https://t.me/thog099{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Discord'}: {Fore.CYAN}https://discord.gg/MnmYBKfHQf{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Channel Telegram'}: {Fore.CYAN}https://t.me/thogairdrops{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm xóa màn hình
def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Các hàm giả lập cho các lệnh (cần triển khai thực tế)

async def run_faucet(language: str):
    from scripts.faucet import run_faucet as faucet_run
    await faucet_run(language)

async def run_sendtx(language: str):
    from scripts.sendtx import run_sendtx as sendtx_run
    await sendtx_run(language)

async def run_deploytoken(language: str):
    from scripts.deploytoken import run_deploytoken as deploytoken_run
    await deploytoken_run(language)

async def run_sendtoken(language: str):
    from scripts.sendtoken import run_sendtoken as sendtoken_run
    await sendtoken_run(language)

async def run_nftcollection(language: str):
    from scripts.nftcollection import run_nftcollection as nftcollection_run
    await nftcollection_run(language)

async def run_deposit(language: str):
    from scripts.deposit import run_deposit as deposit_run
    await deposit_run(language)

async def run_withdraw(language: str):
    from scripts.withdraw import run_withdraw as withdraw_run
    await withdraw_run(language)

async def run_spritetype(language: str):
    from scripts.spritetype import run_spritetype as spritetype_run
    await spritetype_run(language)

async def run_snake(language: str):
    from scripts.snake import run_snake as snake_run
    await snake_run(language)

async def run_asteroids(language: str):
    from scripts.asteroids import run_asteroids as asteroids_run
    await asteroids_run(language)

async def run_hexshot(language: str):
    from scripts.hexshot import run_hexshot as hexshot_run
    await hexshot_run(language)

async def run_missile(language: str):
    from scripts.missile import run_missile as missile_run
    await missile_run(language)
    
async def cmd_exit(language: str):
    print_border(f"Exiting...", Fore.GREEN)
    sys.exit(0)

# Danh sách lệnh menu
SCRIPT_MAP = {
    "faucet": run_faucet,
    "sendtx": run_sendtx,
    "deploytoken": run_deploytoken,
    "sendtoken": run_sendtoken,
    "nftcollection": run_nftcollection,
    "deposit": run_deposit,
    "withdraw": run_withdraw,
    "spritetype": run_spritetype,
    "snake": run_snake,
    "asteroids": run_asteroids,
    "hexshot": run_hexshot,
    "missile": run_missile,
    "exit": cmd_exit
}

def get_available_scripts(language):
    scripts = {
        'vi': [
            {"name": "1. Faucet token [ IRYS ] | Irys Testnet", "value": "faucet", "locked": True},
            
            {"name": "2. Deposit IRYS │ Irys Testnet", "value": "deposit", "locked": True},
            {"name": "3. Withdraw IRYS │ Irys Testnet", "value": "withdraw", "locked": True},
            {"name": "4. Tự động chơi game Spritetype │ Irys Testnet", "value": "spritetype", "locked": True},
            {"name": "5. Tự động chơi game Snake │ Irys Testnet", "value": "snake", "locked": True},
            {"name": "6. Tự động chơi game Asteroids │ Irys Testnet", "value": "asteroids", "locked": True},
            {"name": "7. Tự động chơi game Hexshot │ Irys Testnet", "value": "hexshot", "locked": True},
            {"name": "8. Tự động chơi game Missile │ Irys Testnet", "value": "missile", "locked": True},

          
            {"name": "9. Deploy NFT - Quản lý bộ sưu tập NFT [ Tạo | Mint | Đốt ] | Irys Testnet", "value": "nftcollection"},
            {"name": "10. Send TX ngẫu nhiên hoặc File (address.txt) | Irys Testnet", "value": "sendtx"},
            {"name": "11. Deploy Token smart-contract | Irys Testnet", "value": "deploytoken"},
            {"name": "12. Send Token ERC20 ngẫu nhiên hoặc File (addressERC20.txt) | Irys Testnet", "value": "sendtoken"},

            {"name": "X. Exit", "value": "exit"},
            
        ],
        'en': [
            {"name": "1. Faucet token [ IRYS ] | Irys Testnet", "value": "faucet", "locked": True},
            
            {"name": "2. Deposit IRYS │ Irys Testnet", "value": "deposit", "locked": True},
            {"name": "3. Withdraw IRYS │ Irys Testnet", "value": "withdraw", "locked": True},
            {"name": "4. Automatically play Spritetype │ Irys Testnet", "value": "spritetype", "locked": True},
            {"name": "5. Automatically play Snake │ Irys Testnet", "value": "snake", "locked": True},
            {"name": "6. Automatically play Asteroids │ Irys Testnet", "value": "asteroids", "locked": True},
            {"name": "7. Automatically play Hexshot │ Irys Testnet", "value": "hexshot", "locked": True},
            {"name": "8. Automatically play Missile │ Irys Testnet", "value": "missile", "locked": True},
            

            {"name": "9. Deploy NFT - Manage NFT Collection [ Create | Mint | Burn ] | Irys Testnet", "value": "nftcollection"},
            {"name": "10. Send Random TX or File (address.txt) | Irys Testnet", "value": "sendtx"},
            {"name": "11. Deploy Token smart-contract | Irys Testnet", "value": "deploytoken"},
            {"name": "12. Send Token ERC20 Random or File (addressERC20.txt) | Irys Testnet", "value": "sendtoken"},

            {"name": "X. Exit", "value": "exit"},
        ]
    }
    return scripts[language]

def run_script(script_func, language):
    """Chạy script bất kể nó là async hay không."""
    if asyncio.iscoroutinefunction(script_func):
        asyncio.run(script_func(language))
    else:
        script_func(language)

def select_language():
    while True:
        _clear()
        _banner()
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN NGÔN NGỮ / SELECT LANGUAGE", Fore.YELLOW)
        questions = [
            inquirer.List('language',
                          message=f"{Fore.CYAN}Vui lòng chọn / Please select:{Style.RESET_ALL}",
                          choices=[("1. Tiếng Việt", 'vi'), ("2. English", 'en')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['language'] in ['vi', 'en']:
            return answer['language']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def main():
    _clear()
    _banner()
    language = select_language()

    messages = {
        "vi": {
            "running": "Đang thực thi: {}",
            "completed": "Đã hoàn thành: {}",
            "error": "Lỗi: {}",
            "press_enter": "Nhấn Enter để tiếp tục...",
            "menu_title": "MENU CHÍNH",
            "select_script": "Chọn script để chạy",
            "locked": "🔒 Script này bị khóa! Vui lòng vào group hoặc Role Discord [ OG - Donate ] để mở khóa."
        },
        "en": {
            "running": "Running: {}",
            "completed": "Completed: {}",
            "error": "Error: {}",
            "press_enter": "Press Enter to continue...",
            "menu_title": "MAIN MENU",
            "select_script": "Select script to run",
            "locked": "🔒 This script is locked! Please join the discord group or role [ OG - Donate ] to unlock."
        }
    }

    while True:
        _clear()
        _banner()
        print(f"{Fore.YELLOW}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border(messages[language]["menu_title"], Fore.YELLOW)
        print(f"{Fore.CYAN}│ {messages[language]['select_script'].center(BORDER_WIDTH - 4)} │{Style.RESET_ALL}")

        available_scripts = get_available_scripts(language)
        questions = [
            inquirer.List('script',
                          message=f"{Fore.CYAN}{messages[language]['select_script']}{Style.RESET_ALL}",
                          choices=[script["name"] for script in available_scripts],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            continue

        selected_script_name = answers['script']
        selected_script = next(script for script in available_scripts if script["name"] == selected_script_name)
        selected_script_value = selected_script["value"]

        if selected_script.get("locked"):
            _clear()
            _banner()
            print_border("SCRIPT BỊ KHÓA / LOCKED", Fore.RED)
            print(f"{Fore.YELLOW}{messages[language]['locked']}")
            print('')
            print(f"{Fore.CYAN}→ Telegram: https://t.me/thogairdrops")
            print(f"{Fore.CYAN}→ Donate: https://buymecafe.vercel.app{Style.RESET_ALL}")
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        script_func = SCRIPT_MAP.get(selected_script_value)
        if script_func is None:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Chưa triển khai / Not implemented'}: {selected_script_name}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        try:
            print(f"{Fore.CYAN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["running"].format(selected_script_name), Fore.CYAN)
            run_script(script_func, language)
            print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["completed"].format(selected_script_name), Fore.GREEN)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
        except Exception as e:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["error"].format(str(e)), Fore.RED)
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")

if __name__ == "__main__":
    main()

