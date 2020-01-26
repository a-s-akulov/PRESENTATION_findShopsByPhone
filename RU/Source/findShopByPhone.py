from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pyodbc

from GUI.GUI import Ui_MainWindow
import GUI.GUI_child



class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        """Create main window."""
        self.findedPhones = dict()

        QtWidgets.QMainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('findShopByPhone.ico'))

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.find)
        self.ui.button_get_data.clicked.connect(SQL.get_sql_data)
        self.ui.listWidget.itemDoubleClicked['QListWidgetItem*'].connect(lambda item: self.showChildWindow(item))


    def find(self):
        """Finding shop by phone and display it at self.ui.label_3."""
        self.ui.label_3.setText("Поиск магазинов...")
        self.ui.listWidget.clear()

        number = self.ui.lineEdit.text().strip()
        number = "".join([c for c in number if c.isdecimal()])
        self.ui.lineEdit.setText(number)
        
        if not number:
            self.ui.label_3.setText("Строка ввода номера для поиска пуста")
            return

        self.findedPhones = dict()
        findedShops = { x[1] for x in SQL.sqlPhones if (number in x[0]) and (x[1] in SQL.sqlShops) }
        for x in SQL.sqlPhones:
            phone = x[0]
            shop = x[1]
            
            if shop in findedShops:
                if shop in self.findedPhones:
                    self.findedPhones[shop].append(phone) 
                else:
                    self.findedPhones[shop] = [phone]

        for a in self.findedPhones:
            text = f"{SQL.sqlShops[a]}    -    " + " ".join(self.findedPhones[a])
            self.ui.listWidget.addItem(text)

        self.ui.label_3.setText(f"Найдено магазинов: {len(self.findedPhones)}")


    def showChildWindow(self, item):
        """Create child window by double click on element at list."""
        data = item.text().split("    -    ")

        self.childWindow = ShowChildWindow(data[0])
        self.childWindow.textBrowser.setText("{}\n\n{}".format(data[0], data[1].replace(' ', '\n')))

        self.childWindow.show()



class ShowChildWindow(QtWidgets.QMainWindow, GUI.GUI_child.Ui_MainWindow):
    """Child window constructor."""
    def __init__(self, title="Child Window"):
        """Create child window."""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.textBrowser.setStyleSheet("font-size: 20px")



class FncsSQL():
    """SQL module."""
    def __init__(self):
        """Params initialization."""

        self.sqlShops = {}
        self.sqlPhones = []

        # SQL CONFIG PARAMS
        self.SQLConfig = {
            "driver": r"{SQL Server}",
            "server": r"mailserver\newbooksql",
            "database": "ServiceDesk",
            "UID": "",
            "password": "",
            "Trusted_Connection": "yes", # USE WINDOWS NT AUTHENTIFICATION
            }


    def get_sql_data(self):
        """Getting data from SQL server to self.sqlShops = {} and self.sqlPhones = []."""
        MAIN.ui.listWidget.clear()
        MAIN.ui.label_3.setText("Подключение к SQL...")
        MAIN.ui.label_3.repaint()
        try:
            conn = pyodbc.connect( f'Driver={self.SQLConfig["driver"]}; Server={self.SQLConfig["server"]}; Database={self.SQLConfig["database"]};' \
                f'UID={self.SQLConfig["UID"]}; PWD={self.SQLConfig["password"]}; Trusted_Connection={self.SQLConfig["Trusted_Connection"]};')
        except BaseException as error:
            MAIN.ui.label_3.setText(f"pyodbc.connect error: {error}")
            return False
        
        try:
            cur = conn.cursor()
        except BaseException as error:
            MAIN.ui.label_3.setText(f"""Can't create cursor at server. conn.cursor error: '{error}'.""")
            return

        else:
            MAIN.ui.label_3.setText("Подключение к SQL успешно. Получение данных...")
            MAIN.ui.label_3.repaint()

        self.sqlShops = {}
        self.sqlPhones = []

        # SHOPS
        query = "SELECT PT_ID, PT_SHORTNAME FROM dbo.PARTNERS"
        data, error = self.send_sql_request(cur, query)
        if not data:
            MAIN.ui.label_3.setText(error)
            return

        for x in data:
            self.sqlShops[x[0]] = x[1].strip()

        # PHONES
        query = "SELECT PT_ID, CODE, PHONE FROM dbo.PHONES"
        data, error = self.send_sql_request(cur, query)
        if not data:
            MAIN.ui.label_3.setText(error)
            return

        for x in data:
            shopId = x[0]
            code = x[1]
            phone = x[2].strip()
            result = ""
            if not (code or phone):
                continue

            if code:
                result += str(code)
            for c in phone:
                if c.isdecimal():
                   result += c
            
            if result[0] == "+":
                result = "8" + result[2:len(result)]
            if len(result) == 11 and result[0] == "7":
                result = "8" + result[1:len(result)]
            elif len(result) == 10:
                result = "8" + result

            self.sqlPhones.append([result, shopId])
        
        MAIN.ui.label_show_dataStats.setText(f"Загружено магазинов: {len(self.sqlShops)}, телефонов: {len(self.sqlPhones)}")
        MAIN.ui.label_3.setText(f"Данные успешно загружены. Магазинов: {len(self.sqlShops)}, телефонов: {len(self.sqlPhones)}")
        
    
    def send_sql_request(self, cur, query):
        """Send request to SQL server and returns getted data.
        
        cur = cursor at server, getted with conn.cursor()
        query = SQL query. example: 'SELECT * from dbo.MyTable WHERE someColumn = 1'

        If operation successfull - return (data, None) else - return (False, errorText)
        
        """
        data = []

        try:
            cur.execute(query)
        except pyodbc.ProgrammingError as error:
            text = f"Can't execute query '{query}'. cur.execute error: '{error}'."
            return (False, text)
        else:

            # Other modes
            while True:
                try:
                    row = cur.fetchone()
                except pyodbc.ProgrammingError as error:
                    text = f"Can't execute query '{query}'. cur.fetchone error: '{error}'."
                    return (False, text)

                if not row:
                    break
                else:
                    data.append(row)

            return (data, None)


if __name__ == "__main__":
    SQL = FncsSQL()

    app = QtWidgets.QApplication([])
    MAIN = mywindow()
    MAIN.show()

    sys.exit(app.exec())