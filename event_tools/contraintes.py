from qgis.PyQt.QtWidgets import QHeaderView, QLineEdit, QToolButton, QCheckBox, QFileDialog


class contraintes:
    def __init__(self, iface, myFont):
        self.iface = iface
        self.myFont = myFont

        # Column count
        columns = ["Noms", "Chemins", "", "Prêts"]
        self.iface.dlg.TBL_CONTRAINTE.setColumnCount(len(columns))
        self.iface.dlg.TBL_CONTRAINTE.setHorizontalHeaderLabels(columns)
        # Table will fit the screen horizontally
        self.iface.dlg.TBL_CONTRAINTE.horizontalHeader().setSectionResizeMode(1,
                                                                              QHeaderView.Stretch)
        self.iface.dlg.TBL_CONTRAINTE.horizontalHeader().setSectionResizeMode(2,
                                                                              QHeaderView.ResizeToContents)
        self.iface.dlg.TBL_CONTRAINTE.horizontalHeader().setSectionResizeMode(3,
                                                                              QHeaderView.ResizeToContents)

        # Initialize list of contraintes
        self.contraintes = []

        # Listen to spinbox contraintes
        self.iface.dlg.SB_NB_CONTRAINTE.valueChanged.connect(
            lambda: self.value_changed())

    def value_changed(self):
        # Row count
        spinbox_value = self.iface.dlg.SB_NB_CONTRAINTE.value()
        self.iface.dlg.TBL_CONTRAINTE.setRowCount(spinbox_value)
        self.iface.dlg.TBL_CONTRAINTE.verticalHeader().setVisible(True)

        # Update list of contraintes
        self.contraintes = self.contraintes[:spinbox_value]

        for row in range(spinbox_value):
            # Initialise input widget
            contrainte_name = QLineEdit()
            contrainte_name.setFont(self.myFont)

            contrainte_path = QLineEdit()
            contrainte_path.setFont(self.myFont)

            toolButton = QToolButton()
            toolButton.setText('...')

            checkbox = QCheckBox()

            # Handle items
            r = row
            contrainte_name.textEdited.connect(
                lambda name=row, row=r: self.set_contrainte_name(name, row))
            toolButton.released.connect(
                lambda r=r: self.set_contrainte_path(r))

            # Set contrainte name, path, button, checkbox
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 0, contrainte_name)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 1, contrainte_path)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 2, toolButton)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 3, checkbox)

            # Append list of contraintes
            contrainte = [contrainte_name.text(), contrainte_path.text()]
            self.contraintes.append(contrainte)
            contrainte_name.setText(self.contraintes[row][0])
            contrainte_path.setText(self.contraintes[row][1])

        self.iface.dlg.TBL_CONTRAINTE.setStyleSheet(
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 15px; padding-right: 15px;}")

    def set_contrainte_path(self, row):
        filename, _filter = QFileDialog.getOpenFileName(
            self.iface.dlg.TBL_CONTRAINTE, "Choisir une image", "", "*.shp")
        inlineEdit = self.iface.dlg.TBL_CONTRAINTE.cellWidget(row, 1)
        inlineEdit.setText(filename)
        self.contraintes[row][1] = filename

    def set_contrainte_name(self, name, row):
        self.contraintes[row][0] = name
