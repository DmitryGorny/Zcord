from PyQt6 import QtCore, QtWidgets
import os
from logic.Authorization.AuthorizationWindow.AuthorizationWindowDisplay import AuthoriztionWindowDisplay
from logic.Main.MainWindow import MainWindow
import sys


if __name__ == "__main__":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--unsafely-treat-insecure-origin-as-secure=http://127.0.0.1:8080 "
        "--allow-http-screen-capture "
        "--disable-features=WebRtcHideLocalIpsWithMdns "
        "--webrtc-max-cpu-consumption-percentage=100"
    )
    app = QtWidgets.QApplication(sys.argv)
    app.keyPressEvent = None
    AuthorizationWindow = AuthoriztionWindowDisplay()

    AuthorizationWindow.show()
    AuthorizationWindow.exec()

    Main = MainWindow(AuthorizationWindow.getUser())
    Main.show()

    app.exec()
