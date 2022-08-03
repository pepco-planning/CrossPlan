# w path.append jest istotna ścieżka
# muszą się w niej znajdować 2 pliki:
# 1. Microsoft.AnalysisServices.AdomdClient.dll
# 2. Microsoft.AnalysisServices.dll
# Plików szukaj w C:\Windows\assembly\GAC_MSIL\Microsoft.AnalysisServices.(nazwa pliku)\

import pandas as pd
from sys import path
import daxQueries as daxQ
path.append(r"dll")
from pyadomd import Pyadomd

def dataFrameFromTabular(query, filePath):
    connStr = (r"Provider=MSOLAP;Data Source=LB-P-WE-AS;Catalog=PEPCODW")
    conn = Pyadomd(connStr)
    conn.open()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.arraysize = 5000

    df = pd.DataFrame(cursor.fetchall())
    df.to_csv(filePath, mode='a+', header=False, index=False)
    conn.close()

def getWeekList(startEndMonths):
    connStr = (r"Provider=MSOLAP;Data Source=LB-P-WE-AS;Catalog=PEPCODW")
    query = daxQ.weeks(startEndMonths)

    conn = Pyadomd(connStr)
    conn.open()
    cursor = conn.cursor()
    cursor.execute(query)

    df = pd.DataFrame(cursor.fetchall())

    return df