from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils

class Aggregation:
    def __init__(self, factors, weights):
        self.factors = factors
        self.weights = weights

    def getexpression(self):
        expression = list()
        for i,factor in enumerate(self.factors):
            expression.append("\"" + factor.field_name + "\"" + '*' + str(round(self.weights[i],5)))
        return '+'.join(expression)

    def aggregate(self, list_inputLayers):
        expression = QgsExpression(self.getexpression())

        for inputLayer in list_inputLayers:
            processing.run('qgis:fieldcalculator',
               {"INPUT": inputLayer.path,
               "FIELD_NAME": 'WLC' ,
               "FIELD_TYPE": 2,
               "FIELD_LENGTH": 10,
               "FIELD_PRECISION": 3,
               "NEW_FIELD": True ,
               "FORMULA": expression,
               "OUTPUT": inputLayer.path + ".temp"})
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
