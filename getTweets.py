import os
import relations

def main():
    relations.make_commands()
    print("Commands made")

if __name__ == '__main__':
    main()

# Combine long & query tweet returned from API call
def combine_tweets():
    df_long = pd.read_csv("info/true.csv", sep=';', error_bad_lines=False)
    df_short = pd.read_csv("info/trueShorter.csv", sep=';', error_bad_lines=False)
    df_left_outer = pd.merge(df_short, df_long, on='text', how="left")
    df_left_outer.to_csv("info/true_data_set.csv")
