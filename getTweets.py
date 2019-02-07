import os
import relations
import pandas as pd

def main():
    relations.get_true_rels()
    relations.make_commands()
    # combine_tweets()
    print("Commands made")


# Combine long & query tweet returned from API call
def combine_tweets():
    df_long = pd.read_csv("info/true.csv", sep=';', error_bad_lines=False)
    df_short = pd.read_csv("info/trueShorter.csv", sep=';', error_bad_lines=False)
    df_left_outer = pd.merge(df_short, df_long, on='text', how="left")
    df_left_outer.to_csv("info/true_data_set.csv")

if __name__ == '__main__':
    main()
