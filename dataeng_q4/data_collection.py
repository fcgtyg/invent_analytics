import pandas as pd



class DataCollection:
    brands: pd.DataFrame
    products: pd.DataFrame
    stores: pd.DataFrame
    sales: pd.DataFrame

    def __init__(self, data_folder_path):
        self.__data_folder = data_folder_path
        
        self.brands = self.load("brand.csv")
        self.product = self.load("product.csv")
        self.stores = self.load("store.csv")
        self.sales = self.load("sales.csv")

    def load(self, path:str):
        return pd.read_csv(f"{self.__data_folder}/{path}")
    
