from qgis.PyQt.QtCore import QCoreApplication

class Weigthing:
    def __init__(self, tab):
        self.tab = tab
        self.nb_columns = self.tab.columnCount()

    def sum_columns(self):
        sum_columns = []
        for col in range(self.nb_columns):
            sum = 0
            for row in range(self.nb_columns):
                sum += float(self.tab.cellWidget(row,col).text())
            sum_columns.append(sum)
        return sum_columns

    def layers_weight(self,sum_columns):
        weight = []
        for row in range(self.nb_columns):
            sum = 0
            for col in range(self.nb_columns):
                sum += float(self.tab.cellWidget(row,col).text()) / sum_columns[col]
            weight.append(sum / self.nb_columns)
        return weight

    def lambda_parameter(self,weight):
        self.nb_columns = self.tab.columnCount()

        # value * weight
        lambda_sum = 0
        for row in range(self.nb_columns):
            sum = 0
            for col in range(self.nb_columns):
                sum += float(self.tab.cellWidget(row,col).text()) * weight[col]
            lambda_sum += sum / weight[row]

        return (lambda_sum / self.nb_columns)

    def correct_params(self):
        for row in range(self.nb_columns):
            for col in range(self.nb_columns):
                try:
                    param = float(self.tab.cellWidget(row,col).text())
                except ValueError:
                    # Value is None
                    row_name = self.tab.verticalHeaderItem(row).text()
                    col_name = self.tab.horizontalHeaderItem(col).text()
                    error_msg = QCoreApplication.translate("initialisation","Veuillez saisir une valeur en entier ou réelle valide à la ligne <b<{0}</b> à la colonne <b>{1}</b>!").format(row_name,col_name)
                    return False, error_msg
        return True, None

    def calculate_cr(self):
        sum_columns = self.sum_columns()
        layers_weight = self.layers_weight(sum_columns)
        lambda_value = self.lambda_parameter(layers_weight)
        conIndex = ( lambda_value - self.nb_columns ) / (self.nb_columns - 1)
        randomConsIndex = {1:0.0 , 2:0.0 , 3:0.58 , 4:0.9 , 5:1.12 , 6:1.24 , 7:1.32 ,
                            8:1.41 , 9:1.45 , 10:1.49 , 11:1.51 , 12:1.48 , 13:1.56 , 14:1.57 , 15:1.59}
        conRatio = round(conIndex / randomConsIndex[self.nb_columns],2)
        return conRatio
