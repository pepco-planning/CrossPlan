import os
import re
import numpy as np


def setUpFolderPath():
    folderPath = input()

    if not os.path.exists(folderPath):
        print("Error! Podany folder nie istnieje. Spróbuj ponownie.")
        folderPath = setUpFolderPath()

    return folderPath

def checkEntryFiles(folderPath):
    while(not(os.path.isfile(folderPath + "/LikeStores.csv"))):
        print("Error! Umieść w folderze plik LikeStores.csv i zatwierdź.")
        input()

    print("Plik LikeStores.csv jest.")

    while(not(os.path.isfile(folderPath + "/CS.csv"))):
        print("Error! Umieść w folderze plik CS.csv i zatwierdź.")
        input()

    print("Plik CS.csv jest.")

def setStartEndMonths():
    startEndMonths = []

    print("Podaj początkowy miesiąc (np. Y2021M01):")
    startEndMonths.append(input())

    print("Podaj końcowy miesiąc (np. Y2021M10):")
    startEndMonths.append(input())

    if not(re.match(r"Y[0-9][0-9][0-9][0-9]M[0-9][0-9]", startEndMonths[0])
           and re.match(r"Y[0-9][0-9][0-9][0-9]M[0-9][0-9]", startEndMonths[1])):
        print("Error! Podany format tygodni jest niepoprawny")
        setStartEndMonths()
    elif startEndMonths[0][:5] != startEndMonths[1][:5]:
        print("Error! Zakres dat musi pochodzić z tego samego roku planistycznego")
        setStartEndMonths()
    elif int(startEndMonths[0][1:5] + startEndMonths[0][6:8]) > int(startEndMonths[1][1:5] + startEndMonths[1][6:8]):
        print("Error! Początkowy miesiąc nie może być mniejszy od końcowego.")
        setStartEndMonths()

    return startEndMonths

def setHistoricalStartEndMonths(startEndWeeks, yearsToSubstract):
    historicalStartEndWeeks = []

    if yearsToSubstract > 0:
        historicalStartEndWeeks.append("Y" + str(int(startEndWeeks[0][1:5]) - yearsToSubstract) + "M" + startEndWeeks[0][6:8])
        historicalStartEndWeeks.append("Y" + str(int(startEndWeeks[1][1:5]) - yearsToSubstract) + "M" + startEndWeeks[1][6:8])
    else:
        print("Error! Podana liczba musi być liczbą całkowitą większą od 0.")
        historicalStartEndWeeks = setHistoricalStartEndMonths(yearsToSubstract)

    print("Historyczny zakres dat: ", historicalStartEndWeeks)
    return historicalStartEndWeeks

def xiter(num_iter, ds1, avg_acc=0.02, max_acc=0.05):
    for x in range(1, num_iter + 1):
        ds1['SalesVXS'] = ds1['SalesVXS'] / ds1.groupby(['WeekDP', 'Subclass'])['SalesVXS'].transform(sum) * ds1['SalesVTP']
        ds1['Sum1'] = ds1.groupby(['Subclass', 'Store'])['SalesVXS'].transform(sum)
        ds1['SalesVXS'] = ds1['SalesVXS'] / ds1['Sum1'] * ds1['SalesVTS']
        ds1['Sum2'] = ds1.groupby(['WeekDP', 'Subclass'])['SalesVXS'].transform(sum)
        acc1 = ds1[['Subclass', 'SalesVTP', 'Sum2']].drop_duplicates()
        acc1['accuracy'] = np.where(np.isinf(abs(1 - acc1['Sum2'] / acc1['SalesVTP']) == True), 0,
                                    abs(1 - acc1['Sum2'] / acc1['SalesVTP']))
        acc1_avg = acc1['accuracy'].mean()
        acc1_max = acc1['accuracy'].max()

        if acc1_avg <= avg_acc and acc1_max <= max_acc:
            break

    return ds1[['Subclass', 'Store', 'WeekDP', 'SalesVXS']]