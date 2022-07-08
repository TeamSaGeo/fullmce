from qgis.PyQt.QtCore import QCoreApplication

class Standardization:
    def __init__(self, factor, tab, row):
        self.factor = factor
        self.tab = tab
        self.row = row

    def correct_param (self):
        values,col = self.get_params()
        if col == -1:
            # self.change_attributes_values(values)
            # log = self.write_log(list_values)
            log = self.factor.name + " ok\n"
            return True , log
        else:
            error_msg = self.raise_error_msg(col)
            return False, error_msg

    def get_params(self):
        function = self.tab.cellWidget(self.row,1).currentIndex()
        direction = self.tab.cellWidget(self.row,2).currentIndex()
        values = [function,direction]

        for col in range(3,7):
            param = self.tab.cellWidget(self.row,col)
            if param :
                try:
                    param_value = float(param.text())
                    values.append(param_value)
                except ValueError:
                    return values,col

        return values,-1

    def raise_error_msg(self, col):
        col_name = self.tab.horizontalHeaderItem(col).text()
        return QCoreApplication.translate("initialisation","<b>Facteur \"{0}\":</b> Saisir une valeur en entier (ou réelle) valide à la colonne {1} .").format(self.factor.name,col)
