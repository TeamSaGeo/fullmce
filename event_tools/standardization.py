from qgis.PyQt.QtCore import QCoreApplication
import math

class Standardization:
    def __init__(self, factor, tab, row):
        self.factor = factor
        self.tab = tab
        self.row = row

    def correct_param (self):
        values,col = self.get_params()
        if col == -1:
            self.change_attributes_values(values)
            log = self.write_log(values)
            return True , log
        else:
            error_msg = self.error_msg(col)
            return False, error_msg

    def get_params(self):
        function = self.tab.cellWidget(self.row,1).currentIndex()
        direction = self.tab.cellWidget(self.row,2).currentIndex()
        values = [function, direction]

        for col in range(3,7):
            param = self.tab.cellWidget(self.row,col)
            # if col exist
            if param :
                try:
                    param_value = param.text()

                    # Change param value if equal "min" or "max"
                    if len(values) == 2 and param_value == "min":
                        param_value = min(self.factor.getfield_values())
                    if ((len(values) == 3 and direction != 2) or len(values) == 5)  and param_value == "max":
                        param_value = max(self.factor.getfield_values())

                    param_value = float(param_value)

                    # Return error if not column B > A and D > C and C > B (symetrique)
                    if len(values) >= 3:
                        if param_value <= values[-1]:
                            return values,col

                    values.append(param_value)
                except ValueError:
                    return values,col

        return values,-1

    def error_msg(self, col):
        col_name = self.tab.horizontalHeaderItem(col).text()
        order_error = ""
        if col >= 4:
            previous_col_name = self.tab.horizontalHeaderItem(col-1).text()
            order_error = QCoreApplication.translate("initialisation"," (strictement supérieure à celle de la colonne {0})").format(previous_col_name)
        return QCoreApplication.translate("initialisation","<b>Facteur \"{0}\":</b> Saisir une valeur en entier (ou réelle) valide à la colonne {1}{2}.").format(self.factor.name,col_name,order_error)

    def change_attributes_values(self, values):
        vlayer = self.factor.inputLayer.vlayer
        new_field_name = self.factor.field_name[:-2] + "Fz"
        new_field_idx = self.factor.inputLayer.add_new_field(new_field_name)

        function = values[0]
        direction = values[1]

        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[self.factor.field_idx]

            a = values [2]
            b = values [3]

            if direction == 0:
                new_value = self.descending (value, function, a, b)
            elif direction == 1:
                new_value = self.ascending(value, function, a, b)
            else:
                c = values [4]
                d = values [5]
                if value < c :
                    new_value = self.ascending(value, function, a, b)
                else:
                    new_value = self.descending (value, function, c, d)

            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        self.factor.inputLayer.setvlayer(vlayer)

    def fuzzy_function(self, x, dX, dW):
        return {
            0 : dX / dW,
            1 : math.pow(math.sin(dX / dW * (3.141592653589793 / 2)), 2.0),
            2 : 1.0 / (1.0 + math.pow((dW - dX) / dW, 2.0)),
            }[x]

    def ascending (self,value, function, a, b):
        if value < a:
            return 0
        elif value <= b:
            dX = value - a
            dW = b - a
            return self.fuzzy_function(function, dX, dW)
        else:
            return 1

    def descending (self, value, function, c, d):
        if value < c:
            return 1
        elif value <= d:
            dX = d - value
            dW = d - c
            return self.fuzzy_function(function, dX, dW)
        else:
            return 0

    def write_log(self,values):
        log = f"{self.row+1}) {self.factor.name}\t{self.factor.field_name}"
        for i,value in enumerate(values):
            value_index = value
            if i == 0 or i == 1:
                value = self.tab.cellWidget(self.row,i+1).currentText()
            log += f"\t{value}"
            if i == 1 and value_index == 0:
                log += "\t\t"
        log +="\n\n"
        return log
