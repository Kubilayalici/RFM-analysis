##############################
# RFM ile Müşteri Segmentasyonu
##############################
# 1. İş Problemi
# 2. Veriyi Anlama
# 3. Veri Hazırlama
# 4. RFM Metriklerinin Hesaplanması
# 5. RFM Skorlarının Hesaplanması
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edlimesi
# 7. Tüm Sürecin Fonksiyonlaştırılması

import datetime as dt
import pandas as pd

pd.set_option("display.max_columns", None)
#pd.set_option("display.max_rows", None)
pd.set_option("display.float_format", lambda x : "%.3f" % x)


df_ = pd.read_excel(r"C:\Users\kkubi\OneDrive\Masaüstü\CRM\online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()

df.shape
df.isnull().sum()

# Eşsiz ürün sayısı?

df["Description"].nunique()

df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity":"sum"}).head()

df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity", ascending=False).head()

df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]

df.groupby("Invoice").agg({"TotalPrice":"sum"}).head()


############################3
# Veri Setini Hazırlama
#############################

df.shape

df.dropna(inplace=True)

df.isnull().sum()
df.describe().T

df = df[~df["Invoice"].str.contains("C", na=False)]


#################################################
#4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
#################################################

# Recency(Müşterinin Yeniliği, Sıcaklığı), Frequency(Müşterinin toplam satın alması), Monetary

df.head()

df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)

rfm = df.groupby("Customer ID").agg({
    "InvoiceDate": lambda date: (today_date - date.max()).days,
    "Invoice":lambda num: num.nunique(),
    "TotalPrice":lambda TotalPrice:TotalPrice.sum()
})

rfm.shape

rfm.columns = ["recency", "frequency", "monetary"]

rfm.head()

rfm.describe().T

rfm = rfm[rfm["monetary"]>0]

######################################
# RFM Skorlarının Hesaplanması (Calculating RFM Scores)
######################################

rfm["recency_score"] = pd.qcut(rfm["recency"],5, labels=[5,4,3,2,1])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"),5, labels=[1,2,3,4,5])

rfm["monetary_score"] = pd.qcut(rfm["monetary"],5, labels=[1,2,3,4,5])


rfm["RFM_SCORE"] =(rfm["recency_score"].astype(str)+rfm["frequency_score"].astype(str))


rfm.head()

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"].head()


#####################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
#####################################

# RFM isimlendirmesi

seg_map ={
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_Risk",
    r"[1-2]5": "cant_loose",
    r"3[1-2]": "about_to_sleep",
    r"33": "need_attention",
    r"[3-4][4-5]": "loyal_customer",
    r"41": "promising",
    r"51": "new_customer",
    r"[4-5][2-3]": "potential_loyalists",
    r"5[4-5]": "champions"
}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

rfm[["segment","recency","frequency","monetary"]].groupby("segment").agg(["mean","count"])

rfm[rfm["segment"]=="need_attention"].index

new_df = pd.DataFrame()

new_df["need_attention"] = rfm[rfm["segment"] == "need_attention"].index

new_df["need_attention"] = new_df["need_attention"].astype(int)

new_df.to_csv("need_attetion.csv")

rfm.to_csv("rfm.csv")


################################
# 7. Tüm Sürecin Fonksiyonlaştırılması
################################

def create_rfm(dataframe, csv=False):

    # Veriyi Hazırlama
    dataframe["TotalPrice"] = dataframe["Quantity"] + dataframe["Price"]
    dataframe.dropna(inplace= True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM Metriklerinin Hesaplanması
    today_date = dt.datetime(2011,12,11)
    rfm = dataframe.groupby("Customer ID").agg({"InvoiceDate":lambda date:(today_date-date.max()).days,
                                                "Invoice":lambda num: num.nunique(),
                                                "TotalPrice": lambda price:price.sum()})
    
    rfm.columns = ["recency", "frequency", "monetary"]
    rfm = rfm[rfm["monetary"]>0]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5,4,3,2,1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[5,4,3,2,1])

    #cltv_df skorlarının kategorik değere dönüştürülüp df'e eklenmesi
    rfm["RFM_SCORE"] =(rfm["recency_score"].astype(str)) + rfm["frequency_score"].astype(str)

    #Segmentlerin isimlendirilmesi
    seg_map ={
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_Risk",
    r"[1-2]5": "cant_loose",
    r"3[1-2]": "about_to_sleep",
    r"33": "need_attention",
    r"[3-4][4-5]": "loyal_customer",
    r"41": "promising",
    r"51": "new_customer",
    r"[4-5][2-3]": "potential_loyalists",
    r"5[4-5]": "champions"
    }

    rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)
    
    if csv:
        rfm.to_csv("rfm.csv")

    return rfm


df= df_.copy()


rfm_new = create_rfm(df,csv=True)