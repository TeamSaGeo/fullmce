# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QCoreApplication, QEventLoop, QTimer
from qgis.PyQt.QtGui import QFont, QTextCursor, QPixmap, QImage
from qgis.PyQt.QtWidgets import *
from qgis.core import QgsVectorFileWriter, QgsProcessingFeedback
from .inputData import InputData
from .inputLayer import InputLayer
from .classification import Classification
from .standardization import Standardization
from .weighting import Weigthing
from .aggregation import Aggregation
import os, csv, glob
from datetime import datetime

class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()

        self.error_title = QCoreApplication.translate("full_mce","Erreur ...")

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
        text = QCoreApplication.translate("full_mce","Ce plugin a été spécialement dévéloppé par l'Institut Pasteur de Madagascar dans le cadre d'une étude sur la surveillance constante du paludisme et la détermination des zones prioritaires aux Campagnes d'Aspertion Intra-Domiciliaire (CAID) à Madagascar. Son utilisation est privilégié dans le domaine de la santé publique.")
        self.iface.dlg.TE_INFO.setText(text)

        # self.iface.dlg.LBL_IPM.setPixmap(QPixmap(":/plugins/fullmce/images/ipm.png"))

        # Populate LBL_ROHY
        # self.iface.dlg.LBL_ROHY.setText(
        #       "<a href=\"mailto:sfamenontsoa@pasteur.mg\">" + QCoreApplication.translate("full_mce","Suggestions ou Remarques") + "</a>")
        # self.iface.dlg.LBL_ROHY.setTextFormat(Qt.RichText)
        # self.iface.dlg.LBL_ROHY.setTextInteractionFlags(
        #     Qt.TextBrowserInteraction)
        # self.iface.dlg.LBL_ROHY.setOpenExternalLinks(True)

    def init_inputData_table(self, columns, tbl, sb):
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        # Table will fit the screen horizontally
        tbl.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(5,QHeaderView.Interactive)
        tbl.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)

        # Listen to spinbox
        sb.valueChanged.connect(lambda: self.update_listData(tbl,sb))

    def init_classification_table(self):
        name = QCoreApplication.translate("full_mce","Nom")
        path = QCoreApplication.translate("full_mce","Répertoire")
        field = QCoreApplication.translate("full_mce","Champ")
        type = QCoreApplication.translate("full_mce","Type")
        scr = QCoreApplication.translate("full_mce","SCR")
        ready = QCoreApplication.translate("full_mce","Prêt")
        columns = [name, path, "", field, type, scr, ready]
        self.init_inputData_table(columns,self.iface.dlg.TBL_CONTRAINTE,self.iface.dlg.SB_NB_CONTRAINTE)

        # Listen to list of contraintes not ready
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.itemSelectionChanged.connect(
            lambda : self.select_contrainte_not_ready())
        # Listen to button add/delete row, reclassification contraintes
        self.iface.dlg.BT_DELETE_ROW_CONTRAINTE.clicked.connect(
            lambda : self.delete_classification_row())
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.clicked.connect(
            lambda : self.add_classification_row())

    def init_standardization_table(self):
        # Get columns name
        tab = self.iface.dlg.TBL_CONTRAINTE
        columns =  [tab.horizontalHeaderItem(col).text() for col in range(tab.columnCount())]
        normalized = QCoreApplication.translate("full_mce","Normalisé")
        columns[-1] = normalized

        # Initialize standardization input table
        self.init_inputData_table(columns,self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

        # Initialize 3 input rows
        self.update_listData(self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)

    def display_standardization_params(self):
        tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
        name = QCoreApplication.translate("full_mce","Nom")
        fonctions = QCoreApplication.translate("full_mce","Fonction")
        sens = QCoreApplication.translate("full_mce","Sens")
        inclued_value = QCoreApplication.translate("full_mce","Inclus")
        columns = [name, fonctions, sens, "A", inclued_value, "B", inclued_value, "C",inclued_value, "D", inclued_value]
        tab.setColumnCount(len(columns))
        tab.setHorizontalHeaderLabels(columns)
        tab.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for i in range(3,11):
            if (i % 2) == 0:
                tab.horizontalHeader().setSectionResizeMode(i,QHeaderView.ResizeToContents)
            else:
                tab.setColumnWidth(i,80)

        tab.verticalHeader().setVisible(True)
        tab.setRowCount(0)

    def display_classification_params(self, i, contrainte):
        ###---------Initialize List contrainte not ready Widget----------
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte.name)

        ###---------Initialize Tab Widget----------
        tab = QTableWidget()

        columns = [QCoreApplication.translate("full_mce","Nouvelle valeur")]
        if contrainte.field_type == "String":
            init_value = QCoreApplication.translate("full_mce","Valeur Initiale")
            columns.append(init_value)
        else:
            start_value = QCoreApplication.translate("full_mce","Début")
            start_value_inclued =QCoreApplication.translate("full_mce","Inclus")
            end_value = QCoreApplication.translate("full_mce","Fin")
            end_value_inclued= start_value_inclued
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
        linear = QCoreApplication.translate("full_mce","Linéaire")
        s_shaped = QCoreApplication.translate("full_mce","S-Shaped (Sigmoïdal)")
        # j_shaped = QCoreApplication.translate("full_mce","J-Shaped")
        # functions = [linear,s_shaped,j_shaped]
        functions = [linear,s_shaped]
        factor_function.addItems(functions)
        tab.setCellWidget(row, 1, factor_function)

        factor_direction = QComboBox()
        factor_direction.setFont(self.myFont)
        descending = QCoreApplication.translate("full_mce","Décroissant")
        ascending = QCoreApplication.translate("full_mce","Croissant")
        symmetrical = QCoreApplication.translate("full_mce","Symétrique")
        direction = [descending,ascending,symmetrical]
        factor_direction.addItems(direction)
        tab.setCellWidget(row, 2, factor_direction)
        factor_direction.currentIndexChanged.connect(lambda ind=row: self.add_standardization_column(tab,row,ind))
        factor_direction.setCurrentIndex(1)

    def add_standardization_column(self,tab,row, ind):
        for col in range(3,11):
            if (col % 2) != 0 :
                factor_param = QLineEdit()
                factor_param.setFont(self.myFont)
                tab.setCellWidget(row, col, factor_param)
            else:
                inclued_value = QCheckBox()
                tab.setCellWidget(row,col,inclued_value)
                inclued_value.setStyleSheet("margin-left:10%;");
        if ind == 0:
            for col in range(3,7):
                tab.removeCellWidget(row, col)
        elif ind == 1:
            for col in range(7,11):
                tab.removeCellWidget(row, col)
        tab.setStyleSheet(
            "QTableWidget::item {border: 0px; padding: 3px;}")

    def init_weighting_table(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        rows = [factor.name for factor in self.listFactors]
        nb_rows = len(rows)
        tab.setRowCount(nb_rows)
        tab.setVerticalHeaderLabels(rows)
        tab.setColumnCount(nb_rows + 1 )
        rows.append(QCoreApplication.translate("weighting","Poids"))
        tab.setHorizontalHeaderLabels(rows)
        tab.verticalHeader().setVisible(True)

        for row in range(nb_rows):
            for col in range (nb_rows + 1):
                # Initialize edit line input
                weight = QLineEdit()
                weight.setFont(self.myFont)
                weight.setAlignment(Qt.AlignCenter)
                tab.setCellWidget(row, col, weight)

                # Set text
                if row == col :
                    weight.setText("1")
                    weight.setEnabled(False)
                elif col == nb_rows:
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
                nbr_dec = str(val)[::-1].find('.')
                saaty_scale = [round(1/9,nbr_dec),round(1/7,nbr_dec),0.2,round(1/3,nbr_dec),1,3,5,7,9]
                if val not in saaty_scale:
                    button = QMessageBox.information(
                        self.iface.dlg,
                        self.error_title,
                        QCoreApplication.translate("full_mce","Choisir une valeur dans l'échelle de Saaty ci-dessous:") + "<p><img  src=\":/plugins/fullmce/images/saaty.png\"/></p>",
                        )
                    tab.cellWidget(row,col).setText('')
                else:
                    reverse_val = 1 / val
                    if reverse_val >= 1 or round(reverse_val,2).is_integer() :
                        decimals = 0
                    else:
                        decimals = 5
                    sym.setText("{0:.{1}f}".format(reverse_val, decimals))
            except ValueError:
                # Value is not numeric
                row_name = tab.verticalHeaderItem(row).text()
                col_name = tab.horizontalHeaderItem(col).text()
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    QCoreApplication.translate("full_mce","Saisir une valeur en entier ou réelle valide à la ligne {0} - colonne {1}!").format(row_name,col_name),
                    )

    def select_output_dir(self):
        foldername = QFileDialog.getExistingDirectory(
            self.iface.dlg, QCoreApplication.translate("full_mce","Sélectionner le répertoire de sortie"))
        self.iface.dlg.LE_OUTPUT_DIR.setText(foldername)

    def load_log_file(self, text_edit):
        with open(self.log_path, "r") as input:
            lines = ''.join(input.readlines())
            text_edit.setText(lines)

    def display_next_page(self):
        if self.pageInd == 1 and not self.iface.dlg.LE_OUTPUT_DIR.text():
            button = QMessageBox.information(
                self.iface.dlg,
                self.error_title,
                QCoreApplication.translate("full_mce","Choisir un répertoire de sortie!"),
                )
        elif (self.pageInd == 2 and not self.contraintes_filled()) \
            or ((self.pageInd == 3 or self.pageInd == 6)and not self.run_process()) \
            or ((self.pageInd == 4 or self.pageInd == 7) and not self.continue_next_process()) \
            or (self.pageInd == 5 and not self.factors_filled()):
            self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()
        elif (self.pageInd == 2 and self.listContraintesNotReady == []) :
            self.pageInd = 5
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        elif (self.pageInd == 5 and self.listFactorsNotNormalized == []) \
            or (self.pageInd == 6 and self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.document().isEmpty()):
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

    def display_previous_page(self):
        self.pageInd -= 1
        if self.pageInd == 0:
            self.iface.dlg.BT_PREVIOUS.setEnabled(False)
        elif self.pageInd == 2 :
            self.update_listData(self.iface.dlg.TBL_CONTRAINTE,self.iface.dlg.SB_NB_CONTRAINTE)
        elif self.pageInd == 3:
            if self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.toPlainText().endswith("#"):
                self.pageInd = 2
                self.update_listData(self.iface.dlg.TBL_CONTRAINTE,self.iface.dlg.SB_NB_CONTRAINTE)
            self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
        elif self.pageInd == 4 and self.listContraintesNotReady == []:
            self.pageInd = 2
        elif self.pageInd == 5 :
            self.update_listData(self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)
        elif self.pageInd == 6:
            if self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.toPlainText().endswith("#"):
                self.pageInd = 5
                self.update_listData(self.iface.dlg.TBL_DATA_ENTREE,self.iface.dlg.SB_NB_DATA)
            self.iface.dlg.TE_RUN_PROCESS_NORMALISATION.clear()
            self.pageInd == 5
        elif self.pageInd == 7:
            if self.listFactorsNotNormalized == []:
                self.pageInd = 5
            self.iface.dlg.BT_NEXT.setEnabled(True)
        elif self.pageInd == 8:
            self.iface.dlg.BT_EXECUTE.setEnabled(False)
            exit = QCoreApplication.translate("aggregation","Annuler")
            self.iface.dlg.BT_CANCEL.setText(exit)
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)

    def update_listData(self,tbl,sb):
        # Row count
        spinbox_value = sb.value()
        tbl.setRowCount(spinbox_value)
        tbl.verticalHeader().setVisible(True)

        # Update list of input data
        if self.pageInd == 2 :
            self.listContraintes = self.listContraintes[:spinbox_value]
            list_object = self.listContraintes
        else:
            self.listFactors = self.listFactors[:spinbox_value]
            list_object = self.listFactors

        for row in range(spinbox_value):
            # Initialise input widget
            name = QLineEdit()
            name.setFont(self.myFont)
            name.setMaxLength(8)

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

            scr = QLineEdit()
            scr.setFont(self.myFont)
            scr.setEnabled(False)
            scr.setStyleSheet("QLineEdit {color: black;}")

            checkbox = QCheckBox()

            # Set inputData name, path, button, checkbox
            tbl.setCellWidget(row, 0, name)
            tbl.setCellWidget(row, 1, path)
            tbl.setCellWidget(row, 2, toolButton)
            tbl.setCellWidget(row, 3, field_name)
            tbl.setCellWidget(row, 4, field_type)
            tbl.setCellWidget(row, 5, scr)
            tbl.setCellWidget(row, 6, checkbox)
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
                self.update_field_items(list_object[row],field_name,field_type,scr)
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

    def update_row_param(self, inputData, inputLayer, tbl, row, path):
        # Update inputData attribute
        inputData.setinputLayer(inputLayer)
        # Update table field
        tbl.cellWidget(row, 1).setText(path)
        field_name = tbl.cellWidget(row, 3)
        field_type = tbl.cellWidget(row, 4)
        scr = tbl.cellWidget(row, 5)
        self.update_field_items(inputData,field_name,field_type,scr)

    def select_source_path(self, tbl, row):
        path, _filter = QFileDialog.getOpenFileName(
            tbl, QCoreApplication.translate("full_mce","Choisir un vecteur"), "", "*.shp")

        if self.pageInd == 2:
            inputData = self.listContraintes[row]
        else:
            inputData = self.listFactors[row]

        # Search If inputLayer is in list of inputLayer
        inputLayer = self.same_source_path(path)
        if  inputLayer != None:
            self.update_row_param(inputData,inputLayer,tbl,row,path)
        else:
            # Else create new inputLayer
            inputLayer = InputLayer(path)
            if inputLayer.isValid():
                self.update_row_param(inputData,inputLayer,tbl,row, path)
                self.list_inputLayers.append(inputLayer)
            else:
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    QCoreApplication.translate("full_mce","Choisir un fichier valide!"),
                    )

        # Remove empty inputLayer from list
        for inputLayer in self.list_inputLayers:
            if len(inputLayer.elements) == 0:
                self.list_inputLayers.remove(inputLayer)

    def update_field_type_col(self,inputData,tab,idx,row):
        if idx != -1:
            inputData.setfield_idx(idx)
            tab.cellWidget(row,4).setText(inputData.field_type)

    def update_field_items(self,inputData,field_name,field_type, scr):
        field_name.clear()
        for field in inputData.inputLayer.vlayer.fields():
            field_name.addItem(field.name())
        field_name.setCurrentIndex(inputData.field_idx)
        field_type.setText(inputData.field_type)
        scr.setText(inputData.inputLayer.vlayer.crs().description())

    def input_row_filled(self, element, i):
        if not element.name or element.inputLayer.path == "" or element.inputLayer.field_is_duplicated(element.type):
            type = "contrainte" if element.type == "contraint" else "facteur"
            msg_name = QCoreApplication.translate("full_mce","Saisir un nom pour le {0} n° {1}").format(type,i+1)
            msg_path = QCoreApplication.translate("full_mce","Sélectionner un vecteur pour le {0} n° {1}").format(type,i+1)
            msg_field = QCoreApplication.translate("full_mce","Champ dupliqué! Choisir des champs différents pour les {0}s issus du même fichier source.").format(type)
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
        log = QCoreApplication.translate("classification",
        "Traitement initié le {0}\n\nRépértoire de sortie: {1}\nFormat de sortie: SHP\n\n-----------CLASSIFICATION----------\nNombre de contraintes: {2}\n").format(now,output_dir,len(self.listContraintes))

        # For each listContraintes ...
        for i,contrainte in enumerate(self.listContraintes):
            # Check if each row is filled
            if not self.input_row_filled(contrainte,i):
                return False

            if contrainte.ready == 2:
                if contrainte.field_type == "String":
                    button = QMessageBox.information(
                        self.iface.dlg,
                        self.error_title,
                        QCoreApplication.translate("full_mce","Le contrainte <b>{0}</b> de type \"String\" ne devrait pas être \"Prêt\". Reclassifier ce contrainte.").format(contrainte.name)
                    )
                    return False
                self.listContraintesNotReady.remove(contrainte)
            else:
                # Initialize reclassification table
                self.display_classification_params(i,contrainte)

            contrainte_status = QCoreApplication.translate("classification","PRÊTE") if contrainte.ready else QCoreApplication.translate("full_mce","NON PRÊTE")
            log += f"{contrainte.name}    {contrainte.inputLayer.path}    {contrainte.field_name}    {contrainte_status}\n"

        log += "\n"
        now = datetime.now().strftime("%Y%m%d")
        self.log_path = os.path.join(output_dir,"fullmce_log"+ now + ".txt")
        with open(self.log_path,"w") as f:
            f.write(log)

        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)

        # Show dialog Box
        # Show dialog Box
        self.save_layer_into_new_file = self.get_reply(self.listContraintesNotReady)
        if self.save_layer_into_new_file == QMessageBox.Cancel:
            return False

        return True

    def factors_filled(self):
        # Re-initialize the list of factors
        self.listFactorsNotNormalized = self.listFactors.copy()

        # Update standardization table
        self.display_standardization_params()
        first_line = QCoreApplication.translate("normalisation","----------NORMALISATION----------")
        log = first_line
        log += QCoreApplication.translate("normalisation","\nNombre de facteurs: {0}\n").format(len(self.listFactors))

        list_string_factors =[]
        for row,factor in enumerate(self.listFactors):
            if not self.input_row_filled(factor,row):
                return False

            if factor.field_type == "String":
                list_string_factors.append(factor)

            if factor.ready == 2:
                if factor.field_type == "Date" or factor.field_type == "Datetime":
                    button = QMessageBox.information(
                        self.iface.dlg,
                        self.error_title,
                        QCoreApplication.translate("full_mce","Le facteur <b>{0}</b> de type {1} ne devrait pas être \"Normalisé\". Normaliser ce facteur.").format(factor.name, factor.field_type)
                    )
                    return False
                self.listFactorsNotNormalized.remove(factor)
            else:
                self.add_standardization_row(factor)

            factor_status = QCoreApplication.translate("normalisation","NORMALISÉ") if factor.ready else QCoreApplication.translate("normalisation","NON NORMALISÉ")
            log += f"{factor.name}    {factor.inputLayer.path}    {factor.field_name}    {factor_status}\n"

        if len(list_string_factors) != 0:
            list_factors = ", ".join(f.name for f in list_string_factors )
            sing = QCoreApplication.translate("normalisation","Le facteur <b>{0}</b> est de type \"String\". Voulez-vous le reclassifier ?").format(list_factors)
            mult = QCoreApplication.translate("normalisation","Les facteurs <b>{0}</b> sont de type \"String\". Voulez-vous les reclassifier? ").format(list_factors)
            txt = sing if len(list_string_factors) == 1 else mult
            reply = QMessageBox.question(
                self.iface.dlg,
                QCoreApplication.translate("normalisation","Question ..."),
                QCoreApplication.translate("normalisation","{0} Sinon, choisir des champs de type entier ou réelle.").format(txt),
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                # Go to contrainte input table
                self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.clear()
                self.pageInd = 2
                self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
                # extend list contrainte
                for factor in list_string_factors:
                    factor.type = "contraint"
                self.listContraintes.extend(list_string_factors)
                self.iface.dlg.SB_NB_CONTRAINTE.setValue(len(self.listContraintes))
            return False

        self.iface.dlg.SB_NB_DATA_2.setValue(len(self.listFactorsNotNormalized))
        log += "\n"
        self.save_log(log,first_line)
        self.init_weighting_table()

        # Show dialog Box
        self.save_layer_into_new_file = self.get_reply(self.listFactorsNotNormalized)
        if self.save_layer_into_new_file == QMessageBox.Cancel:
            return False

        return True

    def get_reply (self, list):
        if len(list) > 0:
            reply = QMessageBox.question(
                self.iface.dlg,
                QCoreApplication.translate("full_mce","Question ..."),
                QCoreApplication.translate("full_mce","Voulez-vous sauvegarder les résultats dans des nouveaux fichiers?"),
                buttons= QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes,
            )
            return reply

    def select_contrainte_not_ready(self):
        # display selected containte tab
        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(i)

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

    def run_process(self):
        if self.pageInd == 3:
            first_line = QCoreApplication.translate("classification","Paramètres de reclassification:")
            log = first_line
            list_inputdata = self.listContraintesNotReady
            text_edit = self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE
        else:
            first_line = QCoreApplication.translate("normalisation","Paramètres de normalisation:")
            log = first_line + QCoreApplication.translate("normalisation","\nFacteur\tChamp\tFonction\tDirection")\
            + "\tA\tB\tC\tD\n----------------------------------------------------------------------------------------------------------------------------\n"
            list_inputdata = self.listFactorsNotNormalized
            text_edit = self.iface.dlg.TE_RUN_PROCESS_NORMALISATION

        for i,inputData in enumerate(list_inputdata):
            if inputData.type == "factor":
                tab = self.iface.dlg.TBL_DATA_STANDARDIZATION
                process = Standardization(inputData,tab,i)
            else:
                tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
                process = Classification(inputData, tab, i)

            correct, process_log = process.correct_param()
            if not correct :
                button = QMessageBox.information(
                    self.iface.dlg,
                    self.error_title,
                    process_log,
                )
                return False
            log += process_log + "\n"

        # Write log into log file
        self.save_log(log,first_line)
        self.load_log_file(text_edit)
        return True

    def continue_next_process(self):
        if self.pageInd == 4:
            text_edit = self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE
            question = QCoreApplication.translate("classification","reclassifier les contraintes")
        else:
            text_edit = self.iface.dlg.TE_RUN_PROCESS_NORMALISATION
            question = QCoreApplication.translate("normalisation","normaliser les facteurs")

        if text_edit.toPlainText().endswith("#"):
            return True
        else:
            self.save_layer_into_file(self.save_layer_into_new_file,text_edit)
            return False

    def weighting(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        self.weighting = Weigthing(tab)
        # Check if param are correct
        correct, log_params = self.weighting.correct_params()
        if correct:
            conRatio = self.weighting.conRatio
            self.iface.dlg.LBL_RC_VALUE.setText(f"RC = {conRatio}")
            if conRatio < 0.1:
                status = QCoreApplication.translate("weighting","RC < 0.1. Matrice de jugement cohérent et acceptable!")
                self.iface.dlg.BT_NEXT.setEnabled(True)
                # Write log into log file
                first_line = QCoreApplication.translate("weighting","----------PONDÉRATION----------")
                log = first_line
                log += QCoreApplication.translate("weighting","\nMatrice de jugement:")
                log += f"\n{log_params}\n\n{self.weighting.log_weight}\nRC = {conRatio}\t{status}\n\n"
                self.save_log(log,first_line)
                self.load_log_file(self.iface.dlg.TE_RUN_PROCESS)
            else:
                status = QCoreApplication.translate("weighting","RC >= 0.1. Matrice de jugement non cohérent!\nChanger les valeurs saisies.")
                self.iface.dlg.BT_NEXT.setEnabled(False)
            self.iface.dlg.LBL_STATUT_MATRICE.setText(status)
        else:
            button = QMessageBox.information(
                self.iface.dlg,
                self.error_title,
                log_params,)
            self.iface.dlg.BT_NEXT.setEnabled(False)

    def inputLayer_same_crs(self):
        maxInput = self.list_inputLayers[0]
        max = maxInput.vlayer.featureCount()
        crs = maxInput.vlayer.crs()
        for input in self.list_inputLayers[1:] :
            length = input.vlayer.featureCount()
            if input.vlayer.crs() != crs:
                return False, maxInput
            if max < length:
                max = length
                maxInput = input
        return True, maxInput

    def append_edittext(self, text):
        self.iface.dlg.TE_RUN_PROCESS.append(text)
        self.iface.dlg.TE_RUN_PROCESS.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()

    def aggregate(self):
        self.iface.dlg.BT_EXECUTE.setEnabled(False)
        self.iface.dlg.BT_PREVIOUS.setEnabled(False)
        self.iface.dlg.TE_RUN_PROCESS.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        first_line = QCoreApplication.translate("aggregation","----------AGRÉGATION----------")
        log = first_line

        # if all factors and all contraints in same crs
        test = QCoreApplication.translate("aggregation","Vérification des SCR des facteurs et des contraintes ...")
        self.append_edittext(first_line + "\n" + test )
        QApplication.setOverrideCursor(Qt.WaitCursor)
        inputs_same_crs, max_size_layer = self.inputLayer_same_crs()
        status = ""

        if inputs_same_crs:
            test_result = QCoreApplication.translate("aggregation","Super! Les couches sources sont du même type de géométrie.\n\nCréation du formule ...")
            self.append_edittext(test_result)

            # Get expression
            aggregation = Aggregation(self.listFactors, self.listContraintes, self.weighting.layers_weight)
            expression = aggregation.getexpression()
            formule = QCoreApplication.translate("aggregation","Formule = ") + expression
            self.append_edittext(formule)

            # Commit changes if modified max_size_layer not saved
            max_size_layer.vlayer.commitChanges()

            # if multiple layers, Join them by location
            input_path = max_size_layer.path
            fields = max_size_layer.vlayer.fields()
            if len(self.list_inputLayers) != 1:
                list_inputLayers = self.list_inputLayers.copy()
                list_inputLayers.remove(max_size_layer)
                for i,input in enumerate(list_inputLayers):
                    # Commit changes if modified layers not saved
                    input.vlayer.commitChanges()

                    # joinbylocation
                    #  ---- amboary ito sarah ------
                    # joinfields = list(set(fields.extend(input.vlayer.fields())))
                    result = aggregation.joinbylocation(input_path,input.path)
                    input_path = result['OUTPUT']
                    # fields = joinfields

            # Agregate
            self.append_edittext("\nLancement de l'agrégation ...")
            output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(),"resultat_final.shp" )
            result = aggregation.aggregate(input_path,expression,output_path)

            # Write result
            output_log = QCoreApplication.translate("aggregation","Sauvegarde du résultat dans ") + output_path
            self.append_edittext(output_log)
            log = "\n".join([log,formule,output_log])
            status = QCoreApplication.translate("aggregation","\nAgrégation terminée avec succès!")

        # else cannot aggregate
        else:
            status = QCoreApplication.translate("aggregation","\nAgrégation impossible! Les couches sources ne sont pas du même type de géométrie.")

        QApplication.restoreOverrideCursor()
        button = QMessageBox.information(self.iface.dlg,QCoreApplication.translate("aggregation","Résultat"),status,)
        self.append_edittext(status)
        self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        exit = QCoreApplication.translate("aggregation","Terminer")
        self.iface.dlg.BT_CANCEL.setText(exit)

        # Save log
        log += status
        self.save_log(log,first_line)

    def save_matrix(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        output_path, ok = QFileDialog.getSaveFileName(
            self.iface.dlg, QCoreApplication.translate("full_mce","Sauvegarder la matrice de jugement"), self.iface.dlg.LE_OUTPUT_DIR.text(), 'CSV(*.csv)')

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
            self.iface.dlg, QCoreApplication.translate("full_mce","Choisir le fichier CSV"), "", "*.csv")

        if _filter:
            with open(input_path) as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                for row, values in enumerate(reader):
                    for column, value in enumerate(values):
                        if row != column:
                            cellwidget = tab.cellWidget(row, column)
                            if cellwidget :
                                cellwidget.setText(value)
                            else:
                                break

    def clear_matrix(self):
        tab = self.iface.dlg.TBL_JUGEMENT
        for row in range(tab.rowCount()):
            for column in range(tab.columnCount()):
                if row != column :
                    tab.cellWidget(row, column).setText("")

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

    def objects_same_inputLayer(self, inputLayer, list_objects):
        objects_same_source = []
        for element in inputLayer.elements:
            if element in list_objects:
                objects_same_source.append(element)
        return objects_same_source

    def save_layer_into_file(self,reply,text_edit):
        if text_edit == self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE :
            list_object = self.listContraintes
            list_object_not_ready = self.listContraintesNotReady
            process = QCoreApplication.translate("classification","Reclassification")
            file_extension = "_bool.shp"
            field_extension = "Bl"
        else:
            list_object  = self.listFactors
            list_object_not_ready = self.listFactorsNotNormalized
            process = QCoreApplication.translate("normalisation","Normalisation")
            file_extension = "_fuzz.shp"
            field_extension = "Fz"

        text_edit.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        separator = "#######################################################"
        text_edit.append(separator + QCoreApplication.translate("full_mce","\nSauvegarde du résultat de:\n"))

        if reply == QMessageBox.Yes:
            for inputLayer in self.list_inputLayers:
                object_not_ready = self.objects_same_inputLayer(inputLayer,list_object_not_ready)
                if object_not_ready != []:
                    output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(),inputLayer.name + file_extension)
                    inputLayer.setreclass_output(output_path)
                    QgsVectorFileWriter.writeAsVectorFormat(inputLayer.vlayer, inputLayer.reclass_output, 'utf-8',driverName='ESRI Shapefile')
                    self.set_fields(object_not_ready,field_extension,inputLayer, text_edit,True)
                    # Remove temp fields
                    for object in object_not_ready:
                        inputLayer.delete_new_field(object.field_name)
                    # Set object new path
                    inputLayer.setpath(inputLayer.reclass_output)
                    inputLayer.isValid()
        else:
            self.set_fields(list_object_not_ready,field_extension,None, text_edit,False)
        text_edit.append(QCoreApplication.translate("full_mce","\n{0} terminées avec succès!").format(process))
        text_edit.append(separator)
        text_edit.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

    def set_fields(self,object_not_ready,field_extension, inputLayer, text_edit, new_output_path):
        for object in object_not_ready:
            # Add field extension
            new_field_name = object.name + field_extension
            # set field index
            if not new_output_path:
                inputLayer = object.inputLayer
                inputLayer.vlayer.commitChanges()

            object.setfield_idx(inputLayer.vlayer.fields().indexFromName(new_field_name))
            # Set Ready
            object.setready(2)
            # Set path
            path = inputLayer.reclass_output if new_output_path else object.inputLayer.path
            text_edit.append(QCoreApplication.translate("full_mce","\"{0}\" dans le champ {2} du fichier {1}\n").format(object.name,path, object.field_name))

    def remove_new_fields(self):
        QApplication.restoreOverrideCursor()
        if self.pageInd == 9:
            for contrainte in self.listContraintesNotReady:
                if not contrainte.inputLayer.path.endswith("_bool.shp"):
                    new_field_name = contrainte.name + "Bl"
                    contrainte.inputLayer.delete_new_field(new_field_name)
            for factor in self.listFactorsNotNormalized:
                if not factor.inputLayer.path.endswith("_fuzz.shp"):
                    new_field_name = factor.name + "Fz"
                    factor.inputLayer.delete_new_field(new_field_name)

    def reset_page(self):
        self.pageInd = 0
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)

    def initialise_variable_init(self):
        return self

    def initialise_initGui(self):
        self.iface.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            self.display_plugin_info()

            # On click on Reset
            self.iface.dlg.BT_RESET.clicked.connect(lambda : self.reset_page())
            # On click on Suivant
            self.iface.dlg.BT_NEXT.pressed.connect(lambda: self.display_next_page())
            # On click on Precedent
            self.iface.dlg.BT_PREVIOUS.clicked.connect(lambda: self.display_previous_page())
            # On click on Cancel
            # self.iface.dlg.BT_CANCEL.clicked.connect(lambda: self.remove_new_fields())
            # On click on Close
            self.iface.dlg.rejected.connect(lambda: self.remove_new_fields())

            # On click on répertoire de sortie
            self.iface.dlg.BT_OUTPUT.clicked.connect(lambda: self.select_output_dir())

            self.init_classification_table()
            self.init_standardization_table()

            # On click on Tester
            self.iface.dlg.BT_TEST_JUGEMENT.clicked.connect(self.weighting)
            # On click on Clear
            self.iface.dlg.BT_CLEAR.clicked.connect(lambda: self.clear_matrix())
            # On click on Enregistrer
            self.iface.dlg.BT_SAVE_MATRIX.clicked.connect(lambda: self.save_matrix())
            # On click on Importer
            self.iface.dlg.BT_LOAD_MATRIX.clicked.connect(lambda: self.load_matrix())
            # On click on RUN
            self.iface.dlg.BT_EXECUTE.clicked.connect(lambda : self.aggregate())
