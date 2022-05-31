from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import QVBoxLayout, QLabel, QFileDialog
import os


class initialiseAll:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.myFont = QFont()
        self.myFont.setBold(False)

        concepteurpath = os.path.join(
            self.iface.plugin_dir, 'event_tools/concepteur.csv')
        self.concepteurs = []
        with open(concepteurpath, mode='r') as infile:
            self.concepteur_header = next(infile)
            for row in infile:
                data = row.rstrip('\n').split(";")
                self.concepteurs.append(data)

        # self.concepteurs = pd.read_csv(concepteurpath, sep=';')

    def display_next_page(self, i):
        self.iface.dlg.STACKED_WIDGET.setCurrentIndex(i)
        self.iface.dlg.BT_PREVIOUS.setEnabled(True)
        self.iface.dlg.BT_PREVIOUS.clicked.connect(
            lambda: self.iface.dlg.STACKED_WIDGET.setCurrentIndex(i-1))

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
              self.iface.dlg, "Sélectionner le répertoire de sortie", "", '*.shp')
        self.iface.dlg.LE_OUTPUT_DIR.setText(filename)
        self.iface.dlg.LE_OUTPUT_DIR.setFont(self.myFont)

    def display_plugin_info(self):
        # Populate GB_DEVELOPER
        devbox = QVBoxLayout()  # create groupbox layout
        #developper = " ".join(self.concepteurs.loc[0, ['prenom', 'nom']])
        developper = " ".join(self.concepteurs[0][1::-1])
        labeldevelopper = QLabel(developper)
        labeldevelopper.setFont(self.myFont)
        devbox.addWidget(labeldevelopper)
        self.iface.dlg.GB_DEVELOPER.setLayout(devbox)

        # Populate GB_CONCEPTEUR
        conceptbox = QVBoxLayout()
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
        self.first_start = True

    def initialise_run(self):
        if self.iface.first_start is True:
            self.iface.first_start = False
            # On click on Suivant
            currentInd = self.iface.dlg.STACKED_WIDGET.currentIndex()
            self.iface.dlg.BT_NEXT.clicked.connect(
                lambda: self.display_next_page(currentInd+1))
            self.iface.dlg.BT_OUTPUT.clicked.connect(
                self.select_output_file)
        self.display_plugin_info()
