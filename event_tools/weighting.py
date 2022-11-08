from qgis.PyQt.QtCore import QCoreApplication

class Weigthing:
    def __init__(self, tab):
        self.tab = tab
        self.nb_columns = self.tab.rowCount()

    def sum_columns(self):
        sum_columns = []
        for col in range(self.nb_columns):
            sum = 0
            for row in range(self.nb_columns):
                sum += float(self.tab.cellWidget(row,col).text())
            sum_columns.append(sum)
        return sum_columns

    def layers_weight(self,sum_columns):
        log = QCoreApplication.translate("ponderation","Poids des facteurs:\n")
        weight = []
        for row in range(self.nb_columns):
            sum = 0
            for col in range(self.nb_columns):
                sum += float(self.tab.cellWidget(row,col).text()) / sum_columns[col]
            w = sum / self.nb_columns
            weight.append(w)
            self.tab.cellWidget(row,self.nb_columns).setText("{0:.5f}".format(w))
            log += f"{self.tab.horizontalHeaderItem(row).text()}:\t{round(w,5)}\n"
        return weight, log

    def lambda_parameter(self,weight):
        lambda_sum = 0
        for row in range(self.nb_columns):
            sum = 0
            for col in range(self.nb_columns):
                # value * weight
                sum += float(self.tab.cellWidget(row,col).text()) * weight[col]
            lambda_sum += sum / weight[row]

        return (lambda_sum / self.nb_columns)

    def correct_params(self):
        log = "\t"
        for column in range(self.nb_columns):
            log += f"{self.tab.horizontalHeaderItem(column).text()}\t"

        for row in range(self.nb_columns):
            row_name = self.tab.verticalHeaderItem(row).text()
            log += f"\n{row_name}\t"
            for col in range(self.nb_columns):
                try:
                    param = float(self.tab.cellWidget(row,col).text())
                    log += f"{param}\t"
                except ValueError:
                    # Value is None
                    col_name = self.tab.horizontalHeaderItem(col).text()
                    error_msg = QCoreApplication.translate("ponderation","Saisir une valeur en entier ou réelle valide à la ligne <b>{0}</b> à la colonne <b>{1}</b>!").format(row_name,col_name)
                    return False, error_msg
        self.calculate_cr()
        return True, log

    def calculate_cr(self):
        sum_columns = self.sum_columns()
        self.layers_weight, self.log_weight = self.layers_weight(sum_columns)
        lambda_value = self.lambda_parameter(self.layers_weight)
        conIndex = ( lambda_value - self.nb_columns ) / (self.nb_columns - 1)
        randomConsIndex = {1:0.0 , 2:0.0 , 3:0.58 , 4:0.9 , 5:1.12 , 6:1.24 , 7:1.32 ,
                            8:1.41 , 9:1.45 , 10:1.49 , 11:1.51 , 12:1.48 , 13:1.56 , 14:1.57 , 15:1.59}
        self.conRatio = round(conIndex / randomConsIndex[self.nb_columns],2)
