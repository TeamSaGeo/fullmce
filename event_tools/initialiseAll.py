from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import *
from .contrainte import Contrainte
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsFeatureRequest
import shutil, os
from datetime import datetime

class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()

        # Initialize list of contraintes
        self.listContraintes = []
        self.listContraintesNotReady = []

    def display_page1(self):
        concepteurpath = os.path.join(
            self.iface.plugin_dir, 'event_tools/concepteur.csv')

        concepteurs = []
        with open(concepteurpath, mode='r') as infile:
            concepteur_header = next(infile)
            for row in infile:
                data = row.rstrip('\n').split(";")
                concepteurs.append(data)

        # Populate GB_DEVELOPER
        devbox = QVBoxLayout()  # create groupbox layout
        developper = " ".join(concepteurs[0][1::-1])
        labeldevelopper = QLabel(developper)
        labeldevelopper.setFont(self.myFont)
        devbox.addWidget(labeldevelopper)
        self.iface.dlg.GB_DEVELOPER.setLayout(devbox)

        # Populate GB_CONCEPTEUR
        conceptbox = QVBoxLayout()  # create groupbox layout
        for concepteur in concepteurs:
            concepteurtxt = " ".join(concepteur[1::-1])
            concepteurtxt += " (" + concepteur[-1] + ")"
            labelconcepteur = QLabel(concepteurtxt)
            labelconcepteur.setFont(self.myFont)
            conceptbox.addWidget(labelconcepteur)
            self.iface.dlg.GB_CONCEPTEUR.setLayout(conceptbox)

        # Populate TE_INFO
        self.iface.dlg.TE_INFO.setText(
            "Ce plugin a été spécialement dévéloppé par l'Institut Pasteur de Madagascar dans le cadre d'une étude sur la surveillance constante du paludisme et la détermination des zones prioritaires aux Campagnes d'Aspertion Intra-Domiciliaire (CAID) à Madagascar. Son utilisation est privilégié dans le domaine de la santé publique.")
        self.iface.dlg.TE_INFO.setFont(self.myFont)

        # Populate LBL_ROHY
        self.iface.dlg.LBL_ROHY.setText(
              "<a href=\"mailto:sfamenontsoa@pasteur.mg\">Suggestions ou Remarques</a>")
        self.iface.dlg.LBL_ROHY.setTextFormat(Qt.RichText)
        self.iface.dlg.LBL_ROHY.setTextInteractionFlags(
            Qt.TextBrowserInteraction)
        self.iface.dlg.LBL_ROHY.setOpenExternalLinks(True)

    def select_output_dir(self):
        foldername = QFileDialog.getExistingDirectory(
            self.iface.dlg, "Sélectionner le répertoire de sortie")
        self.iface.dlg.LE_OUTPUT_DIR.setText(foldername)
        self.iface.dlg.LE_OUTPUT_DIR.setFont(self.myFont)

    def display_page3(self):
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
        # Listen to spinbox contraintes
        self.iface.dlg.SB_NB_CONTRAINTE.valueChanged.connect(
            lambda: self.update_listContraintes())

        # Listen to list of contraintes not ready
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.itemSelectionChanged.connect(
            lambda : self.select_contrainte_not_ready())

        # Listen to button add/delete row, reclassification contraintes
        self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.clicked.connect(
            lambda : self.delete_reclass_row_param())

        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.clicked.connect(
            lambda : self.add_reclass_row_param())

    def display_next_page(self):
        if self.pageInd == 1 and not self.iface.dlg.LE_OUTPUT_DIR.text():
            button = QMessageBox.critical(
                self.iface.dlg,
                "Erreur ...",
                "Choisissez un répertoire de sortie!",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
                )
        elif self.pageInd == 2 and self.contraintes_is_empty():
            self.pageInd = 2
        elif self.pageInd == 2 and self.listContraintesNotReady == []:
            self.pageInd += 3
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        elif self.pageInd == 3 and not self.reclassification():
            self.pageInd = 3
        else:
            self.pageInd += 1
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)

        return self.pageInd

    def display_previous_page(self):
        self.pageInd -= 1
        if self.pageInd == 0:
            self.iface.dlg.BT_PREVIOUS.setEnabled(False)
        if self.pageInd == 4:
            if self.listContraintesNotReady == []:
                self.pageInd = 2
            else:
                self.pageInd = 3
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
        return self.pageInd

    def update_listContraintes(self):
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
                lambda name=row, row=r: self.listContraintes[row].setname(name))
            toolButton.released.connect(
                lambda r=r: self.select_contrainte_source_path(r))
            checkbox.stateChanged.connect(
                lambda ready=row, row=r: self.listContraintes[row].setready(ready))

            # Set contrainte name, path, button, checkbox
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 0, contrainte_name)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(
                row, 1, contrainte_path)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 2, toolButton)
            self.iface.dlg.TBL_CONTRAINTE.setCellWidget(row, 3, checkbox)

            # Append list of contraintes
            if row >= len(self.listContraintes):
                contrainte = Contrainte(contrainte_name.text(), contrainte_path.text(), 0)
                self.listContraintes.append(contrainte)
            contrainte_name.setText(self.listContraintes[row].name)
            contrainte_path.setText(self.listContraintes[row].source_path)
            checkbox.setCheckState(self.listContraintes[row].ready)

        self.iface.dlg.TBL_CONTRAINTE.setStyleSheet(
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 15px; padding-right: 15px;}")

    def select_contrainte_source_path(self, row):
        filename, _filter = QFileDialog.getOpenFileName(
            self.iface.dlg.TBL_CONTRAINTE, "Choisir une image", "", "*.shp")
        contrainte = self.listContraintes[row]
        if contrainte.source_path_isvalid(filename):
            inlineEdit = self.iface.dlg.TBL_CONTRAINTE.cellWidget(row, 1)
            inlineEdit.setText(filename)
        else:
            button = QMessageBox.critical(
                self.iface.dlg,
                "Erreur ...",
                "Choisissez un fichier valide!",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
                )

    def contraintes_is_empty(self):
        self.listContraintesNotReady = self.listContraintes.copy()
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.clear()
        nb_tab = self.iface.dlg.STACKED_WIDGET_RECLASS.count()
        for ind in range(nb_tab-1,-1,-1):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
            self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)

        for i,contrainte in enumerate(self.listContraintes):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            if contrainte.ready == 2:
                self.listContraintesNotReady.remove(contrainte)
            else:
                # Initialize tableau param
                self.display_page4(i,contrainte)
            if not contrainte.name or not contrainte.source_path:
                msg_name = "Saisir un nom pour la contrainte numéro"
                msg_path = "Sélectionner une image pour la contrainte numéro"
                button = QMessageBox.critical(
                    self.iface.dlg,
                    "Erreur ...",
                    f"{msg_name}" if not contrainte.name else f"{msg_path}" + f"{i+1}",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return True
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)
        return False

    def display_page4(self, i, contrainte):
        ###---------Initialize List contrainte not ready Widget----------
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte.name)

        ###---------Initialize Tab Widget----------
        tab = QTableWidget()

        # Column count
        columns = ["Attribut","Type", "Nouvelle valeur", "Valeur actuelle"]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.verticalHeader().setVisible(False)

        self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(i,tab)
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)
        # self.add_reclass_row_param()

        # Table will fit the screen horizontally
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px;}")

    def select_contrainte_not_ready(self):
        # Get selected contrainte
        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)
        contrainte = self.listContraintesNotReady[i]

        # Initialise  list attribut
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        if row == 0:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)
            self.add_reclass_row_param()
        elif row == 1:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)
        else:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(True)

        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(True)

        # Handle items
        tab.cellWidget(0,0).currentIndexChanged.connect(lambda: self.update_selected_field(contrainte.vlayer, tab))

    def add_reclass_row_param(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row + 1)

        contrainte_field_type = QLineEdit()
        contrainte_field_type.setFont(self.myFont)
        contrainte_field_type.setEnabled(False)
        tab.setCellWidget(row, 1, contrainte_field_type)

        contrainte_val = QLineEdit()
        contrainte_val.setFont(self.myFont)
        tab.setCellWidget(row, 2, contrainte_val)

        start_value = QLineEdit()
        start_value.setFont(self.myFont)
        tab.setCellWidget(row, 3, start_value)

        if row == 0:
            contrainte_field_name = QComboBox()
            contrainte_field_name.setFont(self.myFont)
            tab.setCellWidget(0, 0, contrainte_field_name)

            i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
            contrainte = self.listContraintesNotReady[i]
            for field in contrainte.vlayer.fields():
                contrainte_field_name.addItem(field.name())
            self.update_selected_field(contrainte.vlayer,tab)

        col = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget().columnCount()
        if col == 5:
            end_value = QLineEdit()
            end_value.setFont(self.myFont)
            tab.setCellWidget(row, 4, end_value)

        if row >= 1:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(True)
            tab.setCellWidget(row,0,QLineEdit())
            tab.cellWidget(row,0).setEnabled(False)

    def delete_reclass_row_param(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row - 1)
        if row == 2:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)

    def update_selected_field(self,vlayer,tab):
        field_name = tab.cellWidget(0,0).currentText()

        field_idx = vlayer.fields().indexOf(field_name)
        field_type = vlayer.fields().at(field_idx).typeName()
        tab.cellWidget(0,1).setText(field_type)

        if field_type == "String":
            tab.setColumnCount(4)
            header4 = QTableWidgetItem()
            header4.setText("Valeur actuelle")
            tab.setHorizontalHeaderItem(3,header4)
            tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            tab.setColumnCount(5)
            header3 = QTableWidgetItem()
            header3.setText("Entre (incluse)")
            tab.setHorizontalHeaderItem(3,header3)

            header4 = QTableWidgetItem()
            header4.setText("et (non incluse)")
            tab.setHorizontalHeaderItem(4,header4)

            for row in range(tab.rowCount()):
                end_value = QLineEdit()
                end_value.setFont(self.myFont)
                tab.setCellWidget(row, 4, end_value)

        # Update contrainte instance
        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        contrainte = self.listContraintesNotReady[i]
        contrainte.setfield(field_name,field_type)

    def reclassification(self):
        for i,contrainte in enumerate(self.listContraintesNotReady):
            output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(), contrainte.name + ".shp")

            # Get field name et field type
            vlayer = contrainte.vlayer
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            field_name = tab.cellWidget(0,0).currentText()
            field_idx = vlayer.fields().indexOf(field_name)
            field_type = tab.cellWidget(0,1).text()
            row = -1
            col = -1

            if field_type == "String":
                vlayer,row,col = self.reclassified_string(field_idx,vlayer,tab)
            elif field_type == "Real" or field_type == "Integer":
                vlayer,row,col = self.reclassified_int_real(field_idx,field_type,vlayer,tab)
            elif field_type == "Date":
                vlayer,row,col = self.reclassified_date(field_idx,vlayer,tab)

            if row == -1 and col == -1:
                contrainte.set_reclass_output(vlayer,output_path)
                # QgsVectorFileWriter.writeAsVectorFormat(vlayer, output_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")
            else:
                button = QMessageBox.critical(
                    self.iface.dlg,
                    "Erreur ...",
                    f"Saisir une valeur valide pour la contrainte {contrainte.name} à la colonne numéro {col +1} à la ligne numéro {row + 1}",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return False
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd + 1)
        self.display_page5()
        return True

    def reclassified_string(self,field_idx,vlayer,tab):
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[field_idx]

            # initialize iteration variable
            row = 0
            start_value = tab.cellWidget(0,3).text()
            if not start_value:
                return vlayer,row,3
            new_value = None

            # Start condition
            while value != start_value and row < (tab.rowCount()-1):
                row += 1
                start_value = tab.cellWidget(row,3).text()
                if not start_value:
                    return vlayer,row,3

            # Change value
            if value == start_value:
                new_value = tab.cellWidget(row,2).text()
                if not new_value:
                    return vlayer,row,2

            vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
        return vlayer,-1,-1

    def reclassified_int_real(self,field_idx,field_type,vlayer,tab):
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[field_idx]

            # initialize iteration variable
            row = 0
            try:
                start_value = float(tab.cellWidget(0,3).text())
            except ValueError:
                return vlayer,row,3

            try:
                end_value = float(tab.cellWidget(0,4).text())
            except ValueError:
                return vlayer,row,4

            new_value = None

            # Start condition
            while (value < start_value or value >= end_value) and row < (tab.rowCount() - 1):
                row += 1
                try:
                    start_value = float(tab.cellWidget(row,3).text())
                except ValueError:
                    return vlayer,row,3

                try:
                    end_value = float(tab.cellWidget(row,4).text())
                except ValueError:
                    return vlayer,row,4

            # Change value
            if value < end_value:
                if field_type == "Real":
                    try:
                        new_value = float(tab.cellWidget(row,2).text())
                    except ValueError:
                        return vlayer,row,2

                elif field_type == "Integer":
                    try:
                        new_value = int(tab.cellWidget(row,2).text())
                    except ValueError:
                        return vlayer,row,2

            vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
            # for row in range(tab.rowCount()):
            #     while value >= start_value and value < end_value:
            #         new_value = tab.cellWidget(row,2).text()
            #         vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
        return vlayer,-1,-1

    def reclassified_date(self,field_idx,vlayer,tab):
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[field_idx]

            # initialize iteration variable
            row = 0
            try:
                start_value = datetime.strptime(tab.cellWidget(0,3).text(),'%y-%m-%d')
            except ValueError:
                return vlayer,row,3

            try:
                end_value = datetime.strptime(tab.cellWidget(0,4).text(),'%y-%m-%d')
            except ValueError:
                return vlayer,row,4

            new_value = None

            # Start condition
            while (value < start_value or value >= end_value) and row < (tab.rowCount()-1):
                row += 1
                try:
                    start_value = datetime.strptime(tab.cellWidget(row,3).text(),'%y-%m-%d')
                except ValueError:
                    return vlayer,row,3

                try:
                    end_value = datetime.strptime(tab.cellWidget(row,4).text(),'%y-%m-%d')
                except ValueError:
                    return vlayer,row,4

            # Change value
            if value < end_value:
                try:
                    new_value = datetime.strptime(tab.cellWidget(row,2).text(),'%y-%m-%d')
                except ValueError:
                    return vlayer,row,2

            vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
        return vlayer,-1,-1

    def display_page5 (self):
        reply = QMessageBox.question(
            self.iface.dlg,
            "Question ...",
            "Voulez-vous tout de suite effectuer le traitement des contraintes ?",
            buttons= QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes :
            for contrainte in self.listContraintesNotReady:
                QgsVectorFileWriter.writeAsVectorFormat(contrainte.vlayer, contrainte.output_path, "UTF-8", contrainte.vlayer.crs(), "ESRI Shapefile")

    def initialise_variable_init(self):
        return self

    def initialise_initGui(self):
        self.iface.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            self.display_page1()
            # On click on Suivant
            self.iface.dlg.BT_NEXT.pressed.connect(lambda: self.display_next_page())

            #On click on répertoire de sortie
            self.iface.dlg.BT_OUTPUT.clicked.connect(lambda: self.select_output_dir())

            #On click on Precedent
            self.iface.dlg.BT_PREVIOUS.clicked.connect(lambda: self.display_previous_page())

            self.display_page3()
