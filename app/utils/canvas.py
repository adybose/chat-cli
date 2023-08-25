import curses
import os
import subprocess


def get_valid_shell_commands():
    # TODO: fix this to work with an input command or script
    try:
        # Get the list of valid shell commands
        result = subprocess.run(['compgen', '-c'], capture_output=True, text=True)
        if result.returncode == 0:
            return set(result.stdout.strip().split('\n'))
        else:
            return set()
    except FileNotFoundError:
        return set()


def get_header_text():
    """
      Get the header text for the interactive shell session
    """
    user = os.popen('whoami').read().strip()
    hostname = os.popen('scutil --get LocalHostName').read().strip()
    cwd = os.getcwd()
    directory_name = os.path.basename(cwd)
    virtualenv = os.environ.get('VIRTUAL_ENV', '')
    header = f" {user}@{hostname} {directory_name} ❯_ "
    if virtualenv:
        header = f" ({os.path.basename(virtualenv)}){header}"
    return header


def render_shell_canvas(stdscr):
    curses.curs_set(2)  # Show the cursor
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # Enable mouse events

    header_text = get_header_text()
    footer_text = " chat-cli v0.1 | Using Model: gpt-3.5-turbo | Press Esc for Options & Ctrl+C to Exit "
    input_prompt = " ❯ "

    # Setup Colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    
    valid_shell_commands = get_valid_shell_commands()

    while True:
        height, width = stdscr.getmaxyx()

        # Check for window size
        if height < 5 or width < len(header_text) + 2:
            stdscr.clear()
            stdscr.addstr(0, 0, "Window too small!")
            stdscr.addstr(1, 0, "Resize to continue...")
            stdscr.refresh()
            continue

        stdscr.clear()
        stdscr.border()
        stdscr.addstr(0, 2, header_text, curses.color_pair(2))
        stdscr.addstr(height - 1, 1, footer_text)

        main_area_height = height - 4
        input_area_start = 2
        input_area_end = height - 2

        printed_lines = []
        current_input = ""
        cursor_x = len(current_input)  # Cursor always starts after the input prompt

        while True:
            stdscr.addstr(input_area_start + len(printed_lines), 1, input_prompt, curses.color_pair(1))
            stdscr.addstr(input_area_start + len(printed_lines), len(input_prompt) + 1, current_input)

            stdscr.move(input_area_start + len(printed_lines), len(input_prompt) + 1 + cursor_x)
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_MOUSE:
                _, mouse_x, mouse_y, _, _ = curses.getmouse()
                if input_area_start <= mouse_y < input_area_end:
                    cursor_x = max(0, min(len(current_input), mouse_x - len(input_prompt) - 1))

            elif key == 10:  # Enter key
                if current_input.strip() == 'exit':
                    return

                printed_lines.append(current_input)
                user_command = current_input.strip()

                # # Clear the current input and reset cursor position
                # current_input = ""
                # cursor_x = len(current_input)

                # Execute the user command
                if user_command in valid_shell_commands:  # TODO: check logic
                    # stdscr.addstr(input_area_start + len(printed_lines), 1, "[clio] Processing...")
                    # stdscr.refresh()  # TODO: check and remove if redundant code
                    oputput_line1 = "[clio]: Processing... Valid command."
                    printed_lines.append(oputput_line1)
                    stdscr.addstr(input_area_start + len(printed_lines), 1, oputput_line1)
                    
                    result = subprocess.run(user_command, shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    printed_lines.append(output_lines[0])
                    stdscr.addstr(input_area_start + len(printed_lines) + 1, 1, "Command: " + output_lines[0])

                    # Print the remaining output lines (if any)
                    for line in output_lines[1:]:
                        printed_lines.append(line)
                        stdscr.addstr(input_area_start + len(printed_lines), 1, line)

                else:
                    oputput_line1 = "[clio]: Processing... Echoing input. TODO: add OpenAI response"
                    printed_lines.append(oputput_line1)
                    stdscr.addstr(input_area_start + len(printed_lines), 1, oputput_line1)
                    output_line2 = "Response: " + current_input
                    printed_lines.append(output_line2)
                    stdscr.addstr(input_area_start + len(printed_lines), 1, "Response: " + current_input)

                printed_lines.append("")
                printed_lines.append("❯ " + current_input)
                stdscr.addstr(input_area_start + len(printed_lines), 1, input_prompt, curses.color_pair(1))
                stdscr.move(input_area_start + len(printed_lines), len(input_prompt) + 1)
                # Clear the current input and reset cursor position
                current_input = ""
                cursor_x = len(current_input)

            elif key == curses.KEY_BACKSPACE or key == 127:
                if cursor_x > 0:
                    current_input = current_input[:cursor_x - 1] + current_input[cursor_x:]
                    cursor_x -= 1

            elif key == curses.KEY_LEFT:
                cursor_x = max(0, cursor_x - 1)

            elif key == curses.KEY_RIGHT:
                cursor_x = min(len(current_input), cursor_x + 1)

            elif key >= 32 and key <= 126:  # Printable characters
                current_input = current_input[:cursor_x] + chr(key) + current_input[cursor_x:]
                cursor_x += 1

            # Handle window resize
            new_height, new_width = stdscr.getmaxyx()
            if height != new_height or width != new_width:  # TODO: reprint screen
                break

        # Clear the screen if window size changed
        # TODO: reprint screen
        stdscr.clear()
        stdscr.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(render_shell_canvas)
    except curses.error:
        pass  # Ignore error when program exits on small window size
    # signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow Ctrl+C to interrupt the program

    # try:
    #     curses.wrapper(main)
    # except KeyboardInterrupt:
    #     pass