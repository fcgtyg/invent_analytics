from data_collection import Feature, WMAPE

PATH = "/Users/fcgtyg/Development/invest_analytics_algo/dataeng_q4/input_data/data"
dataCol = Feature(PATH)
print(dataCol.features)


dataCol2 = WMAPE(PATH)

print(dataCol2.wmape)