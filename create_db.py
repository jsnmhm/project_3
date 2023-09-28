import pandas as pd
import sqlite3

conn = sqlite3.connect("madden_stats.db")
cursor = conn.cursor()

stats = pd.read_csv("madden_stats.csv")

stats.to_sql("stats", conn)