from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox, QPushButton, QLabel, QLineEdit

table = None

class FillTablesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(800, 600)
        self.setWindowTitle('Fill Tables')

        from app.UI.conection_form import INFO
        from app.logic.conection import Connection

        try:
            SERVER, DATABASE, PORT = INFO['server'], INFO['database'], INFO['port']
            con = Connection().connect_to_database(SERVER, DATABASE, PORT)
            cursor = con.cursor()
            tables = cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES').fetchall()
            print(tables)
            con.close()
        except Exception as e:
            print(e)
            tables = []

        table_names = []
        for i, name in enumerate(tables):
            table_names.append(tables[i][0])

        print(table_names)
        self.table_label = QLabel('Select Table:', self)
        self.table_dropdown = QComboBox(self)
        self.table_dropdown.addItems(table_names)

        self.create_button = QPushButton('CREAR', self)
        self.update_button = QPushButton('ACTUALIZAR', self)
        self.delete_button = QPushButton('BORRAR', self)
        self.view_button = QPushButton('VER', self)

        layout = QVBoxLayout()
        layout.addWidget(self.table_label)
        layout.addWidget(self.table_dropdown)
        layout.addWidget(self.view_button)
        layout.addWidget(self.create_button)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.view_button.clicked.connect(self.show_view_layout)
        self.create_button.clicked.connect(self.show_create_layout)
        self.update_button.clicked.connect(self.show_update_layout)
        self.delete_button.clicked.connect(self.show_delete_layout)

    def send_data(self):
        from app.logic.conection import Connection
        from app.UI.conection_form import INFO 

        inputs = self.findChildren(QLineEdit)
        print("INPUTS: ", inputs)
        inputs.pop()
        values = '('
        for i, item in enumerate(inputs):
          if i == 0:
              values += f"{item.text()}" + ','
              continue
          if i != len(inputs) - 1:
            print(item.text())
            values += f"'{item.text()}'" + ','
          else:
              values += f"'{item.text()}'" + ')'
        
        try:
            print(values)
            server, port, database = INFO['server'], INFO['port'], INFO['database']
            conn = Connection().connect_to_database(server, database, port)
            cursor = conn.cursor()
            global table
            sentence = f'INSERT INTO {table} VALUES{values}'
            print(sentence)
            cursor.execute(sentence)
        except Exception as e:
            print("un error ocurrio------", e)


    def send_data_updated(self):
        from app.logic.conection import Connection
        from app.UI.conection_form import INFO 

        server, database, port = INFO['server'], INFO['database'], INFO['port']
        conn = Connection().connect_to_database(server, database, port)
        cursor = conn.cursor()
        
        table_selected = self.table_dropdown.currentText()
        fields = cursor.execute(f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME LIKE {table_selected}').fetchall() 

        query = f'UPDATE {table_selected} SET '
        # iterar por los inputs
        for i, item in enumerate(QLineEdit):
            if i != len(QLineEdit) - 1:
                query += fields[i] + "=" + item.text() + ", "
            else:
                query += fields[i] + "=" + item.text()

        query += f'WHERE Id = {self.fields_label.text()}'
      

    def show_view_layout(self):
        from app.UI.conection_form import INFO
        from app.logic.conection import Connection

        self.clear_layout()
        table_selected = self.table_dropdown.currentText()
        server, database, port = INFO['server'], INFO['database'], INFO['port']
        try:
            conn = Connection().connect_to_database(server, database, port)
            query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME LIKE '{table_selected}'"
            cursor = conn.cursor()
            cursor.execute(query)
            fields = cursor.fetchall()
            fields_names = []
            for i, name in enumerate(fields):
                fields_names.append(fields[i][0])
            print(fields)
            print(fields_names)
            cursor.execute(f'SELECT * FROM {table_selected}')
            data = cursor.fetchall()
            print(data)

            self.result_table = QTableWidget()
            self.result_table.setColumnCount(len(fields_names))
            self.result_table.setHorizontalHeaderLabels(fields_names)
            self.result_table.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

            self.layout().addWidget(self.result_table)
        except Exception as e:
            print(e)

    def show_create_layout(self):
        from app.UI.conection_form import INFO
        from app.logic.conection import Connection
        self.clear_layout()
        self.fields_label = QLabel('Campos para crear entrada', self)
        
        # traer los campos que tiene una tabla
        global table
        table = self.table_dropdown.currentText()
        table_selected = self.table_dropdown.currentText()
        server, database, port = INFO['server'], INFO['database'], INFO['port']
        try:
          conn = Connection().connect_to_database(server, database, port)
          cursor = conn.cursor()
          sentence = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME LIKE '{table_selected}';"
          cursor.execute(sentence)
          table_fields = cursor.fetchall()
          table_names = []
          for i, name in enumerate(table_fields):
              table_names.append(table_fields[i][0])

          print('table fields: ', table_names)
          # crear los campos input por cada columna
          for item in table_names:
            self.item_label = QLabel(f'{item}:', self)
            self.item_input = QLineEdit(self)
            self.layout().addWidget(self.item_label)
            self.layout().addWidget(self.item_input)

        except Exception as e:
            print(e)


        self.fields_input = QLineEdit(self)
        self.save_button = QPushButton('Guardar', self)
        self.save_button.clicked.connect(self.send_data)

        self.layout().addWidget(self.fields_label)
        self.layout().addWidget(self.fields_input)
        self.layout().addWidget(self.save_button)

    def show_update_layout(self):
        from app.UI.conection_form import INFO
        from app.logic.conection import Connection
        
        self.clear_layout()
        self.id_label = QLabel('Mostrar input de ID', self)
        self.id_input = QLineEdit(self)
        self.fields_label = QLabel('Mostrar campos para actualizar entrada', self)
        # crear los campos inputs para actualizar
        # traer los campos que tiene una tabla
        table_selected = self.table_dropdown.currentText()
        server, database, port = INFO['server'], INFO['database'], INFO['port']
        try:
          conn = Connection().connect_to_database(server, database, port)
          cursor = conn.cursor()
          sentence = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME LIKE '{table_selected}';"
          table_fields = cursor.execute(sentence).fetchall()
          table_names = []
          for i, name in table_fields():
            table_names.append(table_fields[i][0])
          # crear los campos input por cada columna
          for item in table_names:
            self.item_label = QLabel(f'{item}:', self)
            self.item_input = QLineEdit(self)
            self.layout().addWidget(self.item_label)
            self.layout().addWidget(self.item_input)
        except Exception as e:
           print(e)

        self.fields_input = QLineEdit(self)
        self.save_button = QPushButton('Guardar', self)
        self.save_button.clicked.connect(self.send_data_updated)

        self.layout().addWidget(self.id_label)
        self.layout().addWidget(self.id_input)
        self.layout().addWidget(self.fields_label)
        self.layout().addWidget(self.fields_input)
        self.layout().addWidget(self.save_button)

    def show_delete_layout(self):
        self.clear_layout()
        self.id_label = QLabel('Campo ID', self)
        self.id_input = QLineEdit(self)
        self.delete_button = QPushButton('Borrar', self)
        self.delete_button.clicked.connect(self.delete_data)

        self.layout().addWidget(self.id_label)
        self.layout().addWidget(self.id_input)
        self.layout().addWidget(self.delete_button)

    def delete_data(self):
      from app.UI.conection_form import INFO
      from app.logic.conection import Connection

      server, database, port = INFO['server'], INFO['database'], INFO['port']
      try:
        conn = Connection().connect_to_database(server, database, port) 
        cursor = conn.cursor()
        table_selected = self.table_dropdown.currentText()
        id = self.id_input.text()
        query = f'DELETE FROM {table_selected} WHERE Id LIKE {id}'
        cursor.execute(query)
      except Exception as e:
          print(e)

    def clear_layout(self):
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
