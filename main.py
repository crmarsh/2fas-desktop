#!/usr/bin/env python3

import pathlib

here = pathlib.Path(__file__).parent

import pystray
from PIL import Image
import lib2fas
import pyperclip


def load_logo():
    image = Image.open(here / "logo.png")
    return image


class ServiceMenuItem(pystray.MenuItem):
    def __init__(self, entry):
        self.entry = entry
        super(ServiceMenuItem, self).__init__(entry.name, self.on_click)

    def on_click(self):
        name = self.entry.name
        code = self.entry.generate()
        print(f"code for {name} is {code}")
        pyperclip.copy(code)


def main():
    services = lib2fas.load_services(pathlib.Path.home() / "2fas-backup.2fas")

    icon = pystray.Icon("2FAS", icon=load_logo())

    menu_items = []

    for entry in services.all():
        menu_items.append(ServiceMenuItem(entry))

    menu_items.extend(
        [
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda: icon.stop()),
        ]
    )

    icon.menu = pystray.Menu(*menu_items)

    icon.run()


if __name__ == "__main__":
    main()
