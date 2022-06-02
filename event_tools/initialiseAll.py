from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import *
import os
from .contraintes import contraintes


class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        self.pageInd = self.iface.dlg.STACKED_WIDGET.currentIndex()

        concepteurpath = os.path.join(
            self.iface.plugin_dir, 'event_tools/concepteur.csv')
        self.concepteurs = []
        with open(concepteurpath, mode='r') as infile:
            self.concepteur_header = next(infile)
            for row in infile:
                data = row.rstrip('\n').split(";")
                self.concepteurs.append(data)

    def display_next_page(self):
        if self.pageInd == 1 and not self.iface.dlg.LE_OUTPUT_DIR.text():
            button = QMessageBox.critical(
                self.iface.dlg,
                "Erreur ...",
                "Choisissez un répertoire de sortie!",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
                )
            if button == QMessageBox.Ok:
                print("OK!")
        else:
            self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd + 1)
            self.iface.dlg.BT_PREVIOUS.setEnabled(True)
            self.pageInd += 1
        return self.pageInd

    def display_previous_page(self):
        self.pageInd -= 1
        if self.pageInd == 0:
            self.iface.dlg.BT_PREVIOUS.setEnabled(False)
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(self.pageInd)
        return self.pageInd

    def select_output_folder(self):
        foldername = QFileDialog.getExistingDirectory(
              self.iface.dlg, "Sélectionner le répertoire de sortie")
        self.iface.dlg.LE_OUTPUT_DIR.setText(foldername)
        self.iface.dlg.LE_OUTPUT_DIR.setFont(self.myFont)

    def display_plugin_info(self):
        # Populate GB_DEVELOPER
        devbox = QVBoxLayout()  # create groupbox layout
        developper = " ".join(self.concepteurs[0][1::-1])
        labeldevelopper = QLabel(developper)
        labeldevelopper.setFont(self.myFont)
        devbox.addWidget(labeldevelopper)
        self.iface.dlg.GB_DEVELOPER.setLayout(devbox)

        # Populate GB_CONCEPTEUR
        conceptbox = QVBoxLayout()  # create groupbox layout
        for concepteur in self.concepteurs:
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

    def initialise_variable_init(self):
        return self

    def initialise_initGui(self):
        self.iface.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            # On click on Suivant
            self.iface.dlg.BT_NEXT.clicked.connect(
                lambda: self.display_next_page())
            #On click on Precedent
            self.iface.dlg.BT_PREVIOUS.clicked.connect(
                lambda: self.display_previous_page())
            #On click on répertoire de sortie
            self.iface.dlg.BT_OUTPUT.clicked.connect(
                self.select_output_folder)
            self.display_plugin_info()
            contrainte = contraintes(self.iface, self.myFont)
