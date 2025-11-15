# Welcome To MirageOS!
A Python Based CLI
---

As it said in the text this is a CLI

# How To Install?
Installing MirageOS is quite simple. just follow these steps!

## The Normal Way
    1. Download the entire repo.
    2. Run mirage.py straight from the explorer.

## The ***C00L*** Way.
    1. Download mirage.cmd
    2. Dismiss windows yapping about a signature
    3. Run mirage.cmd and follow the processes

# Commands
```
════════════════════════════════════════════════════════════
  help             - Show this menu
  ls [-a]          - List files (-a shows hidden)
  pwd              - Show current directory
  cd DIR           - Change directory

  === .mapp Applications ===
  mapp list        - List all .mapp files
  mapp new FILE    - Create new .mapp template
  mapp package DIR - Packages a .mapp folder to a .mapp file
  run FILE.mapp    - Run a .mapp application

  === Mirage Store ===
  ms list          - List apps in the store
  ms download FILE - Download app from store
  ms upload FILE   - Upload app to store
  ms ping          - Ping the MirageStore Server

  === File Operations ===
  cat FILE         - Show file contents
  head FILE [N]    - Show first N lines (default 10)
  tail FILE [N]    - Show last N lines (default 10)
  grep PAT FILE    - Search for pattern in file
  wc FILE          - Count lines, words, chars
  touch FILE       - Create empty file
  mkdir DIR        - Create directory
  rm FILE          - Delete file/directory
  cp SRC DST       - Copy file
  mv SRC DST       - Move file
  rename OLD NEW   - Rename file/directory
  ln SRC LINK      - Create symbolic link
  find TERM        - Search for files
  tree             - Show directory tree
  count            - Count files and directories
  du               - Show disk usage
  info FILE        - Show file information
  pull PATH        - Download file to current directory
  run FILE         - Run/open file with default app
  echo TEXT        - Echo text to console
  calc             - Open calculator
  notes            - Open notes
  todo             - Manage todo list
  apps             - List mini apps
  edit FILE        - Open file in editor
  history          - Show command history
  history clear    - Clear command history
  sysinfo          - Show system information
  uptime           - Show session uptime
  whoami           - Show current user info
  fortune          - Display a random quote
  alias            - Manage command aliases
  switch           - Switch user
  dusr             - Delete a user account
  logout           - Logout and return to login
  clear            - Clear screen
  exit             - Exit Mirage
════════════════════════════════════════════════════════════
```

# not so Frequently Asked Questions!
    - What is a .mapp?
        a .mapp (Mirage Application) is basically well. a Mirage Application. its just JSON and Python combined so its easy. trust me.
    - Why?
        why not?
    - What inspired you to make Mirage?
        toying around with Termux. And also its something ive had in mind for a while :P
