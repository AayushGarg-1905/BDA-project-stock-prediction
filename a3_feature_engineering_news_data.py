import pandas as pd

def convert_date_format_in_csv(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    def convert_date_format(col):
        print("date conversion is ")
        print(col)
        return col.apply(lambda x: '-'.join(x.split('-')[::-1]))

    df['date'] = convert_date_format(df['date'])
    print("pritnign df after conversion------------------")
    print(df.head())
    df.to_csv(output_path, index=False)
    print(f"Converted date format saved to: {output_path}")
    print(df.head()) 

if __name__ == "__main__":
    convert_date_format_in_csv(
    input_path="news_sentiment_gnews_full.csv",
    output_path="news_sentiment_gnews_full_v2.csv"
)