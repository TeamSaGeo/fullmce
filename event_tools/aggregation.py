from qgis.core import QgsFeatureRequest, QgsMessageLog
import processing

class Aggregation:
    def __init__(self, factors,contraintes, weights):
        self.factors = factors
        self.contraintes = contraintes
        self.weights = weights

    def getexpression(self):
        expression = list()
        for i,factor in enumerate(self.factors):
            expression.append("\"" + factor.field_name + "\"" + '*' + str(round(self.weights[i],5)))
        sum = '+'.join(expression)
        product = '*'.join([("\"" + contrainte.field_name + "\"") for contrainte in self.contraintes])
        return ("(" + sum + ") * " + (product if product else "1"))

    def aggregate(self, inputpath, expression, output_path):
        try:
            return processing.run('qgis:fieldcalculator',
            {"INPUT": inputpath,
            "FIELD_NAME": 'WLC' ,
            "FIELD_TYPE": 0,
            "FIELD_LENGTH": 10,
            "FIELD_PRECISION": 3,
            "NEW_FIELD": True ,
            "FORMULA": expression,
            "OUTPUT": output_path})
        except Exception as e:
            QgsMessageLog.logMessage(str(e), level=Qgis.Critical)
            return str(e)


    def joinbylocation(self,inputpath,joinpath,output_path):
        try:
            context = processing.tools.dataobjects.createContext()
            context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
            return processing.run("qgis:joinattributesbylocation",
            {"INPUT":inputpath,
            "JOIN":joinpath,
            "PREDICATE":0,
            "METHOD":1,
            "OUTPUT":output_path}, context=context)
        except Exception as e:
            QgsMessageLog.logMessage(str(e), level=Qgis.Critical)
            return str(e)
