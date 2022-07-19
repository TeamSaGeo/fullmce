# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import *
from .inputData import InputData
from .inputLayer import InputLayer
from .classification import Classification
from . standardization import Standardization
from .weighting import Weigthing
from qgis.core import QgsVectorFileWriter
import os, csv
from datetime import datetime

class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()

        self.error_title = QCoreApplication.translate("initialisation","Erreur ...")

        # Initialize list of InputData
        self.listContraintes = []
        self.listContraintesNotReady = []
        self.listFactors = []
        self.listFactorsNotNormalized = []
        self.list_inputLayers = []

    def display_plugin_info(self):
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
        tbl.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        # Listen to spinbox
        sb.valueChanged.connect(lambda: self.update_listData(tbl,sb))

    def init_classification_input(self):
        name = QCoreApplication.translate("initialisation","Noms")
        path = QCoreApplication.translate("initialisation","Chemins")
        field = QCoreApplication.translate("initialisation","Champ")
        type = QCoreApplication.translate("initialisation","Type")
        ready = QCoreApplication.translate("initialisation","Prêts")
        columns = [name, path, "", field, type, ready]
        self.display_input_config(columns,self.iface.dlg.TBL_CONTRAINTE,self.iface.dlg.SB_NB_CONTRAINTE)

        # Listen to list of contraintes not ready
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.itemSelectionChanged.connect(
            lambda : self.select_contrainte_not_ready())
        # Listen to button add/delete row, reclassification contraintes
        self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.clicked.connect(
            lambda : self.delete_classification_row())
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.clicked.connect(
            lambda : self.add_classification_row())

    def init_standardization_input(self):
        # Get columns name
        tab = self.iface.dlg.TBL_CONTRAINTE
        columns =  [tab.horizontalHeaderItem(col).text() for col in range(tab.columnCount())]
        normalized = QCoreApplication.translate("initialisation","Normalisés")
        columns[-1] = normalized

        # Initialize standardization input table
        self.display_input_config(columns,self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

        # Initialize 3 input rows
        self.update_listData(self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

    def display_standardization_table(self):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
        name = QCoreApplication.translate("initialisation","Noms")
        fonctions = QCoreApplication.translate("initialisation","Fonctions")
        sens = QCoreApplication.translate("initialisation","Sens")
        columns = [name, fonctions, sens, "A", "B", "C", "D"]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        tab.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        tab.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        tab.verticalHeader().setVisible(True)
        tab.setRowCount(0)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px; padding: 4px;}")

    def display_classification_table(self, i, contrainte):
        ###---------Initialize List contrainte not ready Widget----------
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte.name)

        ###---------Initialize Tab Widget----------
        tab = QTableWidget()

        value = QCoreApplication.translate("initialisation","Nouvelle valeur")
        columns = [value]
        if contrainte.field_type == "String":
            init_value = QCoreApplication.translate("initialisation","Valeur Initiale")
            columns.append(init_value)
        else:
            start_value = QCoreApplication.translate("initialisation","Début")
            start_value_inclued =QCoreApplication.translate("initialisation","Inclus")
            end_value = QCoreApplication.translate("initialisation","Fin")
            end_value_inclued= QCoreApplication.translate("initialisation","Inclus")
            columns.extend([start_value, start_value_inclued,end_value,end_value_inclued])
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.verticalHeader().setVisible(False)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px;}")

        self.iface.dlg.STACKED_WIDGET_RECLASS.insertWidget(i,tab)
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)

        # Table will fit the screen horizontally
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_standardization_row(self,factor):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
        row = tab.rowCount()
        tab.setRowCount(row + 1)

        factor_name = QLineEdit()
        factor_name.setFont(self.myFont)
        factor_name.setText(factor.name)
        factor_name.setEnabled(False)
        factor_name.setStyleSheet("QLineEdit {color: black;}")
        tab.setCellWidget(row, 0, factor_name)

        factor_function = QComboBox()
        factor_function.setFont(self.myFont)
        linear = QCoreApplication.translate("initialisation","Linéaire")
        s_shaped = QCoreApplication.translate("initialisation","S-Shaped (Sigmoïdal)")
        j_shaped = QCoreApplication.translate("initialisation","J-Shaped")
        functions = [linear,s_shaped,j_shaped]
        factor_function.addItems(functions)
        tab.setCellWidget(row, 1, factor_function)

        factor_direction = QComboBox()
        factor_direction.setFont(self.myFont)
        descending = QCoreApplication.translate("initialisation","Décroissant")
        ascending = QCoreApplication.translate("initialisation","Croissant")
        symmetrical = QCoreApplication.translate("initialisation","Symétrique")
        direction = [descending,ascending,symmetrical]
        factor_direction.addItems(direction)
        tab.setCellWidget(row, 2, factor_direction)
        factor_direction.currentIndexChanged.connect(lambda ind=row: self.add_standardization_column(tab,row,ind))
        factor_direction.setCurrentIndex(1)

    def add_standardization_column(self,tab,row, ind):
        for col in range(3,7):
            factor_param = QLineEdit()
            factor_param.setFont(self.myFont)
            tab.setCellWidget(row, col, factor_param)
        if ind == 0:
            for col in range(3,5):
                tab.removeCellWidget(row, col)
        elif ind == 1:
            for col in range(5,7):
                tab.removeCellWidget(row, col)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px; padding: 4px;}")

    def init_weighting_table(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        columns = [factor.name for factor in self.listFactors]
        nb_columns = len(columns)
        tab.setColumnCount(nb_columns)
        tab.setHorizontalHeaderLabels(columns)
        tab.setRowCount(nb_columns)
        tab.setVerticalHeaderLabels(columns)
        tab.verticalHeader().setVisible(True)

        for row in range(nb_columns):
            for col in range (nb_columns):
                weight = QLineEdit()
                weight.setFont(self.myFont)
                weight.setAlignment(Qt.AlignCenter)
                tab.setCellWidget(row, col, weight)
                if row == col :
                    weight.setText("1")
                    weight.setEnabled(False)
                else:
                    weight.editingFinished.connect(lambda col=col, row=row : self.set_weighting_value(tab,row,col))
                weight.setStyleSheet("QLineEdit {color: black;}")

    def set_weighting_value(self,tab,row,col):
        self.iface.dlg.BT_NEXT.setEnabled(False)

        val = tab.cellWidget(row,col).text()
        sym = tab.cellWidget(col,row)
        if sym and val != "":
            try:
                val = float(val)
                if val < 0.111 or val > 9:
                    button = QMessageBox.information(
                        self.iface.dlg,
                        self.error_title,
                        QCoreApplication.translate("initialisation","La valeur en entrée doit être entre 0.1111 et 9."),
                        )
                    tab.cellWidget(row,col).setText('')
                else:
                    reverse_val = 1 / val
                    if round(reverse_val,2).is_integer():
                        decimals = 0
                    else:
                        decimals = 5
                    sym.setText("{0:.{1}f}".format(reverse_val, decimals))
            except ValueError:
                # Value is not numeric
                row_name = self.tab.verticalHeaderItem(row).text()
                col_name = self.tab.horizontalHeaderItem(col).text()
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    QCoreApplication.translate("initialisation","Veuillez saisir une valeur en entier ou réelle valide à la ligne {0} - colonne {1}!").format(row_name,col_name),
                    )

    def select_output_dir(self):
        foldername = QFileDialog.getExistingDirectory(
            self.iface.dlg, QCoreApplication.translate("initialisation","Veuillez sélectionner le répertoire de sortie"))
        self.iface.dlg.LE_OUTPUT_DIR.setText(foldername)
        self.iface.dlg.LE_OUTPUT_DIR.setFont(self.myFont)

    def load_log_file(self):
        with open(self.log_path, "r") as input:
            lines = ''.join(input.readlines())
            self.iface.dlg.TE_RUN_PROCESS.setText(lines)
            self.iface.dlg.TE_RUN_PROCESS.setFont(self.myFont)

    def display_next_page(self):
        if self.pageInd == 1 and not self.iface.dlg.LE_OUTPUT_DIR.text():
            button = QMessageBox.information(
                self.iface.dlg,
                self.error_title,
                QCoreApplication.translate("initialisation","Veuillez choisir un répertoire de sortie!"),
                )
        elif (self.pageInd == 2 and not self.contraintes_filled()) or (self.pageInd == 3 and not self.classification()) or (self.pageInd == 5 and not self.factors_filled()) or (self.pageInd == 6 and not self.standardization()):
            self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()
        elif (self.pageInd == 2 and self.listContraintesNotReady == []) or (self.pageInd == 3 and self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.document().isEmpty()):
            self.pageInd = 5
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        elif (self.pageInd == 5 and self.listFactorsNotNormalized == []) or (self.pageInd == 6 and self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.document().isEmpty()):
            self.pageInd = 8
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_NEXT.setEnabled(False)
        else:
            self.pageInd += 1
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
            if self.pageInd == 8 or self.pageInd == 9:
                self.iface.dlg.BT_NEXT.setEnabled(False)
                if self.pageInd == 9:
                    self.iface.dlg.BT_EXECUTE.setEnabled(True)

        return self.pageInd

    def display_previous_page(self):
        self.pageInd -= 1
        if self.pageInd == 0:
            self.iface.dlg.BT_PREVIOUS.setEnabled(False)
        elif self.pageInd == 3:
            self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
        elif self.pageInd == 4:
            if self.listContraintesNotReady == []:
                self.pageInd = 2
            else:
                self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
                self.pageInd = 3
        elif self.pageInd == 6:
            self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.clear()
        elif self.pageInd == 7:
            if self.listFactorsNotNormalized == []:
                self.pageInd = 5
            else:
                self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.clear()
                self.pageInd = 6
            self.iface.dlg.BT_NEXT.setEnabled(True)
        elif self.pageInd == 8:
            self.iface.dlg.BT_EXECUTE.setEnabled(False)
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
            list_object = self.listFactors

        for row in range(spinbox_value):
            # Initialise input widget
            name = QLineEdit()
            name.setFont(self.myFont)

            path = QLineEdit()
            path.setFont(self.myFont)
            path.setEnabled(False)
            path.setStyleSheet("QLineEdit {color: black;}")

            toolButton = QToolButton()
            toolButton.setText('...')

            field_name = QComboBox()
            field_name.setFont(self.myFont)

            field_type = QLineEdit()
            field_type.setFont(self.myFont)
            field_type.setEnabled(False)
            field_type.setStyleSheet("QLineEdit {color: black;}")

            checkbox = QCheckBox()

            # Set inputData name, path, button, checkbox
            tbl.setCellWidget(row, 0, name)
            tbl.setCellWidget(row, 1, path)
            tbl.setCellWidget(row, 2, toolButton)
            tbl.setCellWidget(row, 3, field_name)
            tbl.setCellWidget(row, 4, field_type)
            tbl.setCellWidget(row, 5, checkbox)
            tbl.setStyleSheet(
                "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 5px; padding-right: 5px;}")

             # If row added => Append list of inputData
            if row >= len(list_object):
                type = "contraint" if self.pageInd == 2 else "factor"
                inputLayer = InputLayer(path.text())
                inputObject = InputData(name.text(),inputLayer, 0, type)
                inputLayer.add_element(inputObject)
                list_object.append(inputObject)

            name.setText(list_object[row].name)
            path.setText(list_object[row].inputLayer.path)
            if path.text() != "" :
                self.update_field_items(list_object[row],field_name,field_type)
            checkbox.setCheckState(list_object[row].ready)

            # Handle items
            r = row
            name.textEdited.connect(
                lambda name=row, row=r: list_object[row].setname(name))
            toolButton.released.connect(
                lambda r=r: self.select_source_path(tbl,r))
            field_name.currentIndexChanged.connect(lambda ind=row, row=r: self.update_field_type_col(list_object[row],tbl,ind,row))
            checkbox.stateChanged.connect(
                lambda ready=row, row=r: list_object[row].setready(ready))

    def same_source_path (self, new_path):
        for inputLayer in self.list_inputLayers:
            if inputLayer.path == new_path:
                return inputLayer
        return None

    def select_source_path(self, tbl, row):
        path, _filter = QFileDialog.getOpenFileName(
            tbl, QCoreApplication.translate("initialisation","Veuillez choisir un vecteur"), "", "*.shp")

        if self.pageInd == 2:
            inputData = self.listContraintes[row]
        else:
            inputData = self.listFactors[row]

        # Search If inputLayer is in list of inputLayer
        inputLayer = self.same_source_path(path)
        if  inputLayer != None:
            # Update inputData attribute
            inputData.setinputLayer(inputLayer)
            # Update table field
            tbl.cellWidget(row, 1).setText(path)
            field_name = tbl.cellWidget(row, 3)
            field_type = tbl.cellWidget(row, 4)
            self.update_field_items(inputData,field_name,field_type)
        else:
            # Else create new inputLayer
            inputLayer = InputLayer(path)
            if inputLayer.isValid():
                # Update inputData attribute
                inputData.setinputLayer(inputLayer)
                # Update table field
                tbl.cellWidget(row, 1).setText(path)
                field_name = tbl.cellWidget(row, 3)
                field_type = tbl.cellWidget(row, 4)
                self.update_field_items(inputData,field_name,field_type)
                # Append list of inputLayers
                self.list_inputLayers.append(inputLayer)
            else:
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    QCoreApplication.translate("initialisation","Veuillez choisir un fichier valide!"),
                    )

        # Remove empty inputLayer from list
        for inputLayer in self.list_inputLayers:
            if len(inputLayer.elements) == 0:
                self.list_inputLayers.remove(inputLayer)

    def update_field_type_col(self,inputData,tab,idx,row):
        if idx != -1:
            inputData.setfield_idx(idx)
            tab.cellWidget(row,4).setText(inputData.field_type)

    def update_field_items(self,inputData,field_name,field_type):
        field_name.clear()
        for field in inputData.inputLayer.vlayer.fields():
            field_name.addItem(field.name())
        field_name.setCurrentIndex(inputData.field_idx)
        field_type.setText(inputData.field_type)

    def input_row_filled(self, element, i):
        if not element.name or element.inputLayer.path == "" or element.inputLayer.field_is_duplicated(element.type):
            type = "contrainte" if element.type == "contraint" else "facteur"
            msg_name = QCoreApplication.translate("initialisation","Veuillez saisir un nom pour le {0} n° {1}").format(type,i+1)
            msg_path = QCoreApplication.translate("initialisation","Veuillez sélectionner une image pour le {0} n° {1}").format(type,i+1)
            msg_field = QCoreApplication.translate("initialisation","Champ dupliqué! Veuillez choisir des champs différents pour les {0}s issus du même fichier source.").format(type)
            error_msg = msg_name if not element.name else msg_path if element.inputLayer.path == "" else msg_field
            button = QMessageBox.information(
                self.iface.dlg,
                self.error_title,
                f"{error_msg}",
            )
            return False
        else:
            return True

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
            if not self.input_row_filled(contrainte,i):
                return False

            if contrainte.ready == 2:
                self.listContraintesNotReady.remove(contrainte)
            else:
                # Initialize reclassification table
                self.display_classification_table(i,contrainte)

            contrainte_status = QCoreApplication.translate("initialisation","PRÊTE") if contrainte.ready else QCoreApplication.translate("initialisation","NON PRÊTE")
            log += f"{contrainte.name}\t\t{contrainte.inputLayer.path}\t{contrainte_status}\n"

        log += "\n"
        self.log_path = os.path.join(output_dir,"full_mce_log.txt")
        with open(self.log_path,"w") as f:
            f.write(log)

        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)

        return True

    def factors_filled(self):
        # Re-initialize the list of factors
        self.listFactorsNotNormalized = self.listFactors.copy()

        # Update standardization table
        self.display_standardization_table()
        first_line = QCoreApplication.translate("initialisation","FACTEURS")
        log = first_line
        log += QCoreApplication.translate("initialisation","\nNombre de facteurs: {0}\n").format(len(self.listFactors))

        for row,factor in enumerate(self.listFactors):
            if not self.input_row_filled(factor,row):
                return False

            if factor.field_type == "String":
                error_field = QCoreApplication.translate("initialisation","Le facteur n° {0} est de type \"String\". Voulez-vous reclassifier ce facteur ? Sinon, veuillez choisir un autre champ de type entier ou réelle.").format(row+1)
                reply = QMessageBox.question(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Question ..."),
                    f"{error_field}",
                    buttons=QMessageBox.Yes | QMessageBox.No,
                    defaultButton=QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    # Go to contrainte input table, list contrainte = 1
                    self.listContraintes.clear()
                    self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
                    self.pageInd = 2
                    self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
                    self.iface.dlg.SB_NB_CONTRAINTE.setValue(len(self.listContraintes))
                    self.listContraintes.append(factor)
                    self.iface.dlg.SB_NB_CONTRAINTE.setValue(len(self.listContraintes))
                return False

            if factor.ready == 2:
                self.listFactorsNotNormalized.remove(factor)
            else:
                self.add_standardization_row(factor)

            factor_status = QCoreApplication.translate("initialisation","NORMALISÉ") if factor.ready else QCoreApplication.translate("initialisation","NON NORMALISÉ")
            log += f"{factor.name}\t\t{factor.inputLayer.path}\t{factor_status}\n"

        self.iface.dlg.SB_NB_DATA_2.setValue(len(self.listFactorsNotNormalized))
        log += "\n"
        self.save_log(log,first_line)
        self.init_weighting_table()
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
            self.add_classification_row()
        elif row == 1:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)
        else:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(True)

        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(True)

    def add_classification_row(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row + 1)

        contrainte_val = QLineEdit()
        contrainte_val.setFont(self.myFont)
        tab.setCellWidget(row, 0, contrainte_val)

        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        contrainte = self.listContraintesNotReady[i]
        if contrainte.field_type == "String":
            field_values = contrainte.getfield_values()
            self.add_classification_string_row(tab,row, field_values)
        else:
            self.add_classification_number_row(tab,row)

        if row >= 1:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(True)

    def delete_classification_row(self):
        tab = self.iface.dlg.STACKED_WIDGET_RECLASS.currentWidget()
        row = tab.rowCount()
        tab.setRowCount(row - 1)
        if row == 2:
            self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.setEnabled(False)

    def add_classification_number_row(self,tab,row):
        start_value = QLineEdit()
        start_value.setFont(self.myFont)
        tab.setCellWidget(row, 1, start_value)

        start_value_inclued = QCheckBox()
        start_value_inclued.setStyleSheet("margin-left:50%;")
        tab.setCellWidget(row,2, start_value_inclued)

        end_value = QLineEdit()
        end_value.setFont(self.myFont)
        tab.setCellWidget(row, 3, end_value)

        end_value_inclued = QCheckBox()
        end_value_inclued.setStyleSheet("margin-left:50%;");
        tab.setCellWidget(row,4, end_value_inclued)

    def add_classification_string_row(self,tab,row,values):
        start_value = QComboBox()
        start_value.setFont(self.myFont)
        tab.setCellWidget(row, 1, start_value)
        start_value.addItems(values)

        if row == len(values) - 1 :
            self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)
        elif row < len(values) - 1:
            self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(True)

    def classification(self):
        first_line = QCoreApplication.translate("initialisation","Paramètres de reclassification: \n")
        log = first_line
        for i,contrainte in enumerate(self.listContraintesNotReady):
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            classification = Classification(contrainte, tab, i)
            correct, classification_log = classification.correct_param()
            if not correct :
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    classification_log,
                )
                new_field_name = contrainte.field_name[:-2] + "Bl"
                contrainte.inputLayer.delete_new_field(new_field_name)
                return False
            log += classification_log

        # Show dialog Box
        reply = QMessageBox.question(
            self.iface.dlg,
            QCoreApplication.translate("initialisation","Question ..."),
            QCoreApplication.translate("initialisation","Voulez-vous tout de suite effectuer le traitement des contraintes ?"),
            buttons= QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            self.save_layer_into_file()
        elif reply == QMessageBox.Cancel:
            return False

        # Write into log file
        self.save_log(log,first_line)
        return True

    def standardization(self):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
        first_line = QCoreApplication.translate("initialisation","Paramètres de standardisation:")
        log = first_line
        log += QCoreApplication.translate("initialisation","\nFacteur\tChamp\tFonction\tDirection")
        log += "\tA\tB\tC\tD\n-----------------------------------------------------------------------------------------------\n"
        for row,factor in enumerate(self.listFactorsNotNormalized):
            standardization = Standardization(factor,tab,row)
            correct, standardization_log = standardization.correct_param()
            if not correct :
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    standardization_log,
                )
                return False
            log += standardization_log
        # Show dialog Box
        reply = QMessageBox.question(
            self.iface.dlg,
            QCoreApplication.translate("initialisation","Question ..."),
            QCoreApplication.translate("initialisation","Voulez-vous tout de suite normaliser les facteurs ?"),
            buttons= QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            self.save_layer_into_file()
        elif reply == QMessageBox.Cancel:
            return False

        # Write into log file
        self.save_log(log,first_line)
        return True

    def weighting(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        weighting = Weigthing(tab)
        correct, log_params = weighting.correct_params()
        if correct:
            conRatio, log_weight = weighting.calculate_cr()
            self.iface.dlg.LBL_RC_VALUE.setText(f"RC = {conRatio}")
            if conRatio < 0.1:
                status = QCoreApplication.translate("initialisation","RC < 0.1. Matrice de jugement cohérent et acceptable!")
                self.iface.dlg.BT_NEXT.setEnabled(True)
                # Write into log file
                first_line = QCoreApplication.translate("initialisation","Matrice de jugement: ")
                log = f"{first_line}\n{log_params}\n\n{log_weight}\nRC = {conRatio}\t{status}\n\n"
                self.save_log(log,first_line)
                self.load_log_file()
            else:
                status = QCoreApplication.translate("initialisation","RC >= 0.1. Matrice de jugement non cohérent!\nVeuillez changer les valeurs saisies.")
                self.iface.dlg.BT_NEXT.setEnabled(False)
            self.iface.dlg.LBL_STATUT_MATRICE.setText(status)
        else:
            button = QMessageBox.information(
                self.iface.dlg,
                self.error_title,
                log,
                )
            self.iface.dlg.BT_NEXT.setEnabled(False)

    def save_matrix(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        output_path, ok = QFileDialog.getSaveFileName(
            self.iface.dlg, QCoreApplication.translate("initialisation","Sauvegarder la matrice de jugement"), self.iface.dlg.LE_OUTPUT_DIR.text(), 'CSV(*.csv)')

        nb_columns = range(tab.columnCount())
        headers = [tab.horizontalHeaderItem(column).text() for column in nb_columns]

        with open(output_path, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')
            writer.writerow(headers)
            for row in range(tab.rowCount()):
                writer.writerow(tab.cellWidget(row, column).text() for column in nb_columns)

    def load_matrix(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        input_path, _filter = QFileDialog.getOpenFileName(
            self.iface.dlg, QCoreApplication.translate("initialisation","Veuillez choisir le fichier CSV"), "", "*.csv")

        if _filter:
            with open(input_path) as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                for row, values in enumerate(reader):
                    for column, value in enumerate(values):
                        if row != column:
                            tab.cellWidget(row, column).setText(value)

    def save_log(self,log,first_line):
        with open(self.log_path, "r") as input:
            with open(self.log_path + ".temp", "a") as output:
                # # if line starts with first_line substring then don't write it in temp file
                for line in input:
                    if not line.strip("\n").startswith(first_line):
                        output.write(line)
                    else:
                        break
                output.write(log)
        # replace file with original name
        os.replace(self.log_path + ".temp", self.log_path)

    def contraintes_insame_input(self, inputLayer, list_contraintes):
        contraintes_same_input = []
        for contrainte in inputLayer.elements:
            if contrainte in list_contraintes:
                contraintes_same_input.append(contrainte)
        return contraintes_same_input

    def save_layer_into_file(self):
        if self.pageInd == 2:
            list_object = self.listContraintes
            list_object_not_ready = self.listContraintesNotReady
            object_type = QCoreApplication.translate("initialisation","contrainte")
            process_name = QCoreApplication.translate("initialisation","reclassifier")
            process = QCoreApplication.translate("initialisation","Reclassification")
            file_extension = "_bool.shp"
            field_extension = "Bl"
            text_edit = self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE
        else:
            list_object  = self.listFactors
            list_object_not_ready = self.listFactorsNotNormalized
            object_type = QCoreApplication.translate("initialisation","facteur")
            process_name = QCoreApplication.translate("initialisation","normaliser")
            process = QCoreApplication.translate("initialisation","Normalisation")
            file_extension = "_fuzz.shp"
            field_extension = "Fz"
            text_edit = self.iface.dlg.TE_RUN_PROCESS_NORMALISATION

        log = "#######################################################\n\n"
        log += QCoreApplication.translate("initialisation","Nombre de {0}s en entrée: {1} ({2} à {3})\n\nTraitement en cours. . .\n\n").format(object_type,len(list_object),len(list_object_not_ready),process_name)
        for inputLayer in self.list_inputLayers:
            object_not_ready = self.contraintes_insame_input(inputLayer,list_object_not_ready)
            if object_not_ready != []:
                output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(),inputLayer.name + file_extension)
                inputLayer.setreclass_output(output_path)
                QgsVectorFileWriter.writeAsVectorFormat(inputLayer.vlayer, inputLayer.reclass_output, 'utf-8',driverName='ESRI Shapefile')
                for object in object_not_ready:
                    new_field_name = object.field_name[:-2] + field_extension
                    object.inputLayer.delete_new_field(new_field_name)
                    log += QCoreApplication.translate("initialisation","{0} \"{1}\" :\nLecture des paramètres\t\t[OK]\n{2} du champ \"{3}\" - Type \"{4}\"\t\t[OK]\nSauvegarde du résultat dans le fichier {5} \t\t[OK]\n\n").format(object_type,object.name,process,object.field_name,object.field_type,inputLayer.reclass_output)
        log += QCoreApplication.translate("initialisation","{0} des {1}s terminés avec succès !").format(process,object_type)
        log += "\n\n#######################################################"
        text_edit.setText(log)
        text_edit.setFont(self.myFont)

    def remove_new_fields(self):
        for contrainte in self.listContraintesNotReady:
            new_field_name = contrainte.field_name[:-2] + "Bl"
            contrainte.inputLayer.delete_new_field(new_field_name)
        for factor in self.listFactorsNotNormalized:
            new_field_name = factor.field_name[:-2] + "Fz"
            factor.inputLayer.delete_new_field(new_field_name)

    def initialise_variable_init(self):
        return self

    def initialise_initGui(self):
        self.iface.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            self.display_plugin_info()

            # On click on Suivant
            self.iface.dlg.BT_NEXT.pressed.connect(lambda: self.display_next_page())
            # On click on répertoire de sortie
            self.iface.dlg.BT_OUTPUT.clicked.connect(lambda: self.select_output_dir())
            # On click on Precedent
            self.iface.dlg.BT_PREVIOUS.clicked.connect(lambda: self.display_previous_page())
            # On click on Cancel
            self.iface.dlg.BT_CANCEL.clicked.connect(lambda: self.remove_new_fields())
            # On click on Close
            self.iface.dlg.rejected.connect(lambda: self.remove_new_fields())

            self.init_classification_input()
            self.init_standardization_input()

            # On click on Tester
            self.iface.dlg.BT_TEST_JUGEMENT.clicked.connect(lambda : self.weighting())
            # On click on Enregistrer
            self.iface.dlg.BT_SAVE_MATRIX.clicked.connect(lambda: self.save_matrix())
            # On click on Importer
            self.iface.dlg.BT_LOAD_MATRIX.clicked.connect(lambda: self.load_matrix())
