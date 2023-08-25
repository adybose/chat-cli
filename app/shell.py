# builtin modules
import sys

# installed packages
import curses

# local modules
from utils.canvas import render_shell_canvas


def main(stdscr):
    """
    main driver function
    """
    # Disable cursor
    curses.curs_set(0)
    curses.mousemask(1)
    stdscr.clear()
    stdscr.refresh()

    # Setup Colors
    # curses.start_color()
    # curses.use_default_colors()

    # Launch Loading Screen
    # render_loading_canvas(stdscr)
    # app_ready = render_loading_canvas(stdscr)
    # app_ready = True
    # if app_ready:
        # render_main_canvas(stdscr)
    render_shell_canvas(stdscr)
    

if __name__ == "__main__":
    curses.wrapper(main)
