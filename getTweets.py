import os
import relations

def main():
    relations.make_commands()
    print("Commands made")


if __name__ == '__main__':
    main()

def clean_tweets():
    df_long = pd.read_csv("true.csv", sep=';', error_bad_lines=False)
    df_short = pd.read_csv("trueShorter.csv", sep=';', error_bad_lines=False)
    df_left_outer = pd.merge(df_short, df_long, on='text', how="left")
    df_left_outer.to_csv("true_data_set.csv")
