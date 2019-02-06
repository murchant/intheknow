import pandas as pd
import numpy as np

df_long = pd.read_csv("true.csv", sep=';', error_bad_lines=False)
df_short = pd.read_csv("trueShorter.csv", sep=';', error_bad_lines=False)

print(len(df_long.index))
print(len(df_short.index))

print("Intersection")
df_intersection = pd.merge(df_long, df_short, on='text')
print(len(df_intersection.index))

print("Left Join")
df_left_outer = pd.merge(df_short, df_long, on='text', how="left")
print(len(df_left_outer.index))
