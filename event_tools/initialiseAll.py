# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt, QVariant, QCoreApplication
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import *
from .contrainte import Contrainte
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsFeatureRequest, QgsField, QgsCoordinateTransformContext
import os, shutil
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

    def display_page3(self):
        name = QCoreApplication.translate("initialisation","Noms")
        path = QCoreApplication.translate("initialisation","Chemins")
        ready = QCoreApplication.translate("initialisation","Prêts")
        columns = [name, path, "", ready]
        self.iface.dlg.TBL_CONTRAINTE.setColumnCount(len(columns))
        self.iface.dlg.TBL_CONTRAINTE.setHorizontalHeaderLabels(columns)
        # Table will fit the screen horizontally
        self.iface.dlg.TBL_CONTRAINTE.setColumnWidth(0,150)
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

    def display_page4(self, i, contrainte):
        ###---------Initialize List contrainte not ready Widget----------
        self.iface.dlg.LV_CONTRAINTE_NOT_READY.addItem(contrainte.name)

        ###---------Initialize Tab Widget----------
        tab = QTableWidget()

        # Column count
        field = QCoreApplication.translate("initialisation","Champ")
        type = QCoreApplication.translate("initialisation","Type")
        value = QCoreApplication.translate("initialisation","Valeur")
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
        elif (self.pageInd == 2 and self.contraintes_filled()) or (self.pageInd == 3 and not self.reclassification()):
            self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()
        elif (self.pageInd == 2 and self.listContraintesNotReady == []) or (self.pageInd == 3 and self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.document().isEmpty()):
            self.pageInd = 5
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
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
            contrainte_path.setStyleSheet(
                "QLineEdit {background-color: rgb(255, 255, 255);")

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
            "QTableWidget::item {border: 0px; padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px;}")

    def select_contrainte_source_path(self, row):
        filename, _filter = QFileDialog.getOpenFileName(
            self.iface.dlg.TBL_CONTRAINTE, QCoreApplication.translate("initialisation","Choisir un vecteur"), "", "*.shp")
        contrainte = self.listContraintes[row]
        if contrainte.source_path_isvalid(filename):
            inlineEdit = self.iface.dlg.TBL_CONTRAINTE.cellWidget(row, 1)
            inlineEdit.setText(filename)
        else:
            button = QMessageBox.critical(
                self.iface.dlg,
                QCoreApplication.translate("initialisation","Erreur ..."),
                QCoreApplication.translate("initialisation","Choisissez un fichier valide!"),
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
                )

    def contraintes_filled(self):
        # Re-initialize the list of contrainte not ready and reclassification table
        self.listContraintesNotReady = self.listContraintes.copy()
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
                self.display_page4(i,contrainte)
            if not contrainte.name or not contrainte.source_path:
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
                return True
            contrainte_status = QCoreApplication.translate("initialisation","PRÊTE") if contrainte.ready else QCoreApplication.translate("initialisation","NON PRÊTE")
            log += f"{contrainte.name}\t\t{contrainte.source_path}\t\t{contrainte_status}\n"

        log += "\n\n"
        self.log_path = os.path.join(output_dir,"full_mce_log.txt")
        with open(self.log_path,"w") as f:
            f.write(log)

        self.iface.dlg.STACKED_WIDGET_RECLASS.setCurrentIndex(-1)
        self.iface.dlg.BT_ADD_ROW_CONTRAINTE.setEnabled(False)

        return False

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
        tab.cellWidget(0,0).currentIndexChanged.connect(lambda: self.update_field_type(contrainte.vlayer, tab))

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
            for field in contrainte.vlayer.fields():
                contrainte_field_name.addItem(field.name())
            self.update_field_type(contrainte.vlayer,tab)

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

    def update_field_type(self,vlayer,tab):
        field_name = tab.cellWidget(0,0).currentText()
        field_idx = vlayer.fields().indexOf(field_name)
        field_type = vlayer.fields().at(field_idx).typeName()
        tab.cellWidget(0,1).setText(field_type)

        # Update contrainte instance
        i = self.iface.dlg.LV_CONTRAINTE_NOT_READY.currentRow()
        contrainte = self.listContraintesNotReady[i]
        contrainte.setfield(field_name,field_type)

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

            tab.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            tab.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)

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
            # Get field name et field type
            tab = self.iface.dlg.STACKED_WIDGET_RECLASS.widget(i)
            try:
                field_name = tab.cellWidget(0,0).currentText()
            except (ValueError, AttributeError) as error:
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    QCoreApplication.translate("initialisation","Sélectionner la contrainte \"{0}\" pour choisir le champ à reclassifier").format(contrainte.name),
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                return False

            field_type = tab.cellWidget(0,1).text()
            vlayer = contrainte.vlayer
            field_idx = vlayer.fields().indexOf(field_name)
            log += QCoreApplication.translate("initialisation","{0}) Contrainte \"{1}\": Champ {2} (Type {3})\n").format(i+1,contrainte.name,contrainte.field_name,contrainte.field_type)

            row = -1
            col = -1

            if field_type == "String":
                vlayer,row,col = self.change_string_attributes_values(contrainte,tab)
            elif field_type == "Real" or field_type == "Integer":
                vlayer,row,col = self.change_number_attributes_values(contrainte,tab)
            elif field_type == "Date":
                vlayer,row,col = self.change_date_attributes_values(contrainte,tab)

            if row == -1 and col == -1:
                contrainte.setvlayer(vlayer)
                log = self.write_reclassification_log(log, tab, field_type)
            else:
                error_msg = QCoreApplication.translate("initialisation","en entier (ou réelle)") if col == 2 else QCoreApplication.translate("initialisation","Initiale/Début") if col == 3 else QCoreApplication.translate("initialisation","Finale (supérieure à la valeur Début)")
                button = QMessageBox.critical(
                    self.iface.dlg,
                    QCoreApplication.translate("initialisation","Erreur ..."),
                    QCoreApplication.translate("initialisation","Saisir <b>une valeur {0}</b> valide à la ligne {1} pour la contrainte <b>\"{2}\"</b>.").format(error_msg,row + 1,contrainte.name),
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                self.delete_new_field(contrainte)
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

    def write_reclassification_log(self, log, tab, field_type):
        for r in range(tab.rowCount()):
            log += f"\t{tab.cellWidget(r,2).text()}"
            if field_type == "String":
                log += f"\t{tab.cellWidget(r,3).currentText()}\n"
            else:
                start_inclus = "[" if tab.cellWidget(r,4).isChecked() else "]"
                end_inclus = "]" if tab.cellWidget(r,6).isChecked() else "["

                log += f"\t{start_inclus} {tab.cellWidget(r,3).text()} , {tab.cellWidget(r,5).text()} {end_inclus}\n"
        log +="\n"
        return log

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

    def save_reclassified_layer_to_image(self):
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        log = QCoreApplication.translate("initialisation","#######################################################\n\nNombre de contraintes en entrée: {0} ({1} à reclassifier)\n\nTraitement en cours. . .\n\n").format(len(self.listContraintes),len(self.listContraintesNotReady))
        for contrainte in self.listContraintesNotReady:
            name = contrainte.name
            output_path = os.path.join(self.iface.dlg.LE_OUTPUT_DIR.text(),contrainte.name + "_bool.shp")
            contrainte.setreclass_output(output_path)
            QgsVectorFileWriter.writeAsVectorFormatV2(contrainte.vlayer, contrainte.reclass_output, QgsCoordinateTransformContext(), options)
            self.delete_new_field(contrainte)
            log += QCoreApplication.translate("initialisation","Contrainte \"{0}\" :\nLecture des paramètres\t\t[OK]\nReclassification du champ \"{1}\" - Type \"{2}\"\t\t[OK]\nSauvegarde du résultat dans le fichier {3} \t\t[OK]\n\n").format(contrainte.name,contrainte.field_name,contrainte.field_type,contrainte.reclass_output)
        log += QCoreApplication.translate("initialisation","Reclassification des contraintes terminés avec succès !\n\n#######################################################")
        self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.setText(log)
        self.iface.dlg.TE_RUN_PROCESS_CONTRAINTE.setFont(self.myFont)

    def change_string_attributes_values(self,contrainte,tab):
        new_field_idx = self.add_new_field(contrainte)
        vlayer = contrainte.vlayer
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[contrainte.field_idx]

            # initialize iteration variable
            row = 0
            new_value = 0
            start_value = tab.cellWidget(0,3).currentText()
            if not start_value:
                return vlayer,row,3

            # Start condition
            while value != start_value and row < (tab.rowCount()-1):
                row += 1
                start_value = tab.cellWidget(row,3).currentText()
                if not start_value:
                    return vlayer,row,3

            # Get new value
            if value == start_value:
                try:
                    new_value = float(tab.cellWidget(row,2).text())
                except ValueError:
                    return vlayer,row,2

            # Change Value
            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        return vlayer,-1,-1

    def change_number_attributes_values(self,contrainte,tab):
        new_field_idx = self.add_new_field(contrainte)
        vlayer = contrainte.vlayer
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[contrainte.field_idx]

            # initialize iteration variable
            row = 0
            new_value = 0

            try:
                start_value = float(tab.cellWidget(0,3).text())
            except ValueError:
                return vlayer,row,3

            try:
                end_value = float(tab.cellWidget(0,5).text())
            except ValueError:
                return vlayer,row,5

            if start_value >= end_value:
                return vlayer,row,5

            start_value_inclued = tab.cellWidget(0,4).isChecked()
            end_value_inclued = tab.cellWidget(0,6).isChecked()

            # Start condition
            while self.attribute_is_outof_range(value,start_value,start_value_inclued,end_value,end_value_inclued) and row < (tab.rowCount() - 1):
                row += 1
                try:
                    start_value = float(tab.cellWidget(row,3).text())
                except ValueError:
                    return vlayer,row,3

                try:
                    end_value = float(tab.cellWidget(row,5).text())
                except ValueError:
                    return vlayer,row,5

                start_value_inclued = tab.cellWidget(row,4).isChecked()
                end_value_inclued = tab.cellWidget(row,6).isChecked()

            # Get new value
            if self.attribute_is_in_range(value,end_value,end_value_inclued):
                try:
                    new_value = float(tab.cellWidget(row,2).text())
                except ValueError:
                    return vlayer,row,2

            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
            # for row in range(tab.rowCount()):
            #     while value >= start_value and value < end_value:
            #         new_value = tab.cellWidget(row,2).text()
            #         vlayer.changeAttributeValue(feat.id(), field_idx, new_value)
        return vlayer,-1,-1

    def change_date_attributes_values(self,contrainte,tab):
        new_field_idx = self.add_new_field(contrainte)
        vlayer = contrainte.vlayer
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[contrainte.field_idx]

            # initialize iteration variable
            row = 0
            new_value = 0

            try:
                start_value = datetime.strptime(tab.cellWidget(0,3).text(),'%y-%m-%d')
            except ValueError:
                return vlayer,row,3

            try:
                end_value = datetime.strptime(tab.cellWidget(0,5).text(),'%y-%m-%d')
            except ValueError:
                return vlayer,row,5

            if start_value >= end_value:
                return vlayer,row,5

            start_value_inclued = tab.cellWidget(0,4).isChecked()
            end_value_inclued = tab.cellWidget(0,6).isChecked()

            # Start condition
            while self.attribute_is_outof_range(value,start_value,start_value_inclued,end_value,end_value_inclued) and row < (tab.rowCount() - 1):
                row += 1
                try:
                    start_value = datetime.strptime(tab.cellWidget(row,3).text(),'%y-%m-%d')
                except ValueError:
                    return vlayer,row,3

                try:
                    end_value = datetime.strptime(tab.cellWidget(row,5).text(),'%y-%m-%d')
                except ValueError:
                    return vlayer,row,5

                start_value_inclued = tab.cellWidget(row,4).isChecked()
                end_value_inclued = tab.cellWidget(row,6).isChecked()

            # Get new value
            if self.attribute_is_in_range(value,end_value,end_value_inclued):
                try:
                    new_value = float(tab.cellWidget(row,2).text())
                except ValueError:
                    return vlayer,row,2

            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        return vlayer,-1,-1

    def attribute_is_outof_range(self,value,start_value,start_value_inclued,end_value,end_value_inclued):
        out_of_range = False

        if start_value_inclued and not end_value_inclued:
            out_of_range = value < start_value or value >= end_value
        elif start_value_inclued and end_value_inclued:
            out_of_range = value < start_value or value > end_value
        elif not start_value_inclued and end_value_inclued:
            out_of_range = value <= start_value or value > end_value
        elif not start_value_inclued and not end_value_inclued:
            out_of_range = value <= start_value or value >= end_value

        return out_of_range

    def attribute_is_in_range(self,value,end_value,end_value_inclued):
        if end_value_inclued:
            return (value <= end_value)
        else:
            return (value < end_value)

    def add_new_field(self,contrainte):
        vlayer = contrainte.vlayer
        # Create new field
        vlayer_provider = vlayer.dataProvider()
        new_field_name = contrainte.field_name[:-2] + "Bl"
        new_field_idx = vlayer.fields().indexOf(new_field_name)
        if new_field_idx == -1:
            vlayer_provider.addAttributes([QgsField(new_field_name,QVariant.Double,"double",10,2)])
            vlayer.updateFields()
            new_field_idx = vlayer.fields().indexOf(new_field_name)
        return new_field_idx

    def delete_new_field(self,contrainte):
        new_field_idx = contrainte.vlayer.fields().indexOf(contrainte.field_name[:-2] + "Bl")
        contrainte.vlayer.dataProvider().deleteAttributes([new_field_idx])
        contrainte.vlayer.updateFields()

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
