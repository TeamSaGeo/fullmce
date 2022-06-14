from qgis.PyQt.QtWidgets import *
from qgis.core import QgsVectorLayer, QgsVectorFileWriter
import shutil, os

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
        self.listContraintes = []
        self.listContraintesNotReady = []

        # Listen to spinbox contraintes
        self.iface.dlg.SB_NB_CONTRAINTE.valueChanged.connect(
            lambda: self.value_changed())

        # Listen to list of contraintes not ready
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.itemSelectionChanged.connect(
            lambda : self.selection_changed())

        # Listen to button add/delete row, reclassification contraintes
        self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.clicked.connect(
            lambda : self.delete_reclass_row_param())

        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.clicked.connect(
            lambda : self.add_reclass_row_param())


    def value_changed(self):
        # Row count
        spinbox_value = self.iface.dlg.SB_NB_CONTRAINTE.value()
        self.iface.dlg.TBL_CONTRAINTE.setRowCount(spinbox_value)
        self.iface.dlg.TBL_CONTRAINTE.verticalHeader().setVisible(True)

        # Update list of contraintes
        self.listContraintes = self.listContraintes[:spinbox_value]

        for row in range(spinbox_value):
            # Initialise input widget
            contrainte_name = QLineEdit()
            contrainte_name.setFont(self.myFont)

            contrainte_path = QLineEdit()
            contrainte_path.setFont(self.myFont)
            contrainte_path.setEnabled(False)

            toolButton = QToolButton()
            toolButton.setText('...')

            checkbox = QCheckBox()

            # Handle items
            r = row
            contrainte_name.textEdited.connect(
                lambda name=row, row=r: self.set_contrainte_name(name, row))
            toolButton.released.connect(
                lambda r=r: self.set_contrainte_path(r))
            checkbox.stateChanged.connect(
                lambda status=row, row=r: self.set_contrainte_status(status, row))

            # Set contrainte name, path, button, checkbox
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 0, contrainte_name)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 1, contrainte_path)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 2, toolButton)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 3, checkbox)

            # Append list of contraintes
            if row >= len(self.listContraintes):
                contrainte = [
                    contrainte_name.text(), contrainte_path.text(), 0]
                self.listContraintes.append(contrainte)
            contrainte_name.setText(self.listContraintes[row][0])
            contrainte_path.setText(self.listContraintes[row][1])
            checkbox.setCheckState(self.listContraintes[row][2])

        self.iface.dlg.TBL_CONTRAINTE.setStyleSheet(
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 15px; padding-right: 15px;}")

    def set_contrainte_name(self, name, row):
        self.listContraintes[row][0] = name

    def set_contrainte_path(self, row):
        filename, _filter = QFileDialog.getOpenFileName(
            self.iface.dlg.TBL_CONTRAINTE, "Choisir une image", "", "*.shp")
        inlineEdit = self.iface.dlg.TBL_CONTRAINTE.cellWidget(row, 1)
        inlineEdit.setText(filename)
        self.listContraintes[row][1] = filename

    def set_contrainte_status(self, status, row):
        self.listContraintes[row][2] = status

    def contraintes_empty(self):
        self.listContraintesNotReady = self.listContraintes.copy()
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.clear()
        nb_tab = self.iface.dlg.STACKED_WIDGET_RECLASS.count()
        for ind in range(nb_tab-1,0,-1):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
            self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)

        for i, contrainte in enumerate(self.listContraintes):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            if contrainte[2] == 2:
                self.listContraintesNotReady.remove(contrainte)
            else:
                self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte[0])
                # Initialize tableau param
                self.initialize_reclass_param(i)
            if not contrainte[0] or not contrainte[1]:
                msg_name = "Entrez un nom pour la contrainte numéro"
                msg_path = "Sélectionner une image pour la contrainte numéro"
                button = QMessageBox.critical(
                    self.iface.dlg,
                    "Erreur ...",
                    f"{msg_name} {i+1}" if not contrainte[0] else f"{msg_path} {i+1}",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return True
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        return False

    def initialize_reclass_param(self, i):
        tab = QTableWidget()

        # Column count
        columns = ["Nom de l'attribut","Nouvelle valeur", "Entre(incluse)", "et (non incluse)"]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.verticalHeader().setVisible(False)

        self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(i,tab)
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)
        self.add_reclass_row_param()

        # Table will fit the screen horizontally
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def selection_changed(self):
        # Get selected contrainte
        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)

        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        if row == 0:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)
        else:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(True)

    def add_reclass_row_param(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row + 1)

        # Initialise input widget
        contrainte_champ = QLineEdit()
        contrainte_champ.setFont(self.myFont)
        contrainte_val = QLineEdit()
        contrainte_val.setFont(self.myFont)
        contrainte_start = QLineEdit()
        contrainte_start.setFont(self.myFont)
        contrainte_end = QLineEdit()
        contrainte_end.setFont(self.myFont)

        tab.setCellWidget(row, 0, contrainte_champ)
        tab.setCellWidget(row, 1, contrainte_val)
        tab.setCellWidget(row, 2, contrainte_start)
        tab.setCellWidget(row, 3, contrainte_end)

    def delete_reclass_row_param(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row - 1)
        if row == 1:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)


    def reclassification(self):
        for i,contrainte in enumerate(self.listContraintesNotReady):
            # import input contrainte
            contrainte_name = contrainte[0]
            contrainte_path = contrainte[1]
            contrainte_champ = contrainte_champ

            output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(), contrainte_name + ".shp")


            vlayer = QgsVectorLayer(contrainte_path,contrainte_name, "ogr")
            if not vlayer.isValid():
                print("Layer failed to load!")
            else:
                #change data
                features = vlayer.getFeatures()

                field_idx = vlayer.fields().indexOf('CODE_VOIE')
                field_type = vlayer.fields().at(field_idx).typeName()
                new_value = 150

                vlayer.startEditing()
                for feat in features:
                    vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
                QgsVectorFileWriter.writeAsVectorFormat(vlayer, output_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")


# nb_tab = self.iface.dlg.STACKED_WIDGET_RECLASS.count()
# nb_list = len(self.listContraintes)
# nb_list_notready = len(self.listContraintesNotReady)
#
# # nb_tab < nb_list (insertion à la fin)
# if nb_tab < nb_list_notready:
#     for ind in range(nb_tab,nb_list_notready,1):
#         if self.listContraintes[ind][2] != 2:
#             self.initialize_reclass_param(ind)
# elif nb_tab > nb_list_notready :
#     for ind in range(nb_tab-1,nb_list_notready-1,-1):
#         tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
#         button = QMessageBox.critical(
#             self.iface.dlg,
#             "Erreur ...",
#             f"remove i: {ind} tab : {tab}",
#             buttons=QMessageBox.Ok,
#             defaultButton=QMessageBox.Ok,
#             )
#             self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)
#     if self.listContraintes[ind][2] == 2:
#         tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
#         button = QMessageBox.critical(
#             self.iface.dlg,
#             "Erreur ...",
#             f"remove i: {ind} tab : {tab}",
#             buttons=QMessageBox.Ok,
#             defaultButton=QMessageBox.Ok,
#             )
#             self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)
#
#
# # nb_tab = nb_list Si ready alors remove
# for ind in range(nb_list):
#     if self.listContraintes[ind][2] == 2:
#         tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
#         button = QMessageBox.critical(
#             self.iface.dlg,
#             "Erreur ...",
#             f"remove i: {ind} tab : {tab}",
#             buttons=QMessageBox.Ok,
#             defaultButton=QMessageBox.Ok,
#             )
#             self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)
#
# # Si not ready et surplus
# # nb_tab < nb_list et nb_list >= nb_list_notready
# for ind in range(nb_tab-1,nb_list_notready-1,-1):
#     # si not ready alors decaler
#     if self.listContraintes[ind][2] == 0:
#         for index in range(nb_list_notready+1,ind,-1):
#             suivant = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(index)
#             self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(index,suivant)
#         self.initialize_reclass_param(ind)
#     # si ready
#     elif self.listContraintes[ind][2] == 2:
#         tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
#         button = QMessageBox.critical(
#             self.iface.dlg,
#             "Erreur ...",
#             f"remove i: {ind} tab : {tab}",
#             buttons=QMessageBox.Ok,
#             defaultButton=QMessageBox.Ok,
#             )
#             self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)
#
#
#
#
#
#         for index in range(nb_list_notready+1,ind,-1):
#             suivant = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(index)
#             self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(index,suivant)
#         self.initialize_reclass_param(ind)
