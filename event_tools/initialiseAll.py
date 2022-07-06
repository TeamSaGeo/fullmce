# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import *
from .inputData import InputData
from .inputLayer import InputLayer
from .classification import Classification
from qgis.core import QgsVectorFileWriter, QgsField
import os, shutil
from datetime import datetime

class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()

        # Initialize list of InputData
        self.listContraintes = []
        self.listContraintesNotReady = []
        self.listFactors = []
        self.listFactorNotNormalized = []
        self.list_inputLayers = []

    def display_output_config(self):
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
        developper = " ".join(concepteurs[-1][1::-1])
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
        text = QCoreApplication.translate("initialisation","Ce plugin a été spécialement dévéloppé par l'Institut Pasteur de Madagascar dans le cadre d'une étude sur la surveillance constante du paludisme et la détermination des zones prioritaires aux Campagnes d'Aspertion Intra-Domiciliaire (CAID) à Madagascar. Son utilisation est privilégié dans le domaine de la santé publique.")
        self.iface.dlg.TE_INFO.setText(text)
        self.iface.dlg.TE_INFO.setFont(self.myFont)

        # Populate LBL_ROHY
        self.iface.dlg.LBL_ROHY.setText(
              "<a href=\"mailto:sfamenontsoa@pasteur.mg\">" + QCoreApplication.translate("initialisation","Suggestions ou Remarques") + "</a>")
        self.iface.dlg.LBL_ROHY.setTextFormat(Qt.RichText)
        self.iface.dlg.LBL_ROHY.setTextInteractionFlags(
            Qt.TextBrowserInteraction)
        self.iface.dlg.LBL_ROHY.setOpenExternalLinks(True)

    def display_input_config(self, columns, tbl, sb):
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        # Table will fit the screen horizontally
        tbl.setColumnWidth(0,150)
        tbl.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        # Listen to spinbox
        sb.valueChanged.connect(lambda: self.update_listData(tbl,sb))

    def init_classification_input(self):
        name = QCoreApplication.translate("initialisation","Noms")
        path = QCoreApplication.translate("initialisation","Chemins")
        ready = QCoreApplication.translate("initialisation","Prêts")
        columns = [name, path, "", ready]
        self.display_input_config(columns,self.iface.dlg.TBL_CONTRAINTE,self.iface.dlg.SB_NB_CONTRAINTE)

        # Listen to list of contraintes not ready
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.itemSelectionChanged.connect(
            lambda : self.select_contrainte_not_ready())
        # Listen to button add/delete row, reclassification contraintes
        self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.clicked.connect(
            lambda : self.delete_reclass_row_param())
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.clicked.connect(
            lambda : self.add_reclass_row_param())

    def init_standardization_input(self):
        # Get columns name
        tab = self.iface.dlg.TBL_CONTRAINTE
        columns =  [tab.horizontalHeaderItem(col).text() for col in range(tab.columnCount())]
        normalized = QCoreApplication.translate("initialisation","Normalisés")
        columns[3] = normalized

        # Initialize standardization input table
        self.display_input_config(columns,self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

        # Initialize 3 input rows
        self.update_listData(self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

    def display_standardization_table(self, nb_rows):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
        name = QCoreApplication.translate("initialisation","Noms")
        fonctions = QCoreApplication.translate("initialisation","Fonctions")
        sens = QCoreApplication.translate("initialisation","Sens")
        columns = [name, fonctions, sens, "A", "B", "C", "D"]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.verticalHeader().setVisible(True)
        tab.setRowCount(nb_rows)
        tab.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        tab.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        tab.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 8px; padding-right: 8px;}")

    def display_classification_table(self, i, contrainte):
        ###---------Initialize List contrainte not ready Widget----------
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte.name)

        ###---------Initialize Tab Widget----------
        tab = QTableWidget()

        # Column count
        field = QCoreApplication.translate("initialisation","Champ")
        type = QCoreApplication.translate("initialisation","Type")
        value = QCoreApplication.translate("initialisation","Nouvelle valeur")
        init_value = QCoreApplication.translate("initialisation","Valeur Initiale")
        columns = [field,type, value, init_value]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.verticalHeader().setVisible(False)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px;}")

        self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(i,tab)
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)
        # self.add_reclass_row_param()

        # Table will fit the screen horizontally
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_standardization_row(self,row,factor):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION

        factor_name = QLineEdit()
        factor_name.setFont(self.myFont)
        factor_name.setText(factor.name)
        tab.setCellWidget(row, 0, factor_name)

        factor_function = QComboBox()
        factor_function.setFont(self.myFont)
        s_shaped = QCoreApplication.translate("initialisation","S-Shaped (Sigmoïdal)")
        j_shaped = QCoreApplication.translate("initialisation","J-Shaped")
        linear = QCoreApplication.translate("initialisation","Linéaire")
        functions = [s_shaped,j_shaped,linear]
        factor_function.addItems(functions)
        tab.setCellWidget(row, 1, factor_function)

        factor_sens = QComboBox()
        factor_sens.setFont(self.myFont)
        decroissant = QCoreApplication.translate("initialisation","Décroissant")
        croissant = QCoreApplication.translate("initialisation","Croissant")
        symetrique = QCoreApplication.translate("initialisation","Symétrique")
        sens = [decroissant,croissant,symetrique]
        factor_sens.addItems(sens)
        tab.setCellWidget(row, 2, factor_sens)

        for col in range(3,7):
            factor_param = QLineEdit()
            factor_param.setFont(self.myFont)
            tab.setColumnWidth(col,80)
            tab.setCellWidget(row, col, factor_param)

    def select_output_dir(self):
        foldername = QFileDialog.getExistingDirectory(
            self.iface.dlg, QCoreApplication.translate("initialisation","Sélectionner le répertoire de sortie"))
        self.iface.dlg.LE_OUTPUT_DIR.setText(foldername)
        self.iface.dlg.LE_OUTPUT_DIR.setFont(self.myFont)

    def display_next_page(self):
        if self.pageInd == 1 and not self.iface.dlg.LE_OUTPUT_DIR.text():
            button = QMessageBox.critical(
                self.iface.dlg,
                QCoreApplication.translate("initialisation","Erreur ..."),
                QCoreApplication.translate("initialisation","Choisissez un répertoire de sortie!"),
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
                )
        elif (self.pageInd == 2 and not self.contraintes_filled()) or (self.pageInd == 3 and not self.reclassification()) or (self.pageInd == 5 and not self.factors_filled()):
            self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()
        elif (self.pageInd == 2 and self.listContraintesNotReady == []) or (self.pageInd == 3 and self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.document().isEmpty()):
            self.pageInd = 5
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        elif self.pageInd == 5 and len(self.listFactorNotNormalized)== 0:
            self.pageInd = 8
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
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
                self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
                self.pageInd = 3
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
        return self.pageInd

    def update_listData(self,tbl,sb):
        # Row count
        spinbox_value = sb.value()
        tbl.setRowCount(spinbox_value)
        tbl.verticalHeader().setVisible(True)

        # Update list of input data
        if self.pageInd == 2:
            self.listContraintes = self.listContraintes[:spinbox_value]
            list_object = self.listContraintes
        else:
            self.listFactors = self.listFactors[:spinbox_value]
            self.iface.dlg.SB_NB_DATA_2.setValue(spinbox_value)
            list_object = self.listFactors

        for row in range(spinbox_value):
            # Initialise input widget
            name = QLineEdit()
            name.setFont(self.myFont)

            path = QLineEdit()
            path.setFont(self.myFont)
            path.setEnabled(False)
            path.setStyleSheet(
                "QLineEdit {background-color: rgb(255, 255, 255);")

            toolButton = QToolButton()
            toolButton.setText('...')

            checkbox = QCheckBox()

            # Handle items
            r = row
            name.textEdited.connect(
                lambda name=row, row=r: list_object[row].setname(name))
            checkbox.stateChanged.connect(
                lambda ready=row, row=r: list_object[row].setready(ready))
            toolButton.released.connect(
                lambda r=r: self.select_source_path(tbl,r))

            # Set inputData name, path, button, checkbox
            tbl.setCellWidget(row, 0, name)
            tbl.setCellWidget(row, 1, path)
            tbl.setCellWidget(row, 2, toolButton)
            tbl.setCellWidget(row, 3, checkbox)

             # If row added => Append list of inputData
            if row >= len(list_object):
                type = "contraint" if self.pageInd == 2 else "factor"
                inputLayer = InputLayer(path.text())
                inputObject = InputData(name.text(),inputLayer, 0, type)
                inputLayer.add_element(inputObject)
                list_object.append(inputObject)

            name.setText(list_object[row].name)
            path.setText(list_object[row].inputLayer.path)
            checkbox.setCheckState(list_object[row].ready)

        tbl.setStyleSheet(
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px;}")

    def select_source_path(self, tbl, row):
        path, _filter = QFileDialog.getOpenFileName(
            tbl, QCoreApplication.translate("initialisation","Choisir un vecteur"), "", "*.shp")

        if self.pageInd == 2:
            inputData = self.listContraintes[row]
        else:
            inputData = self.listFactors[row]

        for inputLayer in self.list_inputLayers:
            # Search If inputLayer is in list of inputLayer
            if inputLayer.path == path:
                inputData.setinputLayer(inputLayer)
                inlineEdit = tbl.cellWidget(row, 1)
                inlineEdit.setText(path)

        # Else create new inputLayer
        if inputData.inputLayer.path != path:
            inputLayer = InputLayer(path)
            if inputLayer.isValid():
                inputData.setinputLayer(inputLayer)
                self.list_inputLayers.append(inputLayer)
                inlineEdit = tbl.cellWidget(row, 1)
                inlineEdit.setText(path)
            else:
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    QCoreApplication.translate("initialisation","Choisissez un fichier valide!"),
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                    )

        # Remove empty inputLayer from list
        for inputLayer in self.list_inputLayers:
            if len(inputLayer.elements) == 0:
                self.list_inputLayers.remove(inputLayer)

    def contraintes_filled(self):
        # Re-initialize the list of contrainte not ready
        self.listContraintesNotReady = self.listContraintes.copy()

        # Clear reclassification table
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.clear()
        nb_tab = self.iface.dlg.STACKED_WIDGET_RECLASS.count()
        for ind in range(nb_tab-1,-1,-1):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(ind)
            self.iface.dlg.STACKED_WIDGET_RECLASS.removeWidget(tab)

        # Start writing log
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        output_dir = self.iface.dlg.LE_OUTPUT_DIR.text()
        log = QCoreApplication.translate("initialisation","Traitement initié le {0}\n\nRépértoire de sortie: {1}\nFormat de sortie: SHP\n\nCONTRAINTES\nNombre de contraintes: {2}\n").format(now,output_dir,len(self.listContraintes))

        for i,contrainte in enumerate(self.listContraintes):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            if contrainte.ready == 2:
                self.listContraintesNotReady.remove(contrainte)
            else:
                # Initialize reclassification table
                self.display_classification_table(i,contrainte)
            if not contrainte.name or contrainte.inputLayer.path == "":
                msg_name = QCoreApplication.translate("initialisation","Saisir un nom pour la contrainte numéro")
                msg_path = QCoreApplication.translate("initialisation","Sélectionner une image pour la contrainte numéro")
                error_msg = msg_name if not contrainte.name else msg_path
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    f"{error_msg} {i+1}",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return False
            contrainte_status = QCoreApplication.translate("initialisation","PRÊTE") if contrainte.ready else QCoreApplication.translate("initialisation","NON PRÊTE")
            log += f"{contrainte.name}\t\t{contrainte.inputLayer.path}\t\t{contrainte_status}\n"

        log += "\n\n"
        self.log_path = os.path.join(output_dir,"full_mce_log.txt")
        with open(self.log_path,"w") as f:
            f.write(log)

        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)

        return True

    def factors_filled(self):
        # Re-initialize the list of factors
        self.listFactorNotNormalized = self.listFactors.copy()

        # Update standardization table
        self.display_standardization_table(len(self.listFactors))

        for row,factor in enumerate(self.listFactors):
            if not factor.name or factor.inputLayer.path == "":
                msg_name = QCoreApplication.translate("initialisation","Saisir un nom pour le facteur numéro")
                msg_path = QCoreApplication.translate("initialisation","Sélectionner une image pour le facteur numéro")
                error_msg = msg_name if not factor.name else msg_path
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    f"{error_msg} {row+1}",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return False

            if factor.ready == 2:
                self.listFactorNotNormalized.remove(factor)

            # Initialize standardization table
            self.add_standardization_row(row,factor)
            # contrainte_status = QCoreApplication.translate("initialisation","PRÊTE") if contrainte.ready else QCoreApplication.translate("initialisation","NON PRÊTE")
            # log += f"{contrainte.name}\t\t{contrainte.inputLayer.path}\t\t{contrainte_status}\n"

        # log += "\n\n"
        # self.log_path = os.path.join(output_dir,"full_mce_log.txt")
        # with open(self.log_path,"w") as f:
        #     f.write(log)

        return True

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
        tab.cellWidget(0,0).currentIndexChanged.connect(lambda: self.update_field_type(contrainte, tab))

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

        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        contrainte = self.listContraintesNotReady[i]

        if row == 0:
            contrainte_field_name = QComboBox()
            contrainte_field_name.setFont(self.myFont)
            tab.setCellWidget(0, 0, contrainte_field_name)
            for field in contrainte.inputLayer.vlayer.fields():
                contrainte_field_name.addItem(field.name())
            self.update_field_type(contrainte,tab)

        col = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget().columnCount()
        if col == 7:
            self.update_cell_to_editline(tab,row)
        else:
            self.update_cell_to_combobox(tab,row,contrainte.field_values)

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

    def update_field_type(self,contrainte,tab):
        field_name = tab.cellWidget(0,0).currentText()
        field_type = contrainte.setfield_type(field_name)
        tab.cellWidget(0,1).setText(field_type)

        if field_type == "String":
            tab.setColumnCount(4)
            header3 = QTableWidgetItem()
            header3.setText(QCoreApplication.translate("initialisation","Valeur Initiale"))
            tab.setHorizontalHeaderItem(3,header3)

            # Set Input field of column 4
            for row in range(tab.rowCount()):
                self.update_cell_to_combobox(tab,row,contrainte.field_values)

            tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            tab.setColumnCount(7)

            header3 = QTableWidgetItem()
            header3.setText(QCoreApplication.translate("initialisation","Début"))
            tab.setHorizontalHeaderItem(3,header3)

            header4 = QTableWidgetItem()
            header4.setText(QCoreApplication.translate("initialisation","Inclus"))
            tab.setHorizontalHeaderItem(4,header4)

            header5 = QTableWidgetItem()
            header5.setText(QCoreApplication.translate("initialisation","Fin"))
            tab.setHorizontalHeaderItem(5,header5)

            header6 = QTableWidgetItem()
            header6.setText(QCoreApplication.translate("initialisation","Inclus"))
            tab.setHorizontalHeaderItem(6,header6)

            for row in range(tab.rowCount()):
                self.update_cell_to_editline(tab,row)

            tab.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            tab.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)

    def update_cell_to_editline(self,tab,row):
        start_value = QLineEdit()
        start_value.setFont(self.myFont)
        tab.setCellWidget(row, 3, start_value)

        start_value_inclued = QCheckBox()
        start_value_inclued.setStyleSheet("margin-left:20%;")
        tab.setCellWidget(row,4, start_value_inclued)

        end_value = QLineEdit()
        end_value.setFont(self.myFont)
        tab.setCellWidget(row, 5, end_value)

        end_value_inclued = QCheckBox()
        end_value_inclued.setStyleSheet("margin-left:20%;");
        tab.setCellWidget(row,6, end_value_inclued)

    def update_cell_to_combobox(self,tab,row,values):
        start_value = QComboBox()
        start_value.setFont(self.myFont)
        tab.setCellWidget(row, 3, start_value)
        start_value.addItems(values)

        if row == len(values) - 1 :
            self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)
        elif row < len(values) - 1:
            self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(True)

    def reclassification(self):
        log = QCoreApplication.translate("initialisation","Paramètres de reclassification: \n")
        for i,contrainte in enumerate(self.listContraintesNotReady):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            classification = Classification(contrainte, tab, i, log)
            row, col = classification.correct_param()
            if col != -1 :
                error_msg = classification.raise_error_msg(row,col)
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    error_msg,
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                new_field_name = contrainte.field_name[:-2] + "Bl"
                contrainte.inputLayer.delete_new_field(new_field_name)
                return False

        # Show dialog Box
        reply = QMessageBox.question(
            self.iface.dlg,
            QCoreApplication.translate("initialisation","Question ..."),
            QCoreApplication.translate("initialisation","Voulez-vous tout de suite effectuer le traitement des contraintes ?"),
            buttons= QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            self.save_reclassified_layer_to_image()
        elif reply == QMessageBox.Cancel:
            return False

        # Write into log file
        self.save_reclassification_log_into_file(log)
        return True

    def save_reclassification_log_into_file(self,log):
        with open(self.log_path, "r") as input:
            with open(self.log_path + ".temp", "a") as output:
                # iterate all lines from file
                for line in input:
                    if not line.strip("\n").startswith(QCoreApplication.translate("initialisation",'Paramètres')):
                        # if line starts with substring 'Paramètres' then don't write it in temp file
                        output.write(line)
                    else:
                        break
                output.write(log)
        # replace file with original name
        os.replace(self.log_path + ".temp", self.log_path)

    def contraintes_not_ready_insame_iput(self, inputLayer):
        contraintes_not_ready = []
        for contrainte in inputLayer.elements:
            if contrainte in self.listContraintesNotReady:
                contraintes_not_ready.append(contrainte)
        return contraintes_not_ready

    def save_reclassified_layer_to_image(self):
        log = QCoreApplication.translate("initialisation","#######################################################\n\nNombre de contraintes en entrée: {0} ({1} à reclassifier)\n\nTraitement en cours. . .\n\n").format(len(self.listContraintes),len(self.listContraintesNotReady))
        for inputLayer in self.list_inputLayers:
            contraintes_not_ready = self.contraintes_not_ready_insame_iput(inputLayer)
            if contraintes_not_ready != []:
                output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(),inputLayer.name + "_bool.shp")
                inputLayer.setreclass_output(output_path)
                QgsVectorFileWriter.writeAsVectorFormat(inputLayer.vlayer, inputLayer.reclass_output, 'utf-8',driverName='ESRI Shapefile')
                for contrainte in contraintes_not_ready:
                    new_field_name = contrainte.field_name[:-2] + "Bl"
                    contrainte.inputLayer.delete_new_field(new_field_name)
                    log += QCoreApplication.translate("initialisation","Contrainte \"{0}\" :\nLecture des paramètres\t\t[OK]\nReclassification du champ \"{1}\" - Type \"{2}\"\t\t[OK]\nSauvegarde du résultat dans le fichier {3} \t\t[OK]\n\n").format(contrainte.name,contrainte.field_name,contrainte.field_type,inputLayer.reclass_output)
        log += QCoreApplication.translate("initialisation","Reclassification des contraintes terminés avec succès !\n\n#######################################################")
        self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.setText(log)
        self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.setFont(self.myFont)

    def initialise_variable_init(self):
        return self

    def initialise_initGui(self):
        self.iface.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            self.display_output_config()

            # On click on Suivant
            self.iface.dlg.BT_NEXT.pressed.connect(lambda: self.display_next_page())
            #On click on répertoire de sortie
            self.iface.dlg.BT_OUTPUT.clicked.connect(lambda: self.select_output_dir())
            #On click on Precedent
            self.iface.dlg.BT_PREVIOUS.clicked.connect(lambda: self.display_previous_page())

            self.init_classification_input()
            self.init_standardization_input()
