import streamlit as st
import pandas as pd
import sqlite3

# Function to save DataFrame to SQLite
def save_to_sqlite(df, db_name, table_name):
    with sqlite3.connect(db_name) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)