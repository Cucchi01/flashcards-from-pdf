from PyQt6.QtWidgets import QTableView

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import os

import statistics_tab.heatmap_model as hm
from application_constants import PRIVATE_DB_FILENAME, PATH_TO_DECKS_ABS


def get_statistics() -> QTableView:
    heatmap: QTableView = QTableView()
    heatmap_model: hm.HeatmapModel
    try:
        con = sqlite3.connect(os.path.join(PATH_TO_DECKS_ABS, PRIVATE_DB_FILENAME))
        cur = con.cursor()

        create_table_timestamp(cur)

        df: pd.DataFrame = __get_timestamps_from_db(con)
        heatmap_data: pd.DataFrame = __get_heatmap_data(df)

        heatmap_model = hm.HeatmapModel(heatmap_data)
        heatmap.setModel(heatmap_model)

        cur.close()
    finally:
        if con:
            con.close()

    return heatmap


def __get_timestamps_from_db(con: sqlite3.Connection) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_sql_query("SELECT * from timestamp", con)
    df = df.drop(["id"], axis=1)
    df = df.iloc[:-1:]
    df = df.astype({"type": "string"})
    df.timestamp = pd.to_datetime(df.timestamp)
    return df


def __get_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    df_even = df.iloc[::2]
    df_odd = df.iloc[1::2]

    (df_even, df_odd) = __include_all_the_days(df_even, df_odd)

    df = __combina_even_and_odd(df_even, df_odd)
    return __create_heatmap(df)


def __include_all_the_days(
    df_even: pd.DataFrame, df_odd: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dfapp = pd.DataFrame(
        pd.date_range(start="2023-01-01", end="2023-12-31", periods=365)
    )
    dfapp = dfapp.rename(columns={0: "timestamp"})

    dfapp2 = dfapp.copy()
    dfapp["type"] = "S"
    dfapp2["type"] = "E"

    df_even = pd.concat(
        [df_even, dfapp],
        axis=0,
    )
    df_odd = pd.concat(
        [df_odd, dfapp2],
        axis=0,
    )
    return (df_even, df_odd)


def __combina_even_and_odd(df_even: pd.DataFrame, df_odd: pd.DataFrame) -> pd.DataFrame:
    df_odd.rename(
        columns={"id": "id2", "timestamp": "timestamp2", "type": "type2"},
        inplace=True,
    )
    df_even.reset_index(drop=True, inplace=True)
    df_odd.reset_index(drop=True, inplace=True)
    df: pd.DataFrame = pd.concat(
        [df_even, df_odd],
        axis=1,
    )
    return df


def __create_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    df["diff"] = df["timestamp2"] - df["timestamp"]
    df["day_of_week"] = df["timestamp"].dt.day_of_week
    df["week_of_year"] = df["timestamp"].dt.isocalendar().week

    df = (
        df[["diff", "week_of_year", "day_of_week"]]
        .groupby(["week_of_year", "day_of_week"], as_index=False)
        .sum()
    )
    df["diff"] = df["diff"].dt.total_seconds() / 3600

    return df.pivot(index="day_of_week", columns="week_of_year", values="diff")


def create_table_timestamp(cur: sqlite3.Cursor) -> None:
    res = cur.execute("SELECT * FROM sqlite_master where name='timestamp'")
    if res.fetchone() is None:
        cur.execute(
            """CREATE TABLE timestamp (id integer primary key autoincrement ,
                                        timestamp timestamp NOT NULL,
                                        type varchar(1))"""
        )
