from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt
import pyodbc

class ManagePermissionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(400, 400)
        self.setWindowTitle('Manage Permissions')

        self.username_label = QLabel('Username:', self)
        self.username_input = QComboBox(self)

        self.database_label = QLabel('Database:', self)
        self.database_combo = QComboBox(self)

        self.permission_label = QLabel('Permission:', self)
        self.permission_combo = QComboBox(self)
        self.permission_combo.addItems(['GRANT', 'DENY', 'REVOKE'])

        self.select_checkbox = QCheckBox('SELECT', self)
        self.insert_checkbox = QCheckBox('INSERT', self)
        self.update_checkbox = QCheckBox('UPDATE', self)
        self.delete_checkbox = QCheckBox('DELETE', self)

        self.apply_button = QPushButton('Apply', self)
        self.apply_button.clicked.connect(self.apply_permissions)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.apply_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.database_label)
        main_layout.addWidget(self.database_combo)
        main_layout.addWidget(self.permission_label)
        main_layout.addWidget(self.permission_combo)
        main_layout.addWidget(self.select_checkbox)
        main_layout.addWidget(self.insert_checkbox)
        main_layout.addWidget(self.update_checkbox)
        main_layout.addWidget(self.delete_checkbox)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.load_databases_and_users()

    def load_databases_and_users(self):
        try:
            # Use Windows Authentication (Trusted Connection)
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-HBC5E0J;DATABASE=master;Trusted_Connection=yes')
            cursor = conn.cursor()

            # Load databases
            cursor.execute("SELECT name FROM sys.databases")
            databases = cursor.fetchall()
            self.database_combo.addItems([db[0] for db in databases])

            # Load users
            cursor.execute("SELECT name FROM sys.sql_logins")
            users = cursor.fetchall()
            self.username_input.addItems([user[0] for user in users])

            conn.close()
        except Exception as e:
            self.show_error_message(f"Error loading databases and users: {str(e)}")

    def apply_permissions(self):
        username = self.username_input.currentText()
        database = self.database_combo.currentText()
        permission_type = self.permission_combo.currentText()
        permissions = self.get_selected_permissions()

        if username and permission_type and permissions and database:
            try:
                permission_sql = self.construct_permission_sql(permission_type, permissions, database)
                print(f"SQL command to execute: {permission_sql}")
                self.show_result_message(f"Permissions {permission_type}ed to user: {username} on database: {database}")
            except Exception as e:
                self.show_error_message(f"Error: {str(e)}")
        else:
            self.show_error_message("Please enter a username, select a database, and select permissions")

    def get_selected_permissions(self):
        permissions = []
        if self.select_checkbox.isChecked():
            permissions.append('SELECT')
        if self.insert_checkbox.isChecked():
            permissions.append('INSERT')
        if self.update_checkbox.isChecked():
            permissions.append('UPDATE')
        if self.delete_checkbox.isChecked():
            permissions.append('DELETE')
        return permissions

    def construct_permission_sql(self, permission_type, permissions, database):
        permission_sql = f"{permission_type} "
        if permissions:
            permission_sql += ", ".join(permissions) + " "
        permission_sql += f"ON [{database}].[dbo].[table] TO [{self.username_input.currentText()}]"
        return permission_sql

    def show_result_message(self, message):
        QMessageBox.information(self, 'Success', message)

    def show_error_message(self, message):
        QMessageBox.critical(self, 'Error', message)


# Example usage:
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ManagePermissionsWindow()
    window.show()
    sys.exit(app.exec_())
