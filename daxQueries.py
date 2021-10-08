def salesPlannedDP(daxWeek):
    return """
            EVALUATE
            SELECTCOLUMNS(
            FILTER(
            SUMMARIZECOLUMNS(
            'Product Hierarchy PRH'[PRH Category ID],
            'Planning Calendar PCAL'[PCAL_MONTH_KEY],
            'Planning Calendar PCAL'[PCAL_WEEK_KEY],
            FILTER(
            VALUES('Planning Calendar PCAL'[PCAL_WEEK_KEY]),
            'Planning Calendar PCAL'[PCAL_WEEK_KEY] = """ + str(daxWeek) + """
            ),
            FILTER(
            VALUES('Product Hierarchy PRH'[PRH PEPCO]),
            'Product Hierarchy PRH'[PRH PEPCO] IN {"a Merchandise"}
            ),
            "SalesValue",
            [Sales Retail Report DP mmfp],
            "MonthNew",
            "Y"&LEFT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_MONTH_KEY]), STRING),4)&"M"&RIGHT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_MONTH_KEY]), STRING),2),
            "WeekNew",
            "Y"&LEFT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_WEEK_KEY]), STRING),4)&"W"&RIGHT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_WEEK_KEY]), STRING),2)
            ),
            [SalesValue] > 0
            ),
            "PRH Category ID",
            [PRH Category ID],
            "MonthNew",
            [MonthNew],
            "WeekNew",
            [WeekNew],
            "SalesValue",
            [SalesValue]
            )
    """


def salesHistorical(daxWeek):
    return """
            EVALUATE
            SELECTCOLUMNS(
            FILTER(
            SUMMARIZECOLUMNS(
            'Product Hierarchy PRH'[PRH Category ID],
            'Planning Calendar PCAL'[PCAL_MONTH_KEY],
            'Planning Calendar PCAL'[PCAL_WEEK_KEY],
            'Stores STR'[STR Number],
            FILTER(
            VALUES('Planning Calendar PCAL'[PCAL_WEEK_KEY]),
            'Planning Calendar PCAL'[PCAL_WEEK_KEY] = """ + str(daxWeek) + """
            ),
            FILTER(
            VALUES('Product Hierarchy PRH'[PRH PEPCO]),
            'Product Hierarchy PRH'[PRH PEPCO] IN {"a Merchandise"}
            ),
            "SalesValue",
            [Sales Retail Report dsale],
            "MonthNew",
            "Y"&LEFT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_MONTH_KEY]), STRING),4)&"M"&RIGHT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_MONTH_KEY]), STRING),2),
            "WeekNew",
            "Y"&LEFT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_WEEK_KEY]), STRING),4)&"W"&RIGHT(CONVERT(MAX('Planning Calendar PCAL'[PCAL_WEEK_KEY]), STRING),2)
            ),
            [SalesValue] > 0
            ),
            "PRH Category ID",
            [PRH Category ID],
            "STR Number",
            'Stores STR'[STR Number],
            "MonthNew",
            [MonthNew],
            "WeekNew",
            [WeekNew],
            "SalesValue",
            [SalesValue]
            )

    """

def weeks(startEndMonths):
    daxStartMonth = startEndMonths[0][1:5] + startEndMonths[0][6:8]
    daxEndMonth = startEndMonths[1][1:5] + startEndMonths[1][6:8]

    return """
            EVALUATE
            SUMMARIZECOLUMNS (
                'Planning Calendar PCAL'[PCAL_WEEK_KEY],
                FILTER (
                    VALUES ( 'Planning Calendar PCAL'[PCAL_MONTH_KEY] ),
                    'Planning Calendar PCAL'[PCAL_MONTH_KEY] >= """ + str(daxStartMonth) + """
                        && 'Planning Calendar PCAL'[PCAL_MONTH_KEY] <= """ + str(daxEndMonth) + """
                )
            )
    """