import tabularDownloader as td
import daxQueries as daxQ
import functions as f

import os
import pandas as pd
import numpy as np
import warnings
import gc
import datetime

warnings.filterwarnings("ignore")
gc.collect()

print("### CrossPlan v 1.0 ###")
print("Witaj użytkowniku! W celu wyliczenia cross planu podążaj za instrukcjami.")

print("Ustaw ścieżkę folderu, gdzie będą trzymane wszystkie pliki csv:")
folderPath = f.setUpFolderPath()
salesDPFilePath = folderPath + "/SalesDP.csv"
salesHistoricalFilePath = folderPath + "/SalesHistorical.csv"
csFilePath = folderPath + "/CS.csv"
likeStoresFilePath = folderPath + "/LikeStores.csv"
outputFilePath = folderPath + "/crossplan.csv"

print("Sprawdzam, czy w folderze są wymagane pliki...")
f.checkEntryFiles(folderPath)

print("Czy chcesz pobrać planowaną sprzedaż DP? y/n:")
dowloadSalesDP = input()
while(dowloadSalesDP != "y" and dowloadSalesDP != "n"):
    print("Error! Złe wejście. Czy chcesz pobrać sprzedaż DP? y/n:")
    dowloadSalesDP = input()

print("Czy chcesz pobrać historyczną sprzedaż? y/n:")
dowloadSalesHisotrical = input()
while(dowloadSalesHisotrical != "y" and dowloadSalesHisotrical != "n"):
    print("Error! Złe wejście. Czy chcesz pobrać historyczną sprzedaż? y/n:")
    dowloadSalesHisotrical = input()

print("Ustaw początkowy i końcowy miesiąc, dla którego ma być wyliczony cross plan.")
startEndMonths = f.setStartEndMonths()

print("Podaj sprzed ilu lat ma być wzięta sprzedaż historyczna (liczba całkowita > 0):")
yearsToSubstract = ""
while(type(yearsToSubstract) != np.int):
    try:
        yearsToSubstract = int(input())
    except:
        print("Error! To nie jest liczba całkowita.")

print("Podaj liczbę pełnych tygodni sprzedaży (jeżeli 0, to wyliczy program):")
fullWeeksSales = int(input())

historicalStartEndMonths = f.setHistoricalStartEndMonths(startEndMonths, yearsToSubstract)
print("Pobieram listę historycznych tygodni...")
historicalWeeks = td.getWeekList(historicalStartEndMonths)

if fullWeeksSales == 0:
    fullWeeksSales = len(historicalWeeks)
print("Zakładam, że pełna sprzedaż jest liczona dla minimum", fullWeeksSales, "tygodni sprzedaży...")

if dowloadSalesDP == "y":
    print("Pobieram listę tygodni dla DP...")
    currentWeeks = td.getWeekList(startEndMonths)

    print("Pobieram planowaną sprzedaż DP do folderu...")
    if os.path.isfile(salesDPFilePath):
        os.remove(salesDPFilePath)

    for week in currentWeeks[0]:
        td.dataFrameFromTabular(daxQ.salesPlannedDP(week), salesDPFilePath)
    print("Sprzedaż DP została pobrana.")
elif dowloadSalesDP == "n":
    # TO DO
    print("TO DO!! walidacja pliku wejściowego.")

if dowloadSalesHisotrical == "y":
    print("Pobieram historyczną sprzedaż do folderu...")

    if os.path.isfile(salesHistoricalFilePath):
        os.remove(salesHistoricalFilePath)

    i = 1
    numberOfweeks = len(historicalWeeks)
    for week in historicalWeeks[0]:
        print("Pobierany tydzień", i, "/", numberOfweeks, ": ", week, ", czas:", datetime.datetime.now())
        td.dataFrameFromTabular(daxQ.salesHistorical(week), salesHistoricalFilePath)
        i = i +1

    print("Historyczna sprzedaż została pobrana.")
elif dowloadSalesHisotrical == "n":
    # TO DO
    print("TO DO!! walidacja pliku wejściowego.")

if os.path.isfile(outputFilePath):
    os.remove(outputFilePath)
############## Poniższy kod jest kopią rozwiązania Pawła Judka
cs = pd.read_csv(csFilePath, header=None, dtype={0: "category", 1: "category", 2: "float32"})
cs.columns = ["Store", "MonthCS", "SalesCS"]

salesDP = pd.read_csv(salesDPFilePath, header=None, dtype={3: "float32"})
salesDP.columns = ["Category", "MonthDP", "WeekDP", "SalesDP"]

salesHistorical = pd.read_csv(salesHistoricalFilePath,
                              header=None,
                              dtype={0: "category", 1: "category", 2: "category", 3: "category", 4: "float32"})
salesHistorical.columns = ["Category", "Store", "MonthLY", "WeekLY", "SalesLY"]
storeSalesWeeks = salesHistorical.groupby(["Store"])["WeekLY"].nunique().reset_index()
storesWithFullSales = storeSalesWeeks[storeSalesWeeks.WeekLY >= fullWeeksSales]['Store'].unique()
salesHistorical = salesHistorical[salesHistorical.Store.isin(storesWithFullSales)]

likeStores = pd.read_csv(likeStoresFilePath, header=None, dtype={0: "category", 1: "category"})
likeStores.columns = ["LStore", "Store"]
like_list = likeStores.LStore.unique().tolist()

like_sales = likeStores.merge(salesHistorical, left_on="LStore", right_on="Store", how="left")
like_sales.drop(columns=["LStore", "Store_y"], inplace=True)
like_sales.rename(columns={"Store_x": "Store"}, inplace=True)
like_sales = like_sales[["Category", "Store", "MonthLY", "WeekLY", "SalesLY"]]

salesHistorical = pd.concat([salesHistorical, like_sales])

csYear = startEndMonths[0][:5]
salesHistorical.MonthLY = salesHistorical.MonthLY.apply(lambda x: csYear + x[5:])
salesHistorical.WeekLY = salesHistorical.WeekLY.apply(lambda x: csYear + x[5:])
salesHistorical.rename(columns={"MonthLY": "MonthCS", "WeekLY": "WeekDP"}, inplace=True)

monthCSList = salesHistorical.MonthCS.unique()

historicalSalesChunks = {}
csChunks = {}
salesDPChunks = {}
print("Rozpoczynam chunkowanie...")
for month in monthCSList:
    historicalSalesChunks[month] = salesHistorical[salesHistorical.MonthCS == month]
    csChunks[month] = cs[cs.MonthCS == month]
    salesDPChunks[month] = salesDP[salesDP.MonthDP == month]

for month in monthCSList:
    print("Rozpoczynam kalkulację dla", month, "...")

    df = historicalSalesChunks[month].merge(csChunks[month], on=['Store', 'MonthCS'], how='left')
    df['cont'] = df['SalesLY'] / df.groupby(['Store', 'MonthCS'])['SalesLY'].transform('sum')
    df['SalesVDS'] = df['SalesCS'] * df['cont']
    del df["MonthCS"]
    del df["SalesLY"]
    del df["SalesCS"]
    del df["cont"]
    df['catsum'] = df.groupby('Category')['SalesVDS'].transform(sum)

    dp = salesDPChunks[month]
    dp["dpsplit"] = dp.groupby("Category")["SalesDP"].transform(sum) / dp.SalesDP.sum()
    dp['dp_week_contr'] = dp['SalesDP'] / dp.groupby('Category')['SalesDP'].transform(sum)
    dp.fillna(0, inplace=True)
    del dp["MonthDP"]
    del dp["SalesDP"]

    ds_merged = df.merge(dp, on=['Category', 'WeekDP'], copy=False)
    ds_merged['SalesVXS'] = ds_merged['dpsplit'] * ds_merged['SalesVDS'].sum() * ds_merged['SalesVDS'] / ds_merged['catsum']
    ds_merged['SalesVTP'] = ds_merged['dp_week_contr'] * ds_merged['dpsplit'] * ds_merged['SalesVDS'].sum()
    ds_merged['SalesVTS'] = ds_merged.groupby(['Store', 'Category'])['SalesVXS'].transform(sum)
    del ds_merged["SalesVDS"]
    del ds_merged["catsum"]
    del ds_merged["dpsplit"]
    del ds_merged["dp_week_contr"]
    ds_merged = ds_merged.astype({"SalesVXS": "float32", "SalesVTP": "float32", "SalesVTS": "float32"})

    print("Rozpoczynam xiter...")
    ds5 = f.xiter(5, ds1=ds_merged)

    ds5.to_csv(outputFilePath, header=False, index=False, mode="a+")
    print("Miesiąc", month, "zapisany do pliku", outputFilePath, ".")

print("Czy jesteś zadowolony z programu?: y/n")
input()
