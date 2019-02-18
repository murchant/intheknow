import os
import relations
import pandas as pd

def main():
    # relations.get_true_rels()
    # relations.make_commands()
    combine_tweets()
    print("Commands made")


# Combine long & short query tweet returned from API call
def combine_tweets():
    df_long = pd.read_csv("info/true.csv", sep=';', error_bad_lines=False, low_memory=False)
    df_short = pd.read_csv("info/trueShorter.csv", sep=';', error_bad_lines=False, low_memory=False)
    print(len(df_long.index))
    print(len(df_short.index))
    # df_left_outer = pd.merge(df_short, df_long, on='text', how="outer")
    df_left_outer = pd.concat([df_short, df_long])
    df_left_outer.to_csv("info/true_data_set.csv")
    print(len(df_left_outer.index))


if __name__ == '__main__':
    main()
