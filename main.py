#!/usr/bin/env python3

import logging
import threading
import pathlib
import time

here = pathlib.Path(__file__).parent

import pystray
from PIL import Image
import lib2fas
import pyperclip

app = None


def load_logo():
    image = Image.open(here / "logo.png")
    return image


def time_until_cycle() -> float:
    now = time.time()
    time_left = 30.0 - (now % 30.0)
    return time_left


class ServiceMenuItem(pystray.MenuItem):
    def __init__(self, entry):
        self.entry = entry
        super(ServiceMenuItem, self).__init__(
            f"{entry.name} - {entry.otp.account}", self.on_click
        )

    def on_click(self):
        name = self.entry.name
        code = self.entry.generate()
        logging.info(f"code for {name} is {code}")
        pyperclip.copy(code)
        t = time_until_cycle()
        if t < 5.0:
            app.notify("hold up")
            time.sleep(t)
            code = self.entry.generate()
            pyperclip.copy(code)
            app.notify("copied")


class TwoFactorDesktop(object):
    def __init__(self):
        self.showing_notice = False
        logging.info("Loading tokens")
        self.services = lib2fas.load_services(pathlib.Path.home() / "2fas-backup.2fas")
        self.icon = pystray.Icon("2FAS", icon=load_logo())
        self.draw_menu()

    def draw_timer(self, item) -> str:
        return f"Time left: {time_until_cycle():0.2f}"

    def draw_menu(self) -> None:
        menu_items = []

        menu_items.append(pystray.MenuItem(self.draw_timer, None))

        for entry in self.services.all():
            menu_items.append(ServiceMenuItem(entry))

        menu_items.extend(
            [
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.stop),
            ]
        )

        self.icon.menu = pystray.Menu(*menu_items)

    def redraw_thread(self):
        """
        pystray needs this to refresh the timer, it'll only redraw the menu (updating the string)
        when update_menu is called. Seems to be okay to call it from a separate thread
        """
        logging.info("starting update thread")
        time.sleep(1)
        while self.do_update:
            time.sleep(1)
            self.icon.update_menu()
        logging.info("ending update thread")

    def notify(self, message):
        if self.showing_notice:
            self.icon.remove_notification()
        self.showing_notice = True
        self.icon.notify(message, "2FAS")

    def run(self):
        logging.info("Running update thread")
        self.do_update = True
        self.updater = threading.Thread(name="updater", target=self.redraw_thread)
        self.updater.start()
        logging.info("Running tray icon")
        self.icon.run()
        logging.info("Shutting down")

    def stop(self):
        logging.info("Stopping")
        self.do_update = False
        self.icon.stop()
        self.updater.join()


def main():
    global app
    logging.info("Create app")
    app = TwoFactorDesktop()
    app.run()
    logging.info("Done running")


if __name__ == "__main__":
    logging.basicConfig(
        filename=here / "2fas-desktop.log",
        filemode="w",
        encoding="utf-8",
        level=logging.DEBUG,
    )
    main()
