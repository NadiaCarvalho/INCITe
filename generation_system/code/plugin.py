import sys
import time
import threading

from PyQt5 import QtCore, QtGui, QtQml, QtQuick


class MockHTTPRequest(QtCore.QObject):
    requested = QtCore.pyqtSignal(QtCore.QVariant)

    @QtCore.pyqtSlot(str, str, QtCore.QVariant)
    def request(self, verb, endpoint, data):
        """Expensive call"""
        print verb, endpoint, data

        def thread():
            time.sleep(1)
            self.requested.emit("expensive result")

        threading.Thread(target=thread).start()

app = QtGui.QGuiApplication(sys.argv)
view = QtQuick.QQuickView()
context = view.rootContext()

QtQml.qmlRegisterType(MockHTTPRequest, 'Service', 1, 0, 'MockHTTPRequest')

view.setSource(QtCore.QUrl("main.qml"))
view.show()
app.exec_()