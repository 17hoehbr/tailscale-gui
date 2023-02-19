import subprocess
import webbrowser
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon

class Tailscale:
    def __init__(self, tray):
        self.tray = tray
        self.menu = QMenu()
        self.connect = QAction('Connect')
        self.disconnect = QAction('Disconnect')
        self.devices = QMenu('Devices')
        self.dashboard = QAction("Tailscale Dashboard")
        self.quit = QAction("Quit")

        # set up the menu
        status = self.tailscale_status()
        if status == 'Tailscale is stopped.':
            self.menu.addAction(self.connect)
        else:
            self.menu.addAction(self.disconnect)
            self.menu.addMenu(self.devices)
            self.get_devices()
        
        self.menu.addAction(self.dashboard)
        self.menu.addAction(self.quit)

        # connect the actions to the corresponding functions
        self.connect.triggered.connect(self.tailscale_connect)
        self.disconnect.triggered.connect(self.tailscale_disconnect)
        self.dashboard.triggered.connect(lambda: webbrowser.open("https://login.tailscale.com/admin/machines"))
        self.quit.triggered.connect(app.quit)

        # Adding options to the System Tray
        self.tray.setContextMenu(self.menu)
    
    def tailscale_status(self):
        tailscale_status = subprocess.run(['tailscale', 'status'], capture_output=True, text=True).stdout.strip("\n")
        return tailscale_status

    def tailscale_connect(self):
        subprocess.run(['pkexec', 'tailscale', 'up'])

        self.menu.removeAction(self.connect)

        self.menu.insertAction(self.menu.actions()[0], self.disconnect)

        self.menu.insertMenu(self.menu.actions()[1], self.devices)
        self.get_devices()

    def tailscale_disconnect(self):
        subprocess.run(['pkexec', 'tailscale', 'down'])

        self.devices.clear()  # clear the devices menu
        self.menu.removeAction(self.disconnect)
        self.menu.removeAction(self.devices.menuAction())

        self.menu.insertAction(self.menu.actions()[0], self.connect)

    def get_devices(self):
        self.devices.clear()
        status = self.tailscale_status()
        status = status.splitlines()
        self.device_list = []
        for d in status:
            d = d.split(' ')
            d = [word for word in d if word not in ["", "#", "Health", "check:"]]
            if len(d) >= 2:
                self.device_list.append(d)
                action = QAction(d[1], self.devices)
                self.devices.addAction(action)
        print(self.device_list)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

icon = QIcon("tailscale.png")

# Adding item on the menu bar
tray = QSystemTrayIcon()
tray.setIcon(icon)

tray.setVisible(True)

tailscale = Tailscale(tray) # pass the tray instance to the Tailscale constructor

app.exec_()