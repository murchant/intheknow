import pandas as pd
import numpy as np

df_long = pd.read_csv("info/true.csv", usecols=["username", "text", "date"], sep=';', error_bad_lines=False)
df_short = pd.read_csv("info/trueShorter.csv", usecols=["username", "text", "date"], sep=';', error_bad_lines=False)

print(len(df_long.index))
print(len(df_short.index))

print("Intersection")
df_intersection = pd.merge(df_long, df_short, on='username')
print(len(df_intersection.index))

print("Left Join")
df_left_outer = pd.concat([df_short, df_long])
print(len(df_left_outer.index))

df_left_outer.to_csv("info/true_data_set.csv", sep=";", encoding='utf-8')
