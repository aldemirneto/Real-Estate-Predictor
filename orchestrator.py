import imobiliárias.junqueira, imobiliárias.frias_neto

import csv

filename = 'imoveis.csv'


try:
    imobiliárias.junqueira.run()
except Exception as e:
    print('junqueira', e)
try:
    imobiliárias.frias_neto.run()
except Exception as e:
    print('frias_neto', e)

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
        # Remove the "Data_scrape" column from the row
        row_without_date = row[:date_col_index] + row[date_col_index + 1:]

        # Convert the row to a tuple and add it to the set
        unique_rows.add(tuple(row_without_date))

# Write the header and unique rows back to the CSV file
with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(header)
    writer.writerows(list(unique_rows))
