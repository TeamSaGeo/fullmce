from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsFeatureRequest
import processing, os
# from processing.tools import dataobjects


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
        return ("(" + sum + ") * " + product)

    def aggregate(self, inputpath, output_path):
        return processing.run('qgis:fieldcalculator',
            {"INPUT": inputpath,
            "FIELD_NAME": 'MCE_RESULT' ,
            "FIELD_TYPE": 0,
            "FIELD_LENGTH": 10,
            "FIELD_PRECISION": 3,
            "NEW_FIELD": True ,
            "FORMULA": self.getexpression(),
            "OUTPUT": output_path})

    def merge(self,paths, output_path):
        return processing.run("qgis:mergevectorlayers",
        {"LAYERS":paths,
        "OUTPUT": output_path})


    def joinbylocation(self,inputpath,joinpath,output_path):
        context = processing.tools.dataobjects.createContext()
        context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
        processing.run("qgis:joinattributesbylocation",
        {"INPUT":inputpath,
        "JOIN":joinpath,
        "PREDICATE":0,
        "METHOD":1,
        "OUTPUT":output_path}, context=context)
        # gsProcessingException
        # new_field_idx = inputLayer.add_new_field("WLC")
        # vlayer = inputLayer.vlayer
        # # context = QgsExpressionContext()
        # # context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(vlayer))
        #
        # vlayer.startEditing()
        # for feat in vlayer.getFeatures():
        #     # context.setFeature(feat)
        #     # feat ["WLC"] = expression.evaluate(context)
        #     value = float(2)
        #     vlayer.changeAttributeValue(feat.id(),new_field_idx,value)
        #     # vlayer.updateFeature(feat)
        # inputLayer.setvlayer(vlayer)

    # def aggregate(self):
    #     for inputLayer in self.inputLayers:
    #         vlayer = inputLayer.vlayer
    #         new_field_idx = inputLayer.add_new_field("WLC")
    #
    #         features = vlayer.getFeatures()
    #         vlayer.startEditing()
    #         for feat in features:
    #             s = 0
    #             for factor in self.factors:
    #                 # get layer value
    #                 value = feat[factor.field_idx]
    #                 s  += value * self.weight[i]
    #             vlayer.changeAttributeValue(feat.id(),new_field_idx, s)
    #         self.factor.inputLayer.setvlayer(vlayer)
