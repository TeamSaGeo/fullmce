from qgis.PyQt.QtCore import QCoreApplication

class Classification:
    def __init__(self, contrainte, tab, ind, log):
        self.contrainte = contrainte
        self.tab = tab
        self.ind = ind
        self.log = log

    def correct_param (self):
        col = 0
        row = 0

        try:
            # Check if field name exist
            field_name = self.tab.cellWidget(row,col).currentText()
            list_values,row,col = self.get_params()
            if row == -1 and col == -1:
                self.change_attributes_values(list_values)
            return row, col

        except (ValueError, AttributeError) as error:
            return row, col

    def get_params(self):
        if self.contrainte.field_type == "String":
            return self.get_string_reclass_param()
        else:
            return self.get_number_reclass_param()

    def change_attributes_values(self,list_values):
        self.log += QCoreApplication.translate("initialisation","{0}) Contrainte \"{1}\": Champ {2} (Type {3})\n").format(self.ind+1,self.contrainte.name,self.contrainte.field_name,self.contrainte.field_type)
        if self.contrainte.field_type == "String":
            vlayer = self.change_string_attributes_values(list_values)
        else:
            vlayer = self.change_number_attributes_values(list_values)
        self.contrainte.inputLayer.setvlayer(vlayer)
        self.write_log()

    def write_log(self):
        for r in range(self.tab.rowCount()):
            self.log += f"\t{self.tab.cellWidget(r,2).text()}"
            if self.contrainte.field_type == "String":
                self.log += f"\t{self.tab.cellWidget(r,3).currentText()}\n"
            else:
                start_inclus = "[" if self.tab.cellWidget(r,4).isChecked() else "]"
                end_inclus = "]" if self.tab.cellWidget(r,6).isChecked() else "["

                self.log += f"\t{start_inclus} {self.tab.cellWidget(r,3).text()} , {self.tab.cellWidget(r,5).text()} {end_inclus}\n"
        self.log +="\n"

    def raise_error_msg (self,row,col):
        if col == 0:
            return QCoreApplication.translate("Sélectionner la contrainte \"{0}\" pour choisir le champ à reclassifier").format(self.contrainte.name)
        else:
            error_msg = ""
            if col == 2:
                error_msg = QCoreApplication.translate("initialisation","en entier (ou réelle)")
            elif col == 3:
                if self.contrainte.field_type == "String":
                    error_msg = QCoreApplication.translate("initialisation","Initiale (différente)")
                else:
                    error_msg = QCoreApplication.translate("initialisation","début")
            else:
                error_msg = QCoreApplication.translate("initialisation","finale (supérieure à la valeur Début)")
            return QCoreApplication.translate("initialisation","Contrainte <b>\"{0}\" - Ligne {1} </b>: Saisir <b>une valeur {2}</b> valide.").format(self.contrainte.name,row + 1,error_msg)

    def get_number_reclass_param(self):
        list_values = []
        field_type = self.contrainte.field_type
        for row in range(self.tab.rowCount()):
            # get new value
            try:
                new_value = float(self.tab.cellWidget(row,2).text())
            except ValueError:
                return list_values,row,2

            # get start_value
            try:
                start_value = self.tab.cellWidget(row,3).text()
                if start_value == "min":
                    start_value = min(self.contrainte.field_values)
                # Convert end_value to Date or to Real
                if field_type == "Date":
                    start_value = datetime.strptime(start_value,'%y-%m-%d')
                else:
                    start_value = float(start_value)
            except ValueError:
                return list_values,row,3

            # Get end_value
            try:
                end_value = self.tab.cellWidget(row,5).text()
                if end_value == "max":
                    end_value = max(self.contrainte.field_values)
                # Convert end_value to Date or to Real
                if field_type == "Date":
                    end_value = datetime.strptime(start_value,'%y-%m-%d')
                else:
                    end_value = float(end_value)
            except ValueError:
                return list_values,row,5

            start_value_inclued = self.tab.cellWidget(row,4).isChecked()
            end_value_inclued = self.tab.cellWidget(row,6).isChecked()

            # Check if start value < end_value
            if start_value >= end_value:
                return list_values,row,5

            # Compare row interval to previous row
            for values in list_values:
                # Check if interval is in another interval
                if self.value_is_in_range(start_value,values):
                    if start_value != values[2] or start_value_inclued:
                        return list_values,row,3
                if self.value_is_in_range(end_value,values):
                    if end_value != values[0] or end_value_inclued:
                        return list_values,row,5

                # Check if interval contains another interval
                if start_value < values [0] and end_value >= values [2]:
                    return list_values,row,5


            # Save parameter to list
            row_values = [start_value, start_value_inclued, end_value, end_value_inclued, new_value]
            list_values.append(row_values)
        return list_values, -1, -1

    def get_string_reclass_param(self):
        list_values = []
        for row in range(self.tab.rowCount()):
            # get new value
            try:
                new_value = float(self.tab.cellWidget(row,2).text())
            except ValueError:
                return vlayer,row,2

            # get start_value
            start_value = self.tab.cellWidget(row,3).currentText()

            # check if initial value is duplicated
            for values in list_values:
                if start_value == values[0]:
                    return list_values,row,3

            row_values = [start_value,new_value]
            list_values.append(row_values)

        return list_values, -1, -1

    def change_string_attributes_values(self,values):
        vlayer = self.contrainte.inputLayer.vlayer
        new_field_name = self.contrainte.field_name[:-2] + "Bl"
        new_field_idx = self.contrainte.inputLayer.add_new_field(new_field_name)
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
        new_field_name = self.contrainte.field_name[:-2] + "Bl"
        new_field_idx = self.contrainte.inputLayer.add_new_field(new_field_name)
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
