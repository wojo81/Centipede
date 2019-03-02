from tkinter import *

def main():
    master= Tk()

    screen_width= master.winfo_screenwidth()
    screen_height= master.winfo_screenheight()

    canvas= Canvas(master, width= screen_width, height= screen_height)
    canvas.pack()

    mainloop()

if __name__ == "__main__":
    main()