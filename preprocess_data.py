import pandas as pd

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df = df["Products"]

    df = df.str.split(", ")
    
    all_items = sorted({item for sublist in df for item in sublist})
    # Convert items to unique IDs
    item2id = {item: idx for idx, item in enumerate(all_items)}

    transactions = [
        [item2id[item] for item in transaction]
        for transaction in df
    ]

    return transactions


   


