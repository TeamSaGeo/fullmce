from qgis.PyQt.QtCore import QCoreApplication, QDate , QDateTime
from datetime import datetime

class Classification:
    def __init__(self, contrainte, tab, ind):
        self.contrainte = contrainte
        self.tab = tab
        self.ind = ind

    def correct_param (self):
        if self.tab.rowCount() == 0:
            error_msg = self.error_msg(0,-1)
            return False, error_msg

        list_values,row,col = self.get_params()
        if row == -1 and col == -1:
            log = self.write_log(list_values)
            self.change_attributes_values(list_values)
            return True , log
        else:
            error_msg = self.error_msg(row,col)
            return False, error_msg

    def get_params(self):
        if self.contrainte.field_type == "String":
            return self.get_string_reclass_param()
        else:
            return self.get_number_reclass_param()

    def change_attributes_values(self,list_values):
        if self.contrainte.field_type == "String":
            vlayer = self.change_string_attributes_values(list_values)
        else:
            vlayer = self.change_number_attributes_values(list_values)
        self.contrainte.inputLayer.setvlayer(vlayer)

    def write_log(self,values):
        log = QCoreApplication.translate("classification","\n{0}) Contrainte \"{1}\": Champ {2} (Type {3})\n").format(self.ind+1,self.contrainte.name,self.contrainte.field_name,self.contrainte.field_type)
        for r in range(self.tab.rowCount()):
            log += f"\t{values[r][-1]}"
            if self.contrainte.field_type == "String":
                log += f"\t{values[r][0]}\n"
            else:
                if type(values[r][0]) == QDate :
                    values[r][0] = values[r][0].toString("yyyy-MM-dd")

                if type(values[r][2]) == QDate:
                    values[r][2] = values[r][2].toString("yyyy-MM-dd")

                start_inclus = "[" if values[r][1] else "]"
                end_inclus = "]" if values[r][3] else "["
                log += f"\t{start_inclus} {values[r][0]} , {values[r][2]} {end_inclus}\n"
        return log

    def error_msg (self,row,col):
        if col == -1:
            return QCoreApplication.translate("classification","Sélectionner la contrainte \"{0}\" afin d'ajouter les paramètres de reclassification").format(self.contrainte.name)
        else:
            error_msg = ""
            if col == 0:
                error_msg = QCoreApplication.translate("classification","en entier")
            elif col == 1:
                if self.contrainte.field_type == "String":
                    error_msg = QCoreApplication.translate("classification","Initiale (différente)")
                else:
                    error_msg = QCoreApplication.translate("classification","début")
            else:
                error_msg = QCoreApplication.translate("classification","finale (supérieure à la valeur Début)")
            return QCoreApplication.translate("classification","<b>Contrainte \"{0}\":</b> Saisir une valeur {1} valide à la ligne {2} .").format(self.contrainte.name,error_msg,row + 1)

    def get_number_reclass_param(self):
        list_values = []
        field_type = self.contrainte.field_type
        for row in range(self.tab.rowCount()):
            # get new value
            try:
                new_value = self.tab.cellWidget(row,0).text()
                if new_value == "null":
                    new_value == None
                else:
                    new_value = int(new_value)
            except ValueError:
                return list_values,row,0

            # get start_value
            try:
                start_value = self.tab.cellWidget(row,1).text()
                if start_value == "min":
                    start_value = self.contrainte.get_mimimum_value()
                # Convert end_value to Date or to Real
                if field_type != "Date":
                    start_value = float(start_value)
                elif type(start_value) == str:
                    start_value = datetime.strptime(start_value,'%Y-%m-%d').date()
                    if not start_value:
                        return list_values,row,1
            except ValueError:
                return list_values,row,1

            # Get end_value
            try:
                end_value = self.tab.cellWidget(row,3).text()
                if end_value == "max":
                    end_value = self.contrainte.get_maximum_value()
                # Convert end_value to Date or to Real
                if field_type != "Date":
                    end_value = float(end_value)
                elif type(end_value) == str:
                    end_value = datetime.strptime(end_value,'%Y-%m-%d').date()
                    if not end_value:
                        return list_values,row,3
            except ValueError:
                return list_values,row,3

            start_value_inclued = self.tab.cellWidget(row,2).isChecked()
            end_value_inclued = self.tab.cellWidget(row,4).isChecked()

            # Check if start value < end_value
            if start_value >= end_value:
                return list_values,row,3

            # Compare row interval to previous row
            for values in list_values:
                # Check if interval is in another interval
                if self.value_is_in_range(start_value,values):
                    if start_value != values[2] or start_value_inclued:
                        return list_values,row,1
                if self.value_is_in_range(end_value,values):
                    if end_value != values[0] or end_value_inclued:
                        return list_values,row,3
                # Check if interval contains another interval
                if start_value < values [0] and end_value >= values [2]:
                    return list_values,row,3

            # Save parameter to list
            row_values = [start_value, start_value_inclued, end_value, end_value_inclued, new_value]
            list_values.append(row_values)
        return list_values, -1, -1

    def get_string_reclass_param(self):
        list_values = []
        for row in range(self.tab.rowCount()):
            # get new value
            try:
                new_value = self.tab.cellWidget(row,0).text()
                if new_value == "null":
                    new_value == None
                else:
                    new_value = int(new_value)
            except ValueError:
                return list_values,row,0

            # get start_value
            start_value = self.tab.cellWidget(row,1).currentText()

            # check if initial value is duplicated
            for values in list_values:
                if start_value == values[0]:
                    return list_values,row,1

            row_values = [start_value,new_value]
            list_values.append(row_values)
        return list_values, -1, -1

    def change_string_attributes_values(self,values):
        vlayer = self.contrainte.inputLayer.vlayer
        # new_field_name = self.contrainte.field_name[:-2] + "Bl"
        new_field_name = self.contrainte.name + "Bl"
        new_field_idx = self.contrainte.inputLayer.add_new_field(new_field_name,"int")
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[self.contrainte.field_idx]

            # initialize iteration variable
            row = 0
            new_value = 0
            start_value = values[0][0]

            # Start condition
            while value != start_value and row < (self.tab.rowCount()-1):
                row += 1
                start_value = values[row][0]

            # Get new value
            if value == start_value:
                new_value = values[row][1]

            # Change Value
            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        return vlayer

    def change_number_attributes_values(self, values):
        vlayer = self.contrainte.inputLayer.vlayer
        # new_field_name = self.contrainte.field_name[:-2] + "Bl"
        new_field_name = self.contrainte.name + "Bl"
        new_field_idx = self.contrainte.inputLayer.add_new_field(new_field_name,"int")
        features = vlayer.getFeatures()
        vlayer.startEditing()
        for feat in features:
            # get layer value
            value = feat[self.contrainte.field_idx]

            # initialize iteration variable
            row = 0
            new_value = 0
            row_values = values[0]

            # Start condition
            while not self.value_is_in_range(value,row_values) and row < (self.tab.rowCount() - 1):
                row += 1
                row_values = values[row]

            # Get new value
            if self.value_is_in_range(value,row_values):
                new_value = values[row][4]

            vlayer.changeAttributeValue(feat.id(),new_field_idx, new_value)
        return vlayer

    def value_is_in_range(self,value,values):
        in_range = False
        start_value = values[0]
        start_value_inclued = values[1]
        end_value = values[2]
        end_value_inclued = values[3]

        if start_value_inclued and not end_value_inclued:
            in_range = value >= start_value and value < end_value
        elif start_value_inclued and end_value_inclued:
            in_range = value >= start_value and value <= end_value
        elif not start_value_inclued and end_value_inclued:
            in_range = value > start_value and value <= end_value
        elif not start_value_inclued and not end_value_inclued:
            in_range = value > start_value and value < end_value

        return in_range
