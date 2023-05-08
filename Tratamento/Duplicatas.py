import csv
import os

from pydantic import BaseModel
from datetime import datetime

# Define a Pydantic model for each row in the CSV file
class imovel(BaseModel):
    preco: float
    area: float
    quartos: int
    vagas: str
    banheiros: str
    link: str
    Data_scrape: str
def run(filename):
    # Read the CSV file and store the header row
    with open(filename, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        header = next(reader)

        # Find the index of the "Data_scrape" column
        date_col_index = header.index('Data_scrape')

        # Create a set to store the unique rows
        unique_rows = set()

        # Iterate over the rows in the CSV file
        for row in reader:
            # Parse the row into a Pydantic model
            try:
                imovel(preco=float(row[0]), area=float(row[1]), quartos=int(row[2]), vagas=row[3], banheiros=row[4], link=row[5], Data_scrape=row[6])
            except:
                # If the row cannot be parsed, skip it
                continue

            # Check if the row is already in the set without the date
            if tuple(row[:date_col_index] + row[date_col_index + 1:]) not in [(u[:date_col_index] + u[date_col_index + 1:]) for u in unique_rows]:
                # Add the row to the set
                unique_rows.add(tuple(row))

    # Write the header and unique rows back to the CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(header)
        for row in unique_rows:
            # Add the "Data_scrape" column back to the row before writing it to the file
            writer.writerow(row)

    # Open the CSV file for reading and writing with the 'utf-8-sig' encoding
    with open(filename, 'r', encoding='utf-8-sig') as input_file, open('output.csv', 'w', newline='', encoding='utf-8') as output_file:
        # Create a CSV reader and writer objects with the delimiter set to ';'
        reader = csv.reader(input_file, delimiter=';')
        writer = csv.writer(output_file, delimiter=';')
        # Loop through each row in the input CSV file
        for row in reader:
            # Parse the row into a Pydantic model
            if row[0] == 'preco':
                writer.writerow(row)
                continue
            try:
                imovel(preco=float(row[0]), area=float(row[1]), quartos=int(row[2]), vagas=row[3], banheiros=row[4], link=row[5], Data_scrape=datetime.today().strftime('%Y-%m-%d'))
            except:
                # If the row cannot be parsed, skip it
                continue

            # Replace all instances of ' ;' and '; ' with ';'
            new_row = [cell.strip() for cell in row]
            # Write the new row to the output CSV file
            writer.writerow(new_row)

    # Overwrite the original CSV file with the modified version
    os.replace('output.csv', filename)
