# -*- coding: utf-8 -*-
"""
/***************************************************************************
 full_mce
                                 A QGIS plugin
 Full Multicriteria Evaluation tool for Public Health
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-05-25
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Sarah FAMENONTSOA, Anthonio RAKOTOARISON, Fanjasoa RAKOTOMANANA
        email                : sfamenontsoa@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication,          Qt  # AddbySarah
from qgis.PyQt.QtGui import QIcon,                                              QFont  # AddbySarah
from qgis.PyQt.QtWidgets import QAction,                                        QVBoxLayout, QLabel  # AddbySarah
import pandas as pd  # AddbySarah


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .fullmce_dialog import full_mceDialog
import os.path


class full_mce:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'full_mce_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Full MCE for Public Health')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('full_mce', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/fullmce/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Full MCE for Public Health'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Full MCE for Public Health'),
                action)
            self.iface.removeToolBarIcon(action)

    def display(self, i):
        self.dlg.STACKED_WIDGET.setCurrentIndex(i)
        self.dlg.BT_PREVIOUS.setEnabled(True)
        self.dlg.BT_PREVIOUS.clicked.connect(
            lambda: self.dlg.STACKED_WIDGET.setCurrentIndex(i-1))

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Sélectionner le répertoire de sortie","", '*.shp')
        self.dlg.lineEdit.setText(filename)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = full_mceDialog()
            # On click on Suivant
            currentInd = self.dlg.STACKED_WIDGET.currentIndex()
            self.dlg.BT_NEXT.clicked.connect(
                lambda: self.display(currentInd+1))

        myFont = QFont()
        myFont.setBold(False)

        # Populate GB_DEVELOPER
        concepteurpath = os.path.join(self.plugin_dir, 'concepteur.csv')
        concepteurs = pd.read_csv(concepteurpath, sep=';')

        developper = " ".join(concepteurs.loc[0, ['prenom', 'nom']])
        labeldevelopper = QLabel(developper)
        labeldevelopper.setFont(myFont)
        # create groupbox layout
        devbox = QVBoxLayout()
        devbox.addWidget(labeldevelopper)
        self.dlg.GB_DEVELOPER.setLayout(devbox)

        # Populate GB_CONCEPTEUR
        conceptbox = QVBoxLayout()
        for i in concepteurs.index:
            concepteurtxt = " ".join(concepteurs.loc[i, ['prenom', 'nom']])
            concepteurtxt += " (" + concepteurs['email'][i]+")"
            labelconcepteur = QLabel(concepteurtxt)
            labelconcepteur.setFont(myFont)
            conceptbox.addWidget(labelconcepteur)
        self.dlg.GB_CONCEPTEUR.setLayout(conceptbox)

        # Populate TE_INFO
        self.dlg.TE_INFO.setText("Ce plugin a été spécialement dévéloppé par l'Institut Pasteur de Madagascar dans le cadre d'une étude sur la surveillance constante du paludisme et la détermination des zones prioritaires aux Campagnes d'Aspertion Intra-Domiciliaire (CAID) à Madagascar. Son utilisation est privilégié dans le domaine de la santé publique.")
        self.dlg.TE_INFO.setFont(myFont)

        # Populate LBL_ROHY
        self.dlg.LBL_ROHY.setText(
            "<a href=\"mailto:sfamenontsoa@pasteur.mg\">Suggestions ou Remarques</a>")
        self.dlg.LBL_ROHY.setTextFormat(Qt.RichText)
        self.dlg.LBL_ROHY.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.dlg.LBL_ROHY.setOpenExternalLinks(True)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
