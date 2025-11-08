import os
import sys
import shutil
import getpass
import json
from datetime import datetime
import subprocess
import platform
import random
import time
import importlib
import requests

# Mirage Store API endpoint
STORE_API = "https://miragestore.onrender.com"
STORE_API_PING = "https://miragestore.onrender.com/ping"

def ensure_imports(modules):
    """
    Ensure all modules in the list can be imported.
    If missing, attempt to install via pip.
    """
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError:
            print(f"[!] Missing module '{mod}', attempting to install...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", mod])
            print(f"[+] Installed '{mod}' successfully.")
            importlib.import_module(mod)  # import it again
        except Exception as e:
            print(f"[!] Error checking module '{mod}': {e}")


ensure_imports([
    "colorama",
    "fortune",
    "random",
    "requests"
])


# ---------- Color support ----------
try:
    from colorama import init, Fore, Style
except ImportError:
    os.system("pip install colorama")
    from colorama import init, Fore, Style

init(autoreset=True)

# ---------- User Management ----------
USERS_DIR = os.path.expanduser("~/MirageUsers")
USERS_FILE = os.path.join(USERS_DIR, "users.json")
HISTORY_FILE = "mirage_history.txt"
ALIASES_FILE = "mirage_aliases.json"
MAX_HISTORY = 100
GUEST_USER = "guest"

def ensure_users_dir():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def create_user(username, password):
    users = load_users()
    if username in users:
        print(Fore.YELLOW + f"User '{username}' already exists!")
    else:
        users[username] = password
        os.makedirs(os.path.join(USERS_DIR, username), exist_ok=True)
        save_users(users)
        print(Fore.GREEN + f"User '{username}' created!")

def authenticate(username, password):
    users = load_users()
    return users.get(username) == password

def login():
    ensure_users_dir()
    users = load_users()
    print(Fore.CYAN + "Existing users: " + (", ".join([u for u in users.keys() if u != GUEST_USER]) if users else "No users yet."))
    print(Fore.YELLOW + "Tip: Type 'guest' or press Enter twice to use Guest mode")
    
    empty_count = 0
    while True:
        username = input(Fore.MAGENTA + "Username: ").strip()
        
        # Handle empty input (guest mode trigger)
        if not username:
            empty_count += 1
            if empty_count >= 2:
                print(Fore.CYAN + "\n🌟 Entering Guest Mode...")
                time.sleep(0.5)
                # Create guest user directory if doesn't exist
                guest_dir = os.path.join(USERS_DIR, GUEST_USER)
                if not os.path.exists(guest_dir):
                    os.makedirs(guest_dir)
                os.chdir(guest_dir)
                print(Fore.YELLOW + "⚠️  Guest mode: Changes will persist until you logout")
                print(Fore.GREEN + f"Logged in as '{GUEST_USER}'\n")
                return GUEST_USER
            continue
        
        # Reset empty count if user types something
        empty_count = 0
        
        # Handle guest mode by username
        if username.lower() == "guest":
            print(Fore.CYAN + "\n🌟 Entering Guest Mode...")
            time.sleep(0.5)
            guest_dir = os.path.join(USERS_DIR, GUEST_USER)
            if not os.path.exists(guest_dir):
                os.makedirs(guest_dir)
            os.chdir(guest_dir)
            print(Fore.YELLOW + "⚠️  Guest mode: Changes will persist until you logout")
            print(Fore.GREEN + f"Logged in as '{GUEST_USER}'\n")
            return GUEST_USER
        
        # Normal user login
        if username in users:
            password = getpass.getpass("Password: ")
            if authenticate(username, password):
                print(Fore.GREEN + f"Logged in as '{username}'\n")
                os.chdir(os.path.join(USERS_DIR, username))
                return username
            else:
                print(Fore.RED + "Incorrect password!")
        else:
            password = getpass.getpass("New password: ")
            create_user(username, password)
            os.chdir(os.path.join(USERS_DIR, username))
            return username

def switch_user():
    print(Fore.CYAN + "\nSwitching user...")
    return login()

def cleanup_guest():
    """Clean up guest user directory"""
    guest_dir = os.path.join(USERS_DIR, GUEST_USER)
    if os.path.exists(guest_dir):
        try:
            # Change to parent directory first to avoid "in use" error
            os.chdir(USERS_DIR)
            shutil.rmtree(guest_dir)
            print(Fore.CYAN + "✓ Guest session cleaned up")
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Could not clean up guest directory: {e}")
    """Clean up guest user directory"""
    guest_dir = os.path.join(USERS_DIR, GUEST_USER)
    if os.path.exists(guest_dir):
        try:
            shutil.rmtree(guest_dir)
            print(Fore.CYAN + "✓ Guest session cleaned up")
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Could not clean up guest directory: {e}")

def delete_user(current_user):
    """Delete a user account"""
    if current_user == GUEST_USER:
        print(Fore.RED + "Cannot delete guest account!")
        return
    
    users = load_users()
    print(Fore.CYAN + "Existing users: " + ", ".join([u for u in users.keys() if u != GUEST_USER]))
    username = input(Fore.YELLOW + "Username to delete: ").strip()
    
    if username == GUEST_USER:
        print(Fore.RED + "Cannot delete guest account!")
        return
    
    if username not in users:
        print(Fore.RED + "User not found.")
        return
    
    # If deleting a different user, require password
    if username != current_user:
        password = getpass.getpass(Fore.YELLOW + f"Enter password for '{username}': ")
        if not authenticate(username, password):
            print(Fore.RED + "Incorrect password! Deletion cancelled.")
            return
    
    confirm = input(Fore.RED + f"Are you sure you want to delete '{username}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        # Delete user directory
        user_dir = os.path.join(USERS_DIR, username)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        
        # Remove from users list
        del users[username]
        save_users(users)
        print(Fore.GREEN + f"User '{username}' deleted successfully!")
    else:
        print(Fore.YELLOW + "Deletion cancelled.")

# ---------- Command History ----------
def save_to_history(cmd):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = f.read().splitlines()
        
        history.append(cmd)
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(history))
    except:
        pass

def show_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            lines = f.read().splitlines()
            for i, line in enumerate(lines[-20:], 1):
                print(Fore.CYAN + f"{i}. " + Fore.WHITE + line)
    else:
        print(Fore.YELLOW + "No command history yet.")

def clear_history():
    """Clear command history"""
    if os.path.exists(HISTORY_FILE):
        confirm = input(Fore.YELLOW + "Clear all command history? (yes/no): ").strip().lower()
        if confirm == "yes":
            os.remove(HISTORY_FILE)
            print(Fore.GREEN + "✓ History cleared!")
        else:
            print(Fore.YELLOW + "Cancelled.")
    else:
        print(Fore.YELLOW + "No history to clear.")

# ---------- Alias Management ----------
def load_aliases():
    if os.path.exists(ALIASES_FILE):
        try:
            with open(ALIASES_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_aliases(aliases):
    with open(ALIASES_FILE, "w") as f:
        json.dump(aliases, f, indent=2)

def manage_aliases(args):
    """Manage command aliases"""
    aliases = load_aliases()
    
    if not args or args[0] == "list":
        # List all aliases
        if not aliases:
            print(Fore.YELLOW + "No aliases defined.")
        else:
            print(Fore.CYAN + "Current aliases:")
            for name, command in aliases.items():
                print(Fore.YELLOW + f"  {name} " + Fore.WHITE + f"→ {command}")
    
    elif args[0] == "add":
        # Add new alias: alias add <name> <command>
        if len(args) < 3:
            print(Fore.RED + "Usage: alias add <name> <command>")
            return
        
        alias_name = args[1]
        alias_command = " ".join(args[2:])
        
        # Prevent aliasing built-in commands
        builtin_commands = ["alias", "help", "exit", "switch", "dusr"]
        if alias_name in builtin_commands:
            print(Fore.RED + f"Cannot alias built-in command '{alias_name}'")
            return
        
        aliases[alias_name] = alias_command
        save_aliases(aliases)
        print(Fore.GREEN + f"✓ Alias '{alias_name}' → '{alias_command}' created!")
    
    elif args[0] == "del" or args[0] == "remove":
        # Delete alias: alias del <name>
        if len(args) < 2:
            print(Fore.RED + "Usage: alias del <name>")
            return
        
        alias_name = args[1]
        if alias_name in aliases:
            del aliases[alias_name]
            save_aliases(aliases)
            print(Fore.GREEN + f"✓ Alias '{alias_name}' deleted!")
        else:
            print(Fore.RED + f"Alias '{alias_name}' not found.")
    
    else:
        print(Fore.RED + "Unknown subcommand. Use: list, add, del")

def expand_alias(cmd, aliases):
    """Expand alias if it exists"""
    parts = cmd.split(maxsplit=1)
    if parts[0] in aliases:
        # Replace alias with its command
        expanded = aliases[parts[0]]
        if len(parts) > 1:
            expanded += " " + parts[1]
        return expanded
    return cmd

# ---------- Splash Screen ----------
def clear():
    os.system("clear" if platform.system() != "Windows" else "cls")

def splash_screen():
    clear()
    art = r"""
 __  __ _                         ___  ____  
|  \/  (_)_ __ __ _  __ _  ___   / _ \/ ___| 
| |\/| | | '__/ _` |/ _` |/ _ \ | | | \___ \ 
| |  | | | | | (_| | (_| |  __/ | |_| |___) |
|_|  |_|_|_|  \__,_|\__, |\___|  \___/|____/ 
                    |___/                     
"""
    width = shutil.get_terminal_size((50, 20)).columns
    # Sunset gradient: Red -> Orange -> Yellow -> Magenta (purple sky)
    sunset_colors = [Fore.RED, Fore.RED, Fore.YELLOW, Fore.YELLOW, Fore.MAGENTA, Fore.MAGENTA]
    
    lines = art.splitlines()
    for i, line in enumerate(lines):
        if line.strip():  # Only print non-empty lines
            color = sunset_colors[i % len(sunset_colors)]
            print(color + line.center(width))
    
    # Sunset-themed welcome message
    print(Fore.YELLOW + "\n✨ Welcome to Mirage ✨\n".center(width))
    print(Fore.MAGENTA + "Version 1.1 'eXchange'  \n".center(width))
    print(Fore.CYAN + "Type 'help' for commands\n".center(width))

# ---------- New Utility Functions ----------
def echo_command(args):
    """Echo text to console"""
    print(Fore.WHITE + " ".join(args))

def count_files(path="."):
    """Count files and directories"""
    try:
        items = os.listdir(path)
        files = [i for i in items if os.path.isfile(os.path.join(path, i))]
        dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
        
        print(Fore.CYAN + f"📁 Directories: {len(dirs)}")
        print(Fore.CYAN + f"📄 Files: {len(files)}")
        print(Fore.CYAN + f"📊 Total: {len(items)}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def disk_usage(path="."):
    """Show disk usage of directory"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                print(Fore.CYAN + f"💾 Disk usage: {total_size:.2f} {unit}")
                break
            total_size /= 1024.0
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def whoami(username):
    """Display current user info"""
    print(Fore.CYAN + "═" * 40)
    print(Fore.YELLOW + "Username: " + Fore.WHITE + username)
    print(Fore.YELLOW + "Home: " + Fore.WHITE + os.path.join(USERS_DIR, username))
    print(Fore.YELLOW + "Current Dir: " + Fore.WHITE + os.getcwd())
    if username == GUEST_USER:
        print(Fore.YELLOW + "Mode: " + Fore.MAGENTA + "Guest (Temporary)")
    print(Fore.CYAN + "═" * 40)

def create_link(source, link_name):
    """Create a symbolic link"""
    try:
        if not os.path.exists(source):
            print(Fore.RED + f"Source '{source}' does not exist.")
            return
        
        os.symlink(source, link_name)
        print(Fore.GREEN + f"✓ Created link '{link_name}' → '{source}'")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def rename_file(old_name, new_name):
    """Rename a file or directory"""
    try:
        if not os.path.exists(old_name):
            print(Fore.RED + f"'{old_name}' does not exist.")
            return
        
        os.rename(old_name, new_name)
        print(Fore.GREEN + f"✓ Renamed '{old_name}' to '{new_name}'")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def head_file(filename, lines=10):
    """Show first N lines of a file"""
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i >= lines:
                    break
                print(line, end='')
    except FileNotFoundError:
        print(Fore.RED + "File not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def tail_file(filename, lines=10):
    """Show last N lines of a file"""
    try:
        with open(filename, 'r') as f:
            all_lines = f.readlines()
            for line in all_lines[-lines:]:
                print(line, end='')
    except FileNotFoundError:
        print(Fore.RED + "File not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def grep_file(pattern, filename):
    """Search for pattern in file"""
    try:
        matches = 0
        with open(filename, 'r') as f:
            for i, line in enumerate(f, 1):
                if pattern.lower() in line.lower():
                    print(Fore.YELLOW + f"{i}: " + Fore.WHITE + line.strip())
                    matches += 1
        
        if matches == 0:
            print(Fore.YELLOW + f"No matches found for '{pattern}'")
        else:
            print(Fore.GREEN + f"\n✓ Found {matches} matches")
    except FileNotFoundError:
        print(Fore.RED + "File not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def wc_file(filename):
    """Count lines, words, and characters in file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
            lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
            words = len(content.split())
            chars = len(content)
        
        print(Fore.CYAN + f"📏 Lines: {lines}")
        print(Fore.CYAN + f"📝 Words: {words}")
        print(Fore.CYAN + f"🔤 Characters: {chars}")
    except FileNotFoundError:
        print(Fore.RED + "File not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def uptime_info():
    """Show system uptime (simulated for Mirage)"""
    try:
        # Get Python process uptime as proxy
        print(Fore.CYAN + "⏱️  Mirage Session Info:")
        print(Fore.YELLOW + f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(Fore.YELLOW + f"   Platform: {platform.system()} {platform.release()}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def show_fortune():
    # Try to use the fortune library if available
    try:
        import fortune as fortune_lib
        try:
            fortune_text = fortune_lib.get_random_fortune()
            print(Fore.MAGENTA + "\n💭 Fortune Cookie:\n")
            print(Fore.WHITE + fortune_text + "\n")
            return
        except Exception:
            # If the library fails, fallback
            pass
    except ImportError:
        # Library not installed, fallback
        pass

    # Fallback built-in fortunes
    fortunes = [
        "You will find a hidden gem today.",
        "Be wary of unexpected surprises.",
        "A fresh start will put you on your path.",
        "Something new is about to happen.",
        "Patience is your ally today.",
        "Fortune favors the bold.",
        "An old friend will contact you soon.",
        "Today is a perfect day to learn something new.",
        "Happiness comes from unexpected places.",
        "please send me a fortunes.txt file i had to think of crap to write PLEASE send me a fortune.txt reach me on discord at @.itzyaboigalaxy."
    ]

    # Pick one random fortune
    import random
    print(Fore.MAGENTA + "\n💭 Fortune Cookie:\n")
    print(Fore.WHITE + random.choice(fortunes) + "\n")
    """Display a random fortune/quote"""
    try:
        # Try to use the fortune library if available
        import fortune as fortune_lib
        
        try:
            return
        except:
            pass
    except ImportError:
        pass
    
    # Fallback to built-in fortunes if library not available
    fortunes = [
        "there are no fortunes. something effed up."
    ]
    print(Fore.MAGENTA + "\n💭 " + random.choice(fortunes) + "\n")

# ---------- Existing Utility Functions ----------
def help_menu():
    print(Fore.CYAN + "═" * 60)
    print(Fore.CYAN + "Available commands:")
    print(Fore.CYAN + "═" * 60)
    print(Fore.YELLOW + "  help             " + Fore.WHITE + "- Show this menu")
    print(Fore.YELLOW + "  ls [-a]          " + Fore.WHITE + "- List files (-a shows hidden)")
    print(Fore.YELLOW + "  pwd              " + Fore.WHITE + "- Show current directory")
    print(Fore.YELLOW + "  cd DIR           " + Fore.WHITE + "- Change directory")
    print(Fore.CYAN + "\n  === .mapp Applications ===")
    print(Fore.YELLOW + "  mapp list        " + Fore.WHITE + "- List all .mapp files")
    print(Fore.YELLOW + "  mapp new FILE    " + Fore.WHITE + "- Create new .mapp template")
    print(Fore.YELLOW + "  run FILE.mapp    " + Fore.WHITE + "- Run a .mapp application")
    print(Fore.CYAN + "\n  === Mirage Store ===")
    print(Fore.YELLOW + "  ms list          " + Fore.WHITE + "- List apps in the store")
    print(Fore.YELLOW + "  ms download FILE " + Fore.WHITE + "- Download app from store")
    print(Fore.YELLOW + "  ms upload FILE   " + Fore.WHITE + "- Upload app to store")
    print(Fore.YELLOW + "  ms ping          " + Fore.WHITE + "- Ping the MirageStore server")

    print(Fore.CYAN + "\n  === File Operations ===")
    print(Fore.YELLOW + "  cat FILE         " + Fore.WHITE + "- Show file contents")
    print(Fore.YELLOW + "  head FILE [N]    " + Fore.WHITE + "- Show first N lines (default 10)")
    print(Fore.YELLOW + "  tail FILE [N]    " + Fore.WHITE + "- Show last N lines (default 10)")
    print(Fore.YELLOW + "  grep PAT FILE    " + Fore.WHITE + "- Search for pattern in file")
    print(Fore.YELLOW + "  wc FILE          " + Fore.WHITE + "- Count lines, words, chars")
    print(Fore.YELLOW + "  touch FILE       " + Fore.WHITE + "- Create empty file")
    print(Fore.YELLOW + "  mkdir DIR        " + Fore.WHITE + "- Create directory")
    print(Fore.YELLOW + "  rm FILE          " + Fore.WHITE + "- Delete file/directory")
    print(Fore.YELLOW + "  cp SRC DST       " + Fore.WHITE + "- Copy file")
    print(Fore.YELLOW + "  mv SRC DST       " + Fore.WHITE + "- Move file")
    print(Fore.YELLOW + "  rename OLD NEW   " + Fore.WHITE + "- Rename file/directory")
    print(Fore.YELLOW + "  ln SRC LINK      " + Fore.WHITE + "- Create symbolic link")
    print(Fore.YELLOW + "  find TERM        " + Fore.WHITE + "- Search for files")
    print(Fore.YELLOW + "  tree             " + Fore.WHITE + "- Show directory tree")
    print(Fore.YELLOW + "  count            " + Fore.WHITE + "- Count files and directories")
    print(Fore.YELLOW + "  du               " + Fore.WHITE + "- Show disk usage")
    print(Fore.YELLOW + "  info FILE        " + Fore.WHITE + "- Show file information")
    print(Fore.YELLOW + "  pull PATH        " + Fore.WHITE + "- Download file to current directory")
    print(Fore.YELLOW + "  run FILE         " + Fore.WHITE + "- Run/open file with default app")
    print(Fore.YELLOW + "  echo TEXT        " + Fore.WHITE + "- Echo text to console")
    print(Fore.YELLOW + "  calc             " + Fore.WHITE + "- Open calculator")
    print(Fore.YELLOW + "  notes            " + Fore.WHITE + "- Open notes")
    print(Fore.YELLOW + "  todo             " + Fore.WHITE + "- Manage todo list")
    print(Fore.YELLOW + "  apps             " + Fore.WHITE + "- List mini apps")
    print(Fore.YELLOW + "  edit FILE        " + Fore.WHITE + "- Open file in editor")
    print(Fore.YELLOW + "  history          " + Fore.WHITE + "- Show command history")
    print(Fore.YELLOW + "  history clear    " + Fore.WHITE + "- Clear command history")
    print(Fore.YELLOW + "  sysinfo          " + Fore.WHITE + "- Show system information")
    print(Fore.YELLOW + "  uptime           " + Fore.WHITE + "- Show session uptime")
    print(Fore.YELLOW + "  whoami           " + Fore.WHITE + "- Show current user info")
    print(Fore.YELLOW + "  fortune          " + Fore.WHITE + "- Display a random quote")
    print(Fore.YELLOW + "  alias            " + Fore.WHITE + "- Manage command aliases")
    print(Fore.YELLOW + "  switch           " + Fore.WHITE + "- Switch user")
    print(Fore.YELLOW + "  dusr             " + Fore.WHITE + "- Delete a user account")
    print(Fore.YELLOW + "  logout           " + Fore.WHITE + "- Logout and return to login")
    print(Fore.YELLOW + "  clear            " + Fore.WHITE + "- Clear screen")
    print(Fore.YELLOW + "  exit             " + Fore.WHITE + "- Exit Mirage")
    print(Fore.CYAN + "═" * 60)
    
def run_calculator():
    print(Fore.GREEN + "Simple Calculator: type 'exit' to leave")
    print(Fore.CYAN + "Supports: +, -, *, /, **, sqrt(), sin(), cos(), tan()")
    import math
    while True:
        try:
            expr = input(Fore.MAGENTA + "calc> ").strip()
            if expr.lower() == "exit":
                break
            # Safe eval with math functions
            result = eval(expr, {"__builtins__": None}, {
                "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "pi": math.pi, "e": math.e
            })
            print(Fore.CYAN + str(result))
        except Exception as e:
            print(Fore.RED + "Error:", e)

def run_notes():
    notes_file = "mirage_notes.txt"
    print(Fore.GREEN + "Notes: type 'exit' to leave, 'view' to see all notes")
    while True:
        line = input(Fore.MAGENTA + "notes> ").strip()
        if line.lower() == "exit":
            break
        elif line.lower() == "view":
            if os.path.exists(notes_file):
                with open(notes_file, "r") as f:
                    print(Fore.CYAN + f.read())
            else:
                print(Fore.YELLOW + "No notes yet.")
        else:
            with open(notes_file, "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {line}\n")
            print(Fore.GREEN + "Note saved!")

def run_todo():
    todo_file = "mirage_todo.json"
    
    def load_todos():
        if os.path.exists(todo_file):
            with open(todo_file, "r") as f:
                return json.load(f)
        return []
    
    def save_todos(todos):
        with open(todo_file, "w") as f:
            json.dump(todos, f, indent=2)
    
    print(Fore.GREEN + "Todo Manager: 'add', 'list', 'done NUM', 'del NUM', 'exit'")
    
    while True:
        cmd = input(Fore.MAGENTA + "todo> ").strip()
        
        if cmd.lower() == "exit":
            break
        elif cmd.lower() == "list":
            todos = load_todos()
            if not todos:
                print(Fore.YELLOW + "No todos yet!")
            else:
                for i, todo in enumerate(todos, 1):
                    status = Fore.GREEN + "✓" if todo.get("done") else Fore.RED + "✗"
                    print(f"{status} {i}. {Fore.WHITE}{todo['task']}")
        elif cmd.lower().startswith("add "):
            task = cmd[4:].strip()
            todos = load_todos()
            todos.append({"task": task, "done": False, "created": datetime.now().isoformat()})
            save_todos(todos)
            print(Fore.GREEN + "Todo added!")
        elif cmd.lower().startswith("done "):
            try:
                num = int(cmd[5:].strip()) - 1
                todos = load_todos()
                todos[num]["done"] = True
                save_todos(todos)
                print(Fore.GREEN + "Todo marked as done!")
            except:
                print(Fore.RED + "Invalid todo number")
        elif cmd.lower().startswith("del "):
            try:
                num = int(cmd[4:].strip()) - 1
                todos = load_todos()
                todos.pop(num)
                save_todos(todos)
                print(Fore.GREEN + "Todo deleted!")
            except:
                print(Fore.RED + "Invalid todo number")
        else:
            print(Fore.RED + "Unknown command. Use: add, list, done NUM, del NUM, exit")

def list_apps():
    print(Fore.CYAN + "Mini Apps:")
    print(Fore.YELLOW + "  calc   " + Fore.WHITE + "- Calculator")
    print(Fore.YELLOW + "  notes  " + Fore.WHITE + "- Notes")
    print(Fore.YELLOW + "  todo   " + Fore.WHITE + "- Todo Manager")

def run_editor(filename):
    editor_path = os.path.join(os.path.dirname(__file__), "mirage_editor.py")
    if not os.path.exists(editor_path):
        print(Fore.RED + "mirage_editor.py not found!")
        return
    subprocess.run([sys.executable, editor_path, filename])

def show_tree(path=".", prefix="", is_last=True):
    """Display directory tree structure"""
    try:
        items = sorted(os.listdir(path))
        items = [i for i in items if not i.startswith('.')]
        
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            item_path = os.path.join(path, item)
            
            connector = "└── " if is_last_item else "├── "
            if os.path.isdir(item_path):
                print(Fore.BLUE + prefix + connector + item + "/")
                extension = "    " if is_last_item else "│   "
                show_tree(item_path, prefix + extension, is_last_item)
            else:
                print(Fore.WHITE + prefix + connector + item)
    except PermissionError:
        print(Fore.RED + prefix + "[Permission Denied]")

def show_file_info(filename):
    """Show detailed file information"""
    if not os.path.exists(filename):
        print(Fore.RED + "File not found.")
        return
    
    stat = os.stat(filename)
    print(Fore.CYAN + "═" * 40)
    print(Fore.YELLOW + "File: " + Fore.WHITE + filename)
    print(Fore.YELLOW + "Size: " + Fore.WHITE + f"{stat.st_size} bytes")
    print(Fore.YELLOW + "Type: " + Fore.WHITE + ("Directory" if os.path.isdir(filename) else "File"))
    print(Fore.YELLOW + "Modified: " + Fore.WHITE + datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
    print(Fore.YELLOW + "Created: " + Fore.WHITE + datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'))
    print(Fore.CYAN + "═" * 40)

def show_sysinfo():
    """Show system information"""
    print(Fore.CYAN + "═" * 40)
    print(Fore.YELLOW + "System: " + Fore.WHITE + platform.system())
    print(Fore.YELLOW + "Platform: " + Fore.WHITE + platform.platform())
    print(Fore.YELLOW + "Python: " + Fore.WHITE + platform.python_version())
    print(Fore.YELLOW + "CWD: " + Fore.WHITE + os.getcwd())
    print(Fore.CYAN + "═" * 40)

def find_files(search_term, path="."):
    """Search for files matching term"""
    found = []
    try:
        for root, dirs, files in os.walk(path):
            for name in files + dirs:
                if search_term.lower() in name.lower():
                    full_path = os.path.join(root, name)
                    found.append(full_path)
    except PermissionError:
        pass
    
    if found:
        print(Fore.GREEN + f"Found {len(found)} matches:")
        for f in found[:20]:  # Limit to 20 results
            if os.path.isdir(f):
                print(Fore.BLUE + f + "/")
            else:
                print(Fore.WHITE + f)
        if len(found) > 20:
            print(Fore.YELLOW + f"... and {len(found) - 20} more")
    else:
        print(Fore.YELLOW + "No matches found.")

def pull_file(source_path):
    """Pull (download) a file from anywhere to current directory"""
    source_path = os.path.expanduser(source_path)
    
    if not os.path.exists(source_path):
        print(Fore.RED + f"Source file '{source_path}' not found.")
        return
    
    if os.path.isdir(source_path):
        print(Fore.RED + "Cannot pull a directory. Use a file path.")
        return
    
    filename = os.path.basename(source_path)
    dest_path = os.path.join(os.getcwd(), filename)
    
    # Check if file already exists
    if os.path.exists(dest_path):
        overwrite = input(Fore.YELLOW + f"'{filename}' already exists. Overwrite? (yes/no): ").strip().lower()
        if overwrite != "yes":
            print(Fore.YELLOW + "Pull cancelled.")
            return
    
    try:
        # Get file size
        file_size = os.path.getsize(source_path)
        
        # Show downloading message
        print(Fore.CYAN + f"Downloading '{filename}'...")
        
        # Simple progress bar
        bar_length = 30
        
        # Read and write in chunks to show progress
        with open(source_path, 'rb') as src:
            with open(dest_path, 'wb') as dst:
                bytes_copied = 0
                chunk_size = max(1024, file_size // 20)  # At least 1KB chunks
                
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
                    bytes_copied += len(chunk)
                    
                    # Calculate progress
                    progress = bytes_copied / file_size if file_size > 0 else 1
                    filled = int(bar_length * progress)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    percent = int(progress * 100)
                    
                    # Print progress bar
                    print(f"\r{Fore.GREEN}[{bar}] {percent}%", end='', flush=True)
                    
                    # Small delay for visibility (only if file is large enough)
                    if file_size > 10000:
                        time.sleep(0.02)
        
        # Complete
        print(f"\r{Fore.GREEN}[{'█' * bar_length}] 100%")
        print(Fore.GREEN + f"✓ Downloaded '{filename}' to current directory")
        print(Fore.CYAN + f"  Source: {source_path}")
        print(Fore.CYAN + f"  Destination: {dest_path}")
    except Exception as e:
        print(Fore.RED + f"Error pulling file: {e}")

def parse_mapp_file(filename):
    """Parse a .mapp (Mirage Application) file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Extract JSON metadata
        json_start = content.find('[JSON]')
        json_end = content.find('[JSONEND]')
        
        # Extract Python code
        py_start = content.find('[PY]')
        py_end = content.find('[PYEND]')
        
        if json_start == -1 or json_end == -1:
            print(Fore.RED + "Error: Invalid .mapp format - missing [JSON] or [JSONEND]")
            return None, None
        
        if py_start == -1 or py_end == -1:
            print(Fore.RED + "Error: Invalid .mapp format - missing [PY] or [PYEND]")
            return None, None
        
        # Parse JSON metadata
        json_str = content[json_start + 6:json_end].strip()
        try:
            metadata = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(Fore.RED + f"Error parsing JSON metadata: {e}")
            return None, None
        
        # Extract Python code
        code = content[py_start + 4:py_end].strip()
        
        return metadata, code
    
    except FileNotFoundError:
        print(Fore.RED + "File not found.")
        return None, None
    except Exception as e:
        print(Fore.RED + f"Error reading .mapp file: {e}")
        return None, None

def run_mapp(filename):
    """Run a .mapp (Mirage Application) file"""
    print(Fore.CYAN + f"Loading Mirage Application: {filename}")
    
    metadata, code = parse_mapp_file(filename)
    if metadata is None or code is None:
        return
    
    # Display app info
    print(Fore.CYAN + "═" * 50)
    print(Fore.YELLOW + f"📦 App: " + Fore.WHITE + metadata.get('name', 'Unknown'))
    print(Fore.YELLOW + f"🔖 Version: " + Fore.WHITE + metadata.get('version', 'Unknown'))
    if 'author' in metadata:
        print(Fore.YELLOW + f"👤 Author: " + Fore.WHITE + metadata['author'])
    if 'description' in metadata:
        print(Fore.YELLOW + f"📝 Description: " + Fore.WHITE + metadata['description'])
    print(Fore.CYAN + "═" * 50)

    run_confirm = input(Fore.YELLOW + "Run this application? (yes/no): ").strip().lower()
    if run_confirm != 'yes':
        print(Fore.YELLOW + "Execution cancelled.")
        return
    
    print(Fore.GREEN + "\n▶ Running application...\n")
    
    import tempfile, subprocess, os
    
    try:
        # Write the Python section to a temp file
        app_name = metadata.get("name", "MirageApp").replace(" ", "_")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", prefix=f"{app_name}_") as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_path = temp_file.name
        
        # Decide how to run (interactive or silent)
        interactive = metadata.get("interactive", True)
        
        if interactive:
            subprocess.run(["python", temp_path])  # full console access
        else:
            result = subprocess.run(["python", temp_path], capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(Fore.RED + result.stderr)
        
        print(Fore.GREEN + "\n✓ Application completed successfully")
    
    except Exception as e:
        print(Fore.RED + f"\n✗ Application error: {e}")
    finally:
        # Clean up temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass

def create_mapp_template(filename):
    """Create a template .mapp file"""
    if os.path.exists(filename):
        overwrite = input(Fore.YELLOW + f"'{filename}' already exists. Overwrite? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print(Fore.YELLOW + "Cancelled.")
            return
    
    template = '''[JSON]
{
  "name": "My Mirage App",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A simple Mirage application"
}
[JSONEND]
[PY]
# Your Mirage Application Code
print(Fore.CYAN + "Hello from " + metadata['name'] + "!")
print(Fore.YELLOW + "Version: " + metadata['version'])

# You have access to:
# - metadata: The JSON metadata dictionary
# - Fore, Style: Colorama for colored output
# - os, sys, datetime, json: Standard Python modules
# - All standard Python built-ins

# Example: Get user input
name = input(Fore.MAGENTA + "What's your name? ")
print(Fore.GREEN + f"Nice to meet you, {name}!")
[PYEND]
'''
    
    try:
        with open(filename, 'w') as f:
            f.write(template)
        print(Fore.GREEN + f"✓ Created template .mapp file: {filename}")
        print(Fore.CYAN + f"Edit with: edit {filename}")
        print(Fore.CYAN + f"Run with: run {filename}")
    except Exception as e:
        print(Fore.RED + f"Error creating template: {e}")

def list_mapps():
    """List all .mapp files in current directory"""
    mapps = [f for f in os.listdir('.') if f.endswith('.mapp')]
    
    if not mapps:
        print(Fore.YELLOW + "No .mapp files found in current directory.")
        return
    
    print(Fore.CYAN + "═" * 50)
    print(Fore.CYAN + "Mirage Applications (.mapp files):")
    print(Fore.CYAN + "═" * 50)
    
    for mapp_file in sorted(mapps):
        metadata, _ = parse_mapp_file(mapp_file)
        if metadata:
            name = metadata.get('name', 'Unknown')
            version = metadata.get('version', '?')
            print(Fore.BLUE + f"📦 {mapp_file}")
            print(Fore.YELLOW + f"   {name} " + Fore.WHITE + f"v{version}")
            if 'description' in metadata:
                print(Fore.WHITE + f"   {metadata['description']}")
            print()

def run_file(filename):
    """Run a file with its default application"""
    if not os.path.exists(filename):
        print(Fore.RED + f"File '{filename}' not found.")
        return
    
    if os.path.isdir(filename):
        print(Fore.RED + f"'{filename}' is a directory, not a file.")
        return
    
    # Get file extension
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # Handle .mapp files
    if ext == '.mapp':
        run_mapp(filename)
    # Text files open in editor
    elif ext in ['.txt', '.md', '.log', '.cfg', '.conf', '']:
        print(Fore.CYAN + f"Opening '{filename}' in editor...")
        run_editor(filename)
    elif ext == '.py':
        # Python files can be executed
        print(Fore.CYAN + f"Running Python script '{filename}'...")
        try:
            subprocess.run([sys.executable, filename])
        except Exception as e:
            print(Fore.RED + f"Error running script: {e}")
    elif ext in ['.sh', '.bash']:
        # Shell scripts
        print(Fore.CYAN + f"Running shell script '{filename}'...")
        try:
            subprocess.run(['bash', filename])
        except Exception as e:
            print(Fore.RED + f"Error running script: {e}")
    elif ext in ['.html', '.htm']:
        # HTML files - open in browser
        print(Fore.CYAN + f"Opening '{filename}' in browser...")
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(filename))
            print(Fore.GREEN + "✓ Opened in browser")
        except Exception as e:
            print(Fore.RED + f"Error opening in browser: {e}")
    else:
        # Code files and unknown types - just inform the user
        print(Fore.YELLOW + f"Cannot run '{ext}' files. Use 'edit {filename}' to view/edit.")

# ---------- Mirage Store Functions ----------
def mirage_store_list():
    """List all apps in the Mirage Store"""
    try:
        import requests
        print(Fore.CYAN + "📦 Fetching apps from Mirage Store...")
        response = requests.get(f"{STORE_API}/apps", timeout=10)
        
        if response.status_code == 200:
            apps = response.json()
            
            if not apps:
                print(Fore.YELLOW + "No apps in the store yet.")
                return
            
            print(Fore.CYAN + "═" * 60)
            print(Fore.CYAN + "Available Apps in Mirage Store:")
            print(Fore.CYAN + "═" * 60)
            
            for app_file in sorted(apps):
                # Parse the filename to extract info
                # Format could be: filename.mapp or filename-code.mapp
                base_name = app_file.replace('.mapp', '')
                
                print(Fore.BLUE + f"📦 {app_file}")
                
                # Try to download and parse metadata without saving
                try:
                    meta_response = requests.get(f"{STORE_API}/apps/{app_file}", timeout=10)
                    if meta_response.status_code == 200:
                        # Parse the .mapp file to extract metadata
                        content = meta_response.text
                        json_start = content.find('[JSON]')
                        json_end = content.find('[JSONEND]')
                        
                        if json_start != -1 and json_end != -1:
                            json_str = content[json_start + 6:json_end].strip()
                            metadata = json.loads(json_str)
                            
                            name = metadata.get('name', 'Unknown')
                            version = metadata.get('version', '?')
                            author = metadata.get('author', 'Unknown')
                            
                            print(Fore.YELLOW + f"   {name} " + Fore.WHITE + f"v{version}")
                            print(Fore.WHITE + f"   👤 Author: {author}")
                            
                            if 'description' in metadata:
                                print(Fore.WHITE + f"   {metadata['description']}")
                except:
                    # If we can't parse metadata, just show filename
                    pass
                
                print()
        else:
            print(Fore.RED + f"Error fetching store apps: HTTP {response.status_code}")
    
    except ImportError:
        print(Fore.RED + "Error: 'requests' module not installed")
        print(Fore.YELLOW + "Install with: pip install requests")
    except Exception as e:
        print(Fore.RED + f"Error connecting to Mirage Store: {e}")

def mirage_store_download(filename):
    """Download an app from the Mirage Store"""
    try:
        import requests
        
        # Add .mapp extension if not present
        if not filename.endswith('.mapp'):
            filename += '.mapp'
        
        print(Fore.CYAN + f"📥 Downloading '{filename}' from Mirage Store...")
        
        response = requests.get(f"{STORE_API}/apps/{filename}", timeout=30)
        
        if response.status_code == 200:
            # Check if file already exists locally
            local_path = os.path.join(os.getcwd(), filename)
            
            if os.path.exists(local_path):
                overwrite = input(Fore.YELLOW + f"'{filename}' already exists. Overwrite? (yes/no): ").strip().lower()
                if overwrite != 'yes':
                    print(Fore.YELLOW + "Download cancelled.")
                    return
            
            # Save the file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(Fore.GREEN + f"✓ Downloaded '{filename}' successfully!")
            print(Fore.CYAN + f"  Run with: run {filename}")
        
        elif response.status_code == 404:
            print(Fore.RED + f"App '{filename}' not found in store.")
            print(Fore.YELLOW + "Use 'ms list' to see available apps.")
        else:
            print(Fore.RED + f"Error downloading: HTTP {response.status_code}")
    
    except ImportError:
        print(Fore.RED + "Error: 'requests' module not installed")
        print(Fore.YELLOW + "Install with: pip install requests")
    except Exception as e:
        print(Fore.RED + f"Error downloading from store: {e}")

def mirage_store_upload(filename, current_user):
    """Upload an app to the Mirage Store"""
    try:
        import requests
        
        # Add .mapp extension if not present
        if not filename.endswith('.mapp'):
            filename += '.mapp'
        
        # Check if file exists
        if not os.path.exists(filename):
            print(Fore.RED + f"File '{filename}' not found.")
            return
        
        # Parse the .mapp file to get metadata
        metadata, code = parse_mapp_file(filename)
        if metadata is None:
            print(Fore.RED + "Invalid .mapp file format. Cannot upload.")
            return
        
        # Update author to current user if not set or empty
        if 'author' not in metadata or not metadata['author'] or metadata['author'] == 'Your Name':
            metadata['author'] = current_user
            print(Fore.YELLOW + f"Setting author to: {current_user}")
        
        print(Fore.CYAN + f"📤 Uploading '{filename}' to Mirage Store...")
        print(Fore.YELLOW + f"   App: {metadata.get('name', 'Unknown')}")
        print(Fore.YELLOW + f"   Version: {metadata.get('version', '?')}")
        print(Fore.YELLOW + f"   Author: {metadata.get('author', 'Unknown')}")
        
        confirm = input(Fore.YELLOW + "\nProceed with upload? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print(Fore.YELLOW + "Upload cancelled.")
            return
        
        # Read file content
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            
            response = requests.post(f"{STORE_API}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            uploaded_name = result.get('filename', filename)
            
            print(Fore.GREEN + f"✓ Uploaded successfully!")
            
            if uploaded_name != filename:
                print(Fore.YELLOW + f"  Note: File was renamed to '{uploaded_name}' (name conflict)")
            
            print(Fore.CYAN + f"  Others can download with: ms download {uploaded_name}")
        else:
            print(Fore.RED + f"Error uploading: HTTP {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(Fore.RED + f"  {error_data['error']}")
            except:
                pass
    
    except ImportError:
        print(Fore.RED + "Error: 'requests' module not installed")
        print(Fore.YELLOW + "Install with: pip install requests")
    except Exception as e:
        print(Fore.RED + f"Error uploading to store: {e}")
# ---------- Main OS ----------
def mirage():
    splash_screen()
    current_user = login()
    aliases = load_aliases()

    while True:
        try:
            cmd = input(Fore.MAGENTA + f"{current_user}@Mirage:{Fore.CYAN}{os.path.basename(os.getcwd())}> " + Fore.WHITE).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + Fore.GREEN + "Exiting Mirage...")
            sys.exit()
        
        if not cmd:
            continue
        
        # Expand aliases
        cmd = expand_alias(cmd, aliases)
        
        save_to_history(cmd)
        parts = cmd.split()
        command = parts[0]

        if command == "help":
            help_menu()
        elif command == "pwd":
            print(Fore.CYAN + os.getcwd())
        elif command == "ls":
            show_all = "-a" in parts
            files = os.listdir(".")
            if not show_all:
                files = [f for f in files if not f.startswith('.')]
            for f in sorted(files):
                if os.path.isdir(f):
                    print(Fore.BLUE + f + "/")
                else:
                    print(Fore.WHITE + f)
        elif command == "cd":
            if len(parts) > 1:
                path = parts[1]
                try:
                    os.chdir(os.path.expanduser(path))
                except FileNotFoundError:
                    print(Fore.RED + "Directory not found.")
                except NotADirectoryError:
                    print(Fore.RED + "Not a directory.")
            else:
                os.chdir(os.path.join(USERS_DIR, current_user))
        elif command == "cat":
            if len(parts) > 1:
                fname = parts[1]
                try:
                    with open(fname, "r") as f:
                        print(f.read())
                except FileNotFoundError:
                    print(Fore.RED + "File not found.")
                except IsADirectoryError:
                    print(Fore.RED + "Cannot cat a directory.")
            else:
                print(Fore.RED + "Usage: cat FILE")
        elif command == "head":
            if len(parts) > 1:
                fname = parts[1]
                lines = int(parts[2]) if len(parts) > 2 else 10
                head_file(fname, lines)
            else:
                print(Fore.RED + "Usage: head FILE [N]")
        elif command == "tail":
            if len(parts) > 1:
                fname = parts[1]
                lines = int(parts[2]) if len(parts) > 2 else 10
                tail_file(fname, lines)
            else:
                print(Fore.RED + "Usage: tail FILE [N]")
        elif command == "grep":
            if len(parts) > 2:
                pattern = parts[1]
                fname = parts[2]
                grep_file(pattern, fname)
            else:
                print(Fore.RED + "Usage: grep PATTERN FILE")
        elif command == "wc":
            if len(parts) > 1:
                wc_file(parts[1])
            else:
                print(Fore.RED + "Usage: wc FILE")
        elif command == "echo":
            if len(parts) > 1:
                echo_command(parts[1:])
            else:
                print()
        elif command == "touch":
            if len(parts) > 1:
                fname = parts[1]
                open(fname, "a").close()
                print(Fore.GREEN + f"Created '{fname}'")
            else:
                print(Fore.RED + "Usage: touch FILE")
        elif command == "mkdir":
            if len(parts) > 1:
                dirname = parts[1]
                os.makedirs(dirname, exist_ok=True)
                print(Fore.GREEN + f"Created directory '{dirname}'")
            else:
                print(Fore.RED + "Usage: mkdir DIR")
        elif command == "rm":
            if len(parts) > 1:
                fname = parts[1]
                if os.path.exists(fname):
                    try:
                        if os.path.isdir(fname):
                            shutil.rmtree(fname)
                        else:
                            os.remove(fname)
                        print(Fore.GREEN + f"Deleted '{fname}'")
                    except Exception as e:
                        print(Fore.RED + f"Error: {e}")
                else:
                    print(Fore.RED + "File not found.")
            else:
                print(Fore.RED + "Usage: rm FILE")
        elif command == "cp":
            if len(parts) > 2:
                src, dst = parts[1], parts[2]
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    print(Fore.GREEN + f"Copied '{src}' to '{dst}'")
                except Exception as e:
                    print(Fore.RED + f"Error: {e}")
            else:
                print(Fore.RED + "Usage: cp SRC DST")
        elif command == "mv":
            if len(parts) > 2:
                src, dst = parts[1], parts[2]
                try:
                    shutil.move(src, dst)
                    print(Fore.GREEN + f"Moved '{src}' to '{dst}'")
                except Exception as e:
                    print(Fore.RED + f"Error: {e}")
            else:
                print(Fore.RED + "Usage: mv SRC DST")
        elif command == "rename":
            if len(parts) > 2:
                rename_file(parts[1], parts[2])
            else:
                print(Fore.RED + "Usage: rename OLD NEW")
        elif command == "ln":
            if len(parts) > 2:
                create_link(parts[1], parts[2])
            else:
                print(Fore.RED + "Usage: ln SOURCE LINK")
        elif command == "find":
            if len(parts) > 1:
                find_files(parts[1])
            else:
                print(Fore.RED + "Usage: find TERM")
        elif command == "tree":
            print(Fore.BLUE + ".\n")
            show_tree()
        elif command == "count":
            count_files()
        elif command == "du":
            disk_usage()
        elif command == "info":
            if len(parts) > 1:
                show_file_info(parts[1])
            else:
                print(Fore.RED + "Usage: info FILE")
        elif command == "pull":
            if len(parts) > 1:
                pull_file(" ".join(parts[1:]))
            else:
                print(Fore.RED + "Usage: pull PATH")
        elif command == "run":
            if len(parts) > 1:
                run_file(parts[1])
            else:
                print(Fore.RED + "Usage: run FILE")
        elif command == "mapp":
            if len(parts) > 1:
                if parts[1] == "list":
                    list_mapps()
                elif parts[1] == "new":
                    if len(parts) > 2:
                        filename = parts[2]
                        if not filename.endswith('.mapp'):
                            filename += '.mapp'
                        create_mapp_template(filename)
                    else:
                        print(Fore.RED + "Usage: mapp new FILENAME")
                else:
                    print(Fore.RED + "Unknown mapp command. Use: list, new")
            else:
                print(Fore.YELLOW + "mapp commands: list, new")
                print(Fore.CYAN + "  mapp list      - List all .mapp files")
                print(Fore.CYAN + "  mapp new FILE  - Create new .mapp template")
        elif command == "edit":
            if len(parts) > 1:
                run_editor(parts[1])
            else:
                print(Fore.RED + "Usage: edit FILE")
        elif command == "history":
            if len(parts) > 1 and parts[1] == "clear":
                clear_history()
            else:
                show_history()
        elif command == "sysinfo":
            show_sysinfo()
        elif command == "uptime":
            uptime_info()
        elif command == "whoami":
            whoami(current_user)
        elif command == "fortune":
            show_fortune()
        elif command == "alias":
            manage_aliases(parts[1:])
            # Reload aliases after modification
            aliases = load_aliases()
        elif command == "clear":
            clear()
        elif command == "calc":
            run_calculator()
        elif command == "notes":
            run_notes()
        elif command == "todo":
            run_todo()
        elif command == "apps":
            list_apps()
        elif command == "switch":
            # Clean up guest directory if switching from guest
            if current_user == GUEST_USER:
                cleanup_guest()
            current_user = switch_user()
            aliases = load_aliases()
            current_user = switch_user()
            aliases = load_aliases()
                    
        elif command == "logout":
            print(Fore.CYAN + f"Logging out '{current_user}'...")
            # Clean up guest directory if logging out as guest
            if current_user == GUEST_USER:
                cleanup_guest()
            current_user = login()
            aliases = load_aliases()
        elif command == "dusr":
            delete_user(current_user)
        elif command == "exit":
            print(Fore.GREEN + "Exiting Mirage...")
            sys.exit()
        elif command == "ms":
            if len(parts) > 1:
                subcmd = parts[1]

                if subcmd == "list":
                    mirage_store_list()

                elif subcmd == "download":
                    if len(parts) > 2:
                        mirage_store_download(parts[2])
                    else:
                        print(Fore.RED + "Usage: ms download FILENAME")

                elif subcmd == "upload":
                    if len(parts) > 2:
                        mirage_store_upload(parts[2], current_user)
                    else:
                        print(Fore.RED + "Usage: ms upload FILENAME")

                elif subcmd == "ping":
                    print(Fore.YELLOW + "Pinging Mirage Store server...")
                    try:
                        response = requests.post(STORE_API_PING, json={"client": "MirageCLI"})
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                print(Fore.GREEN + "✓ Mirage Store is online!")
                                print(Fore.CYAN + f"  Server:     {data.get('server', 'Unknown')}")
                                print(Fore.CYAN + f"  Status:     {data.get('status', 'Unknown')}")
                                print(Fore.CYAN + f"  B2 Status:  {data.get('b2_status', 'Unknown')}")
                                print(Fore.CYAN + f"  Latency:    {data.get('latency_ms', 'N/A')} ms")
                                print(Fore.CYAN + f"  Uptime:     {data.get('uptime', 'N/A')}")
                                print(Fore.CYAN + f"  Timestamp:  {data.get('timestamp', 'N/A')}")
                            except ValueError:
                                print(Fore.RED + "✗ Invalid JSON response from server.")
                                print(Fore.RED + f"Raw output: {response.text}")
                        else:
                            print(Fore.RED + f"✗ Server responded with status {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(Fore.RED + f"✗ Could not reach Mirage Store: {e}")

                        print(Fore.YELLOW + "Pinging Mirage Store server...")
                        try:
                                response = requests.post(STORE_API_PING, json={"client": "MirageCLI"})
                                if response.status_code == 200:
                                    print(Fore.GREEN + f"✓ Mirage Store is online! ({response.text})")
                                else:
                                    print(Fore.RED + f"✗ Server responded with status {response.status_code}: {response.text}")
                        except requests.exceptions.RequestException as e:
                                    print(Fore.RED + f"✗ Could not reach Mirage Store: {e}")

                elif subcmd == "help":
                    print(Fore.YELLOW + "Mirage Store commands:")
                    print(Fore.CYAN + "  ms list           - List apps in store")
                    print(Fore.CYAN + "  ms download FILE  - Download app from store")
                    print(Fore.CYAN + "  ms upload FILE    - Upload app to store")
                    print(Fore.CYAN + "  ms ping           - Check server connectivity")

            else:
                print(Fore.RED + "Unknown ms command. Use: list, download, upload, ping, help")

        else:
            print(Fore.YELLOW + "Mirage Store commands:")
            print(Fore.CYAN + "  ms list           - List apps in store")
            print(Fore.CYAN + "  ms download FILE  - Download app from store")
            print(Fore.CYAN + "  ms upload FILE    - Upload app to store")
            print(Fore.CYAN + "  ms ping           - Check server connectivity")
    else:
        print(Fore.RED + f"Unknown command: {command}")
        print(Fore.YELLOW + "Type 'help' for available commands")

if __name__ == "__main__":
    mirage()