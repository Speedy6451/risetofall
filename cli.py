import sys, os, src.main


if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    game = src.main.RiseToFall()
    game.run();

