import time
from infi.systray import SysTrayIcon
import tkinter as tk
import os
import sys
import win32api
import win32con
import win32gui_struct
from tkinter import messagebox
from screeninfo import get_monitors
from ctypes import windll
import pkg_resources
import json
import requests
from datetime import datetime
import pygetwindow as gw
import threading



global delocked
delocked = False

github_url = 'https://raw.githubusercontent.com/MiGuide3025/nortonsafety/main/properties.json'

h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)

timerequestboturl = "https://discord.com/api/webhooks/1187017024950509589/ZtDEE0ss_MdpIQnnQuDvsAMEu7WGuoEW_h3baR_K6gShfK_iynfMB3yq-76ZjAsexnIW"

global locked

locked = True

def turn_off_secondary_displays():
    # Get all open windows
    windows = gw.getAllTitles()

    # Get the title of the active window
    active_window_title = gw.getActiveWindow().title

    # Filter out windows that are not on the main display
    secondary_windows = [title for title in windows if title != active_window_title]

    # Minimize or close secondary windows
    for title in secondary_windows:
        try:
            window = gw.getWindowsWithTitle(title)[0]
            window.minimize()
        except Exception as e:
            print(f"Error minimizing window '{title}': {e}")


def ist_(json_data, what):
    try:
        data = json.loads(json_data)

        schlafenszeit = data.get("schlafenszeit")
        sperren = data.get("sperren")

        passwort = data.get("passwort")
        whatvar = data.get(what)


        startraw, endraw = map(str, schlafenszeit.split("-"))

        starthour, startminute = map(int, startraw.split(":"))

        endhour, endminute = map(int, endraw.split(":"))

        start = int(startminute)+int(starthour)*60

        end = int(endminute)+int(endhour)*60


        # Aktuelle Uhrzeit abrufen
        current_hour = int(datetime.now().minute)+int(datetime.now().hour)*60

        if what == "schlafenszeit":
            if start <= current_hour:
                return True
            if current_hour <= end:
                return True
            else:
                return False


        elif what == "gesperrt":
            if sperren == "false":
                return False
            else:
                return True


        elif what == "passwort":
            return passwort

        else:
            return whatvar


    except json.JSONDecodeError:

        print("Fehler beim Dekodieren der JSON-Daten")

        return False



def jsonabfrage(what, truefalse):

    # JSON-Daten von der URL abrufen
    response = requests.get(github_url)

    if response.status_code == 200:
        json_data = response.text

        if truefalse == "off":
            return ist_(json_data, what)

        else:

            if ist_(json_data, what):
                return True
            else:
                return False

    else:
        print(f"Fehler beim Abrufen der Daten. Statuscode: {response.status_code}")
        return True


class TimeRemainingWindow(tk.Toplevel):
    def __init__(self, remaining_time, close_callback):
        super().__init__()
        self.title("Zeit verbleibend")
        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)
        self.configure(bg="black")

        frame = tk.Frame(self, bg="black")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        label = tk.Label(frame, text=f"Verbleibende Zeit: {remaining_time} Stunden", bg="black", fg="white", font=("Helvetica", 16))
        label.pack()

        close_button = tk.Button(frame, text="Schließen", command=close_callback, bg="red", fg="white")
        close_button.pack(pady=20)


def create_time_remaining_window(remaining_time):
    def close_window():
        time_remaining_window.destroy()

    time_remaining_window = TimeRemainingWindow(remaining_time, close_window)
    time_remaining_window.mainloop()

class AlwaysOnTopWindow(tk.Tk):
    def __init__(self, monitor_index, open_callback):
        super().__init__()
        self.attributes("-alpha", 0.5)
        # Set window properties
        self.title("Always On Top Window")
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-fullscreen", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Override window close event


        # Bind events for minimize and maximize
        self.bind("<Unmap>", self.on_minimize)
        self.bind("<Map>", self.on_maximize)

        # Set the background color to white
        self.configure(bg="black")

        # Create a frame to contain the widgets
        frame = tk.Frame(self, bg="black")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        if monitor_index == 0:  # Main screen
            # Create and place widgets for password input
            self.label = tk.Label(frame, text="Eltern Passwort eingeben:", bg="black", fg="white")
            self.label.grid(row=0, column=0, sticky="n")

            self.password_entry = tk.Entry(frame, show="*")
            self.password_entry.grid(row=1, column=0, sticky="n")

            self.submit_button = tk.Button(frame, text="Submit", command=self.check_password, bg="green", fg="white")
            self.submit_button.grid(row=2, column=0, sticky="n", pady=5)

            self.submit_buttonza = tk.Button(frame, text="Zeit anfragen", command=lambda: zeitanfrage("lol"), bg="white", fg="black")
            self.submit_buttonza.grid(row=3, column=0, sticky="n", pady=5)

            self.submit_button2 = tk.Button(frame, text="Abmelden", command=lambda: os.system("shutdown –l"), bg="yellow", fg="black")
            self.submit_button2.grid(row=4, column=0, sticky="s", pady=20)

            self.submit_button3 = tk.Button(frame, text="Herunterfahren", command=lambda: os.system("shutdown –s"), bg="red", fg="white")
            self.submit_button3.grid(row=5, column=0, sticky="s", pady=5)

        # Callback function to open the window
        open_callback(self)

    def check_password(self):
        password = self.password_entry.get()
        if password == jsonabfrage("passwort", "off"):
            windll.user32.ShowWindow(h, 9)
            messagebox.showinfo("Hat geklappt", "Password richtig.")
            windll.user32.ShowWindow(h, 9)
            self.destroy()  # Close the window
            windll.user32.ShowWindow(h, 9)

            global delocked, delocked_time
            delocked_time = float(datetime.now().hour) * 60 * 60 + float(datetime.now().minute) * 60 + datetime.now().second
            delocked = True

        else:
            messagebox.showerror("Fehler", "HAHA Falsch")

    def on_close(self):
        # Override window close event
        messagebox.showwarning("Warnung", "So leicht geht das nicht...")

    def on_minimize(self, event):
        # Handle window minimize event
        self.iconify()  # Minimize the window

    def on_maximize(self, event):
        # Handle window maximize event
        self.deiconify()  # Restore the window

def create_windows():
    # Get information about connected monitors
    monitors = get_monitors()

    print(monitors)

    # Function to open the window for each monitor
    def open_window(window):
        print(window)
        window.mainloop()

    # Create windows for each monitor
    for i, monitor in enumerate(monitors):
        if i == 0:
            window = AlwaysOnTopWindow(i, open_window)
            try:
                screen_width, screen_height = monitor.width, monitor.height
                window.geometry(f"{screen_width}x{screen_height}+{monitor.x}+{monitor.y}")
            except:
                print("error")



def maincheck():
    global delocked_time, delocked, firsttime
    delocked = False
    firsttime = True
    locked2 = True
    while True:

        if not locked2:
            time.sleep(30)
        try:
            if not delocked:
                if jsonabfrage("schlafenszeit", "on") == True:
                    locked2 = True
                    windll.user32.ShowWindow(h, 0)
                    create_windows()
                    create_windows()
                    remaining_time = jsonabfrage("timeunlocked", "off")
                    create_time_remaining_window(remaining_time)
                    #turn_off_secondary_displays()

                if jsonabfrage("gesperrt", "on") == True:
                    locked2 = True
                    windll.user32.ShowWindow(h, 0)
                    create_windows()

                    schlafenszeit = str(jsonabfrage("schlafenszeit", "off"))
                    startraw, endraw = map(str, schlafenszeit.split("-"))
                    starthour, startminute = map(int, startraw.split(":"))
                    endhour, endminute = map(int, endraw.split(":"))
                    start = int(startminute) + int(starthour) * 60
                    end = int(endminute) + int(endhour) * 60



                    if jsonabfrage("schlafenszeit", "off"):
                        create_windows()
                        remaining_time = jsonabfrage("timeunlocked", "off")
                        create_time_remaining_window(remaining_time)


                    #turn_off_secondary_displays()




            if jsonabfrage("gesperrt", "on") == False:
                if jsonabfrage("schlafenszeit", "on") == False:
                    locked2 = False

            timenow = float(datetime.now().hour) * 60 * 60 + float(datetime.now().minute) * 60 + datetime.now().second

            if delocked and timenow - float(delocked_time) >= float(jsonabfrage("timeunlocked", "off")):
                delocked = False

            firsttime = False

        except:
            if not delocked:
                locked2 = True
                windll.user32.ShowWindow(h, 0)
                create_windows()
                #turn_off_secondary_displays()




def zeitanfrage(sysTrayIcon):
    def checkinput(zahl, frage):

        try:
            # Wenn die Antwort keine Zahl ist, eine Warnung anzeigen
            if zahl is None or float(zahl) >= 12:
                messagebox.showwarning(
                    "Warnung",
                    "Die Eingabe muss eine Zahl unter 12 sein.",
                )

            # Wenn die Antwort außerhalb des gültigen Bereichs liegt, eine Warnung anzeigen
            if float(zahl) < 0 or float(zahl) >= 24:
                messagebox.showwarning(
                    "Warnung",
                    "Die Eingabe muss eine Zahl zwischen 0 und 23 sein.",
                )

            if float(zahl) > 0 and float(zahl) < 24:
                if zahl is not None and float(zahl) < 12:
                    hostname = os.popen('hostname').read().replace('\n', '')

                    # Die Antwort zurückgeben
                    payload = payload = {'content': f"{datetime.now().hour}:{datetime.now().minute}: {hostname} möchte noch {zahl} Stunden haben!"}
                    response = requests.post(timerequestboturl, json=payload)
                    fenster.destroy()

        except:
            messagebox.showwarning(
                "Warnung",
                "Es gab einen Fehler!",
            )




    frage = "Wie viele Stunden möchtest du anfragen?"

    # Das Fenster erstellen
    fenster = tk.Tk()
    fenster.wm_attributes("-topmost", True)
    fenster.resizable(False, False)

    # Die Frage anzeigen
    label = tk.Label(fenster, text=frage)
    label.pack()

    # Die Antwort abfragen
    eingabe = tk.Entry(fenster)
    eingabe.pack()

    submit = tk.Button(fenster, text="bestätigen", command=lambda: checkinput(eingabe.get(), frage))
    submit.pack()

    # Den Dialog anzeigen
    fenster.mainloop()


def say_hello(sysTrayIcon):
    print("Hello, World!")

menu_options = (("Zeit anfragen", None, zeitanfrage),)

systray = SysTrayIcon(r"C:\Users\PC\OneDrive\Dokumente\Rainmeter\Skins\Droptop\Other\WindowMenu\icon1.ico", "Microsoft Security", menu_options)

if __name__ == "__main__":

    if jsonabfrage("schlafenszeit", "on") == True:
        windll.user32.ShowWindow(h, 0)
        create_windows()

    if jsonabfrage("gesperrt", "on") == True:
        windll.user32.ShowWindow(h, 0)
        create_windows()

    systray.start()
    maincheck()