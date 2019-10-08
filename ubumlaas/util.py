import pandas as pd

def get_dataframe_from_file(path, filename):
    if filename.split(".")[-1] == "csv":
        file_df = pd.read_csv(path + filename)
    elif filename.split(".")[-1] == "xls":
        file_df = pd.read_excel(path + filename)
    else:
        raise Exception("Invalid format for "+filename)
    return file_df