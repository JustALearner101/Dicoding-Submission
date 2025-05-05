from utils.extract import extract
from utils.transform import transform
from utils.load import load

def run_etl():
    print("Extracting data...")
    raw_data = extract()

    print("Transforming data...")
    transformed_data = transform(raw_data)

    print("Loading data...")
    load(transformed_data)

if __name__ == "__main__":
    run_etl()
