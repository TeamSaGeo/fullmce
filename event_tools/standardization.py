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
                    # if (col == 3 or col == 5 ) and param_value == "min":
                    #     param_value = min(self.factor.getfield_values())

                    param_value = float(param.text())

                    # Check if column B > A and D > C and C > B (symetrique)
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

            # if sigmoidal
            if function == 0:
                if direction == 0:
                    new_value = self.sigmoidal_descending(value, a, b)
                elif direction == 1:
                    new_value = self.sigmoidal_ascending(value, a, b)
                else:
                    c = values [4]
                    d = values [5]
                    if value < c :
                        new_value = self.sigmoidal_ascending(value, a, b)
                    else:
                        new_value = self.sigmoidal_descending(value, c, d)

            # if linear
            else:
                # if linear decreasing
                if direction == 0:
                    new_value = self.linear_descending(value, a, b)
                # if linear increasing
                elif direction == 1:
                    new_value = self.linear_ascending(value, a, b)
                else:
                    c = values [4]
                    d = values [5]
                    if value < c :
                        new_value = self.linear_ascending(value, a, b)
                    else:
                        new_value = self.linear_descending (value, c, d)

            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        self.factor.inputLayer.setvlayer(vlayer)

    def linear_descending (self, value, c, d):
        if value < c:
            return 1
        elif value <= d:
            return ((d - value) / (d - c))
        else:
            return 0

    def linear_ascending (self,value, a, b):
        if value < a:
            return 0
        elif value <= b:
            return ((value - a) / (b - a))
        else:
            return 1

    def sigmoidal_ascending (self,value, a, b):
        if value < a:
            return 0
        elif value <= b:
            c = a + (b - a) / 2
            return self.sigmoidal(value,-1,c)
        else:
            return 1

    def sigmoidal_descending (self, value, c, d):
        if value < c:
            return 1
        elif value <= d:
            c_exp = c + (d - c) / 2
            return self.sigmoidal(value,1,c_exp)
        else:
            return 0

    def sigmoidal (self,value, a, c):
        val_exp = a * (value - c)
        val_exp = round (val_exp,3)
        try:
            result = 1 / (1 + math.exp(val_exp))
        except OverflowError:
	        result = float('inf')
        return result

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
