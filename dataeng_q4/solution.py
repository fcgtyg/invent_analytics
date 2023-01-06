import pandas as pd
import argparse
import os.path as path

class Feature:
    __brands: pd.DataFrame
    __products: pd.DataFrame
    __stores: pd.DataFrame
    __sales: pd.DataFrame
    __features: pd.DataFrame

    @property
    def brands(self):
        if self.__brands is None:
            self.__brands = self._load("brand.csv")
            self.__brands.rename(columns={"name": "brand", "id": "brand_id"}, inplace=True)
        return self.__brands
    @property
    def products(self):
        if self.__products is None:
            self.__products = self._load("product.csv")
            self.__products.rename(columns={"id": "product_id"}, inplace=True)
        return self.__products
    @property
    def stores(self):
        if self.__stores is None:
            self.__stores = self._load("store.csv")
        return self.__stores
    @property
    def sales(self):
        if self.__sales is None:
            self.__sales = self._load("sales.csv")
            self.__sales.rename(columns={"store": "store_id", "product": "product_id", "quantity": "sales_product"}, inplace="True")
        return self.__sales

    @property
    def features(self):
        if self.__features is None:
            self.__features = self.__calculate_features()
        return self.__features
    @features.setter
    def features(self, f):
        self.features = f
    

    def __init__(self, data_folder_path):
        self.__data_folder = data_folder_path
        self.__brands = None
        self.__products = None
        self.__stores = None
        self.__sales = None
        self.__features = None
    

    def _load(self, path:str):
        return pd.read_csv(f"{self.__data_folder}/{path}")

    
    def _product_feature_calc(self):
        product_brand_df = self.products.merge(self.brands, on="brand")
        sales_w_brand_id = self.sales.merge(product_brand_df, on="product_id")
        group_by = sales_w_brand_id.groupby(["store_id", "product_id"])
        ma7_p = group_by["sales_product"].transform(lambda d: d.rolling(7, closed="left").mean())
        lag7_p = group_by.shift(periods=7)["sales_product"]

        product_feature_df = pd.DataFrame()
        product_feature_df["product_id"] = self.sales["product_id"]
        product_feature_df["brand_id"] = sales_w_brand_id["brand_id"]
        product_feature_df["MA7_P"] = ma7_p
        product_feature_df["LAG7_P"] = lag7_p

        return product_feature_df

    def _brand_features_calc(self):
        product_brand_df = self.products.merge(self.brands, on="brand")
        sales_product_brand = self.sales.join(product_brand_df, on="product_id", rsuffix="_").drop(["product_id_", "name"], axis=1)

        group_by = sales_product_brand.groupby(["brand_id", "store_id", "date"])

        sales_product_sum_s = group_by["sales_product"].sum()
        ma7_b = sales_product_sum_s.transform(lambda d: d.rolling(7, closed="left").mean())
        lag7_b = sales_product_sum_s.shift(periods=7)

        brand_feature_df = ma7_b.to_frame().rename(columns={"sales_product":"MA7_B"})
        brand_feature_df["sales_brand"] = sales_product_sum_s
        brand_feature_df["LAG7_B"] = lag7_b.shift(periods=7)
        
        return brand_feature_df

    def _store_features_calc(self):
        store_sales_sum_date_s = self.sales.groupby(["store_id", "date"])["sales_product"].sum()
        ma7_s = store_sales_sum_date_s.transform(lambda d: d.rolling(7, closed="left").mean())
        lag7_s = store_sales_sum_date_s.shift(periods=7)
        
        store_feature_df = ma7_s.to_frame().rename(columns={"sales_product": "MA7_S"})
        store_feature_df["LAG7_S"] = lag7_s
        store_feature_df["sales_store"] = store_sales_sum_date_s

        return store_feature_df

    def __calculate_features(self):

        product_feature_df = self._product_feature_calc()
        sales_product_brand = self.sales.merge(product_feature_df, on="product_id")
        brand_feature_df = self._brand_features_calc()
        product_agg_df = sales_product_brand.merge(brand_feature_df, on=["brand_id", "store_id", "date"])
        store_feature_df = self._store_features_calc()
        
        features_df = product_agg_df.merge(store_feature_df, on=["store_id", "date"])
        features_df = features_df[["product_id","store_id","brand_id","date","sales_product","MA7_P","LAG7_P","sales_brand","MA7_B","LAG7_B","sales_store","MA7_S","LAG7_S"]]
        features_df.sort_values(by=["product_id","brand_id","store_id","date"], axis=0, inplace=True)
        return features_df

    def reset(self):
        self.__features = None
        return self.features

    def filter_features(self, min_date = "2021-01-08", max_date = "2021-05-30"):
        return self.features.where((self.features["date"]>=min_date) & (self.features["date"]<=max_date)).dropna(how="all")

    def save_features(self, min_date = "2021-01-08", max_date="2021-05-30", top=5):
        f_where = self.filter_features(min_date, max_date)
        f_where.head(top).to_csv("features.csv", index=False)

class WMAPE(Feature):
    __wmape: pd.DataFrame

    @property
    def wmape(self):
        if self.__wmape is None:
            self.__wmape = self.__calculate_wmape()
        return self.__wmape
    def __init__(self, data_folder_path):
        super().__init__(data_folder_path)
        self.__wmape = None

    def reset(self):
        super().reset()
        self.__wmape = None
        return self.wmape

    def __calculate_wmape(self, min_date = "2021-01-08", max_date="2021-05-30"):
        wmape = self.filter_features(min_date, max_date)
        
        wmape["ape_dividing"] = abs(wmape["sales_product"]-wmape["MA7_P"])
        ape_group = wmape.groupby(["product_id", "store_id", "brand_id"])[["ape_dividing", "sales_product"]]
        wmape_df_temp = ape_group.sum()
        wmape_df = wmape_df_temp["ape_dividing"]/wmape_df_temp["sales_product"]
        wmape_df.to_frame("WMAPE").sort_values(["WMAPE"], ascending=False)

        return wmape_df

    def save_wmape(self, min_date = "2021-01-08", max_date="2021-05-30", top=5):
        wmape = self.__calculate_wmape(min_date, max_date)
        wmape.head(top).to_csv("mapes.csv")



if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--min-date", help="start of the date range. type:str, format:'YYYY-MM-DD', default:'2021-01-08'")
    argParser.add_argument("--max-date", help="end of the date range. type:str, format:'YYYY-MM-DD', default:'2021-05-30'")
    argParser.add_argument("--top", help="number of rows in the WMAPE output. type:int, default:5")
    args = argParser.parse_args()
    min_date = args.min_date
    max_date= args.max_date
    if(min_date>max_date):
        raise Exception("max-date must be later than min-date")
    top = args.top
    
    try:
        top = int(top)
    except Exception:
        raise Exception("top has to be an integer")

    p = path.dirname(__file__)
    PATH = f"{p}/input_data/data"
    w = WMAPE(PATH)
    w.save_features(min_date, max_date, top)
    w.save_wmape(min_date, max_date, top)