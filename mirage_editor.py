import curses
import sys
import os

def main(stdscr, filename="untitled.txt"):
    curses.curs_set(0)
    stdscr.timeout(100)
    
    # Initialize colors with better scheme
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Header
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Line numbers
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Cursor
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)       # Error
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Success
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Accent

    # Load file
    if os.path.exists(filename):
        with open(filename, "r") as f:
            text = [line.rstrip("\n") for line in f.readlines()]
    else:
        text = []

    if not text:
        text = [""]

    cursor_y, cursor_x = 0, 0
    scroll = 0
    modified = False
    message = ""
    msg_timer = 0
    wrap_enabled = True
    show_line_nums = True

    def wrap_line(line, width):
        """Wrap a line into multiple display lines"""
        if not wrap_enabled or len(line) <= width:
            return [line]
        
        wrapped = []
        pos = 0
        while pos < len(line):
            wrapped.append(line[pos:pos + width])
            pos += width
        return wrapped if wrapped else [""]

    def get_display_lines():
        """Convert text to display lines with wrapping and line number info"""
        display = []
        height, width = stdscr.getmaxyx()
        line_width = width - (5 if show_line_nums else 1)
        
        for line_num, line in enumerate(text):
            wrapped = wrap_line(line, line_width)
            for wrap_idx, segment in enumerate(wrapped):
                display.append({
                    'text': segment,
                    'logical_line': line_num,
                    'wrap_index': wrap_idx,
                    'is_first': wrap_idx == 0
                })
        return display

    def cursor_to_display_pos():
        """Convert logical cursor position to display position"""
        height, width = stdscr.getmaxyx()
        line_width = width - (5 if show_line_nums else 1)
        
        display_y = 0
        for i in range(cursor_y):
            wrapped = wrap_line(text[i], line_width)
            display_y += len(wrapped)
        
        # Add offset within current line
        if wrap_enabled:
            display_y += cursor_x // line_width
            display_x = cursor_x % line_width
        else:
            display_x = min(cursor_x, line_width - 1)
        
        return display_y, display_x

    def show_message(msg, duration=20, msg_type='info'):
        nonlocal message, msg_timer
        message = (msg, msg_type)
        msg_timer = duration

    def redraw():
        nonlocal msg_timer, message
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        
        if height < 3 or width < 10:
            return
        
        # Header
        mod_str = " [+]" if modified else ""
        wrap_str = " [W]" if wrap_enabled else ""
        header = f" ✨ Mirage - {filename}{mod_str}{wrap_str}"
        # Ensure header fits within width
        if len(header) > width:
            header = header[:width-3] + "..."
        header = header.ljust(width)
        
        try:
            if curses.has_colors():
                stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)
            else:
                stdscr.addstr(0, 0, header, curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        # Get display lines
        display_lines = get_display_lines()
        visible_height = height - 2
        
        # Display text
        for i in range(visible_height):
            display_idx = scroll + i
            if display_idx >= len(display_lines):
                break
            
            line_info = display_lines[display_idx]
            y_pos = i + 1
            
            try:
                # Line numbers
                if show_line_nums:
                    if line_info['is_first']:
                        line_num = f"{line_info['logical_line'] + 1:3d} "
                        if curses.has_colors():
                            stdscr.addstr(y_pos, 0, line_num, curses.color_pair(2) | curses.A_BOLD)
                        else:
                            stdscr.addstr(y_pos, 0, line_num)
                    else:
                        if curses.has_colors():
                            stdscr.addstr(y_pos, 0, "  · ", curses.color_pair(2) | curses.A_DIM)
                        else:
                            stdscr.addstr(y_pos, 0, "  > ")
                    
                    # Text content
                    text_start = 4
                    max_text_width = width - 5
                else:
                    text_start = 0
                    max_text_width = width - 1
                
                display_text = line_info['text'][:max_text_width]
                stdscr.addstr(y_pos, text_start, display_text)
                
            except curses.error:
                pass

        # Footer with status message or help
        if message and msg_timer > 0:
            msg_text, msg_type = message
            footer = f" {msg_text}"
            msg_timer -= 1
            
            if curses.has_colors():
                if msg_type == 'success':
                    color = curses.color_pair(5) | curses.A_BOLD
                elif msg_type == 'error':
                    color = curses.color_pair(4) | curses.A_BOLD
                else:
                    color = curses.color_pair(1)
            else:
                color = curses.A_REVERSE
        else:
            footer = " ^S Save | ^Q Quit | ^W Wrap | ^L Lines | ^H Help"
            message = ""
            color = curses.color_pair(1) if curses.has_colors() else curses.A_REVERSE
        
        # Ensure footer fits within width
        if len(footer) > width:
            footer = footer[:width-3] + "..."
        footer = footer.ljust(width)
        
        try:
            stdscr.addstr(height - 1, 0, footer, color)
        except curses.error:
            pass

        # Draw cursor
        display_y, display_x = cursor_to_display_pos()
        cursor_screen_y = display_y - scroll + 1
        
        if 1 <= cursor_screen_y < height - 1:
            cursor_x_pos = display_x + (4 if show_line_nums else 0)
            cursor_x_pos = min(cursor_x_pos, width - 1)
            
            try:
                if curses.has_colors():
                    stdscr.addstr(cursor_screen_y, cursor_x_pos, "│", 
                                curses.color_pair(3) | curses.A_BOLD)
                else:
                    stdscr.addstr(cursor_screen_y, cursor_x_pos, "|", 
                                curses.A_BOLD | curses.A_BLINK)
            except curses.error:
                pass

        try:
            stdscr.refresh()
        except curses.error:
            pass

    def show_help():
        """Display help overlay"""
        help_lines = [
            "┌────────────────────────────────────────────┐",
            "│       MIRAGE EDITOR - HELP GUIDE          │",
            "├────────────────────────────────────────────┤",
            "│ Navigation:                                │",
            "│   ↑↓←→        Move cursor                  │",
            "│   Home/End    Start/End of line            │",
            "│   Ctrl+A/E    Alternative Home/End         │",
            "│                                            │",
            "│ Editing:                                   │",
            "│   Enter       New line                     │",
            "│   Backspace   Delete before cursor         │",
            "│   Delete      Delete at cursor (Ctrl+D)    │",
            "│                                            │",
            "│ Commands:                                  │",
            "│   Ctrl+S      Save file                    │",
            "│   Ctrl+Q      Quit (warns if unsaved)      │",
            "│   Ctrl+W      Toggle line wrapping         │",
            "│   Ctrl+L      Toggle line numbers          │",
            "│   Ctrl+H      Show this help               │",
            "│                                            │",
            "│      Press any key to continue...          │",
            "└────────────────────────────────────────────┘"
        ]
        
        height, width = stdscr.getmaxyx()
        start_y = max(0, (height - len(help_lines)) // 2)
        start_x = max(0, (width - 46) // 2)
        
        # Create help window
        for i, line in enumerate(help_lines):
            try:
                line_to_show = line[:min(len(line), width - start_x)]
                if curses.has_colors():
                    stdscr.addstr(start_y + i, start_x, line_to_show, curses.color_pair(6) | curses.A_BOLD)
                else:
                    stdscr.addstr(start_y + i, start_x, line_to_show, curses.A_BOLD)
            except curses.error:
                pass
        
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        stdscr.nodelay(True)

    # Main loop
    while True:
        height, width = stdscr.getmaxyx()

        if not text:
            text = [""]

        # Clamp cursor
        cursor_y = max(0, min(cursor_y, len(text) - 1))
        cursor_x = max(0, min(cursor_x, len(text[cursor_y])))

        # Manage scrolling
        display_y, _ = cursor_to_display_pos()
        visible_height = max(1, height - 2)
        
        if display_y < scroll:
            scroll = display_y
        elif display_y >= scroll + visible_height:
            scroll = display_y - visible_height + 1

        redraw()
        
        try:
            key = stdscr.get_wch()
        except:
            continue

        # Handle keyboard input
        if key == "\x11":  # Ctrl+Q
            if modified:
                show_message("Unsaved changes! Press Ctrl+Q again to quit", 30, 'error')
                try:
                    stdscr.timeout(3000)
                    confirm = stdscr.get_wch()
                    stdscr.timeout(100)
                    if confirm == "\x11":
                        break
                except:
                    stdscr.timeout(100)
            else:
                break
                
        elif key == "\x13":  # Ctrl+S
            try:
                with open(filename, "w") as f:
                    for line in text:
                        f.write(line + "\n")
                modified = False
                show_message(f"Saved to {filename}", 20, 'success')
            except Exception as e:
                show_message(f"Save failed: {str(e)}", 30, 'error')
                
        elif key == "\x17":  # Ctrl+W
            wrap_enabled = not wrap_enabled
            show_message(f"Line wrap: {'ON' if wrap_enabled else 'OFF'}", 15)
            
        elif key == "\x0c":  # Ctrl+L
            show_line_nums = not show_line_nums
            show_message(f"Line numbers: {'ON' if show_line_nums else 'OFF'}", 15)
            
        elif key == curses.KEY_F1:  # Ctrl+H
            show_help()

            
        elif key == curses.KEY_UP:
            if cursor_y > 0:
                cursor_y -= 1
                cursor_x = min(cursor_x, len(text[cursor_y]))
                
        elif key == curses.KEY_DOWN:
            if cursor_y < len(text) - 1:
                cursor_y += 1
                cursor_x = min(cursor_x, len(text[cursor_y]))
                
        elif key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(text[cursor_y])
                
        elif key == curses.KEY_RIGHT:
            if cursor_x < len(text[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(text) - 1:
                cursor_y += 1
                cursor_x = 0
                
        elif key == curses.KEY_HOME or key == "\x01":  # Ctrl+A
            cursor_x = 0
            
        elif key == curses.KEY_END or key == "\x05":  # Ctrl+E
            cursor_x = len(text[cursor_y])
            
        elif key == "\n":  # Enter
            new_line = text[cursor_y][cursor_x:]
            text[cursor_y] = text[cursor_y][:cursor_x]
            text.insert(cursor_y + 1, new_line)
            cursor_y += 1
            cursor_x = 0
            modified = True
            
        elif key == curses.KEY_BACKSPACE or key == "\x7f" or key == "\x08":
            if cursor_x > 0:
                text[cursor_y] = text[cursor_y][:cursor_x - 1] + text[cursor_y][cursor_x:]
                cursor_x -= 1
                modified = True
            elif cursor_y > 0:
                prev_len = len(text[cursor_y - 1])
                text[cursor_y - 1] += text[cursor_y]
                text.pop(cursor_y)
                cursor_y -= 1
                cursor_x = prev_len
                modified = True
                if not text:
                    text = [""]
                    cursor_y = 0
                    cursor_x = 0
                    
        elif key == curses.KEY_DC or key == "\x04":  # Delete / Ctrl+D
            if cursor_x < len(text[cursor_y]):
                text[cursor_y] = text[cursor_y][:cursor_x] + text[cursor_y][cursor_x + 1:]
                modified = True
            elif cursor_y < len(text) - 1:
                text[cursor_y] += text[cursor_y + 1]
                text.pop(cursor_y + 1)
                modified = True
                
        elif isinstance(key, str) and key.isprintable():
            text[cursor_y] = text[cursor_y][:cursor_x] + key + text[cursor_y][cursor_x:]
            cursor_x += 1
            modified = True

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "untitled.txt"
    curses.wrapper(main, filename)
