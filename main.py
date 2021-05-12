# Main MedNet
# coding: utf-8

# T-Mednet GUI improvement
# Version: 0.5.dev1
# Author: Marc Jou
# Date: 28/04/2021

__version__ = "0.5"
__author__ = "Marc Jou"
__date__ = "April 2018"

import file_manipulation as fm
import user_interaction as ui


def main():
    root = ui.Tk()
    # root.minsize(1000,500)
    root.title("TMEDNET tool")
    app = ui.tmednet(root)
    root.protocol("WM_DELETE_WINDOW", lambda: ui.close(root))
    root.mainloop()


if __name__ == '__main__':
    main()
