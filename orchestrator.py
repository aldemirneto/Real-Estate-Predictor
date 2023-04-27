import imobiliárias.junqueira, imobiliárias.frias_neto, imobiliárias.sao_judas, piracicaba_json
import os
import csv
import Tratamento.Nome_Bairro
filename = 'imoveis.csv'
try:
    piracicaba_json.run()
except:
    pass

print('Iniciando scrape de imobiliárias')
try:
    print('Inicio de scrape Junqueira')
    imobiliárias.junqueira.run()
    print('Fim de scrape Junqueira')
except Exception as e:
    print('junqueira', e)
try:
    print('Inicio de scrape Frias Neto')
    imobiliárias.frias_neto.run()
    print('Fim de scrape Frias Neto')
except Exception as e:
    print('frias_neto', e)
try:
    print('Inicio de scrape São Judas')
    imobiliárias.sao_judas.run()
    print('Fim de scrape São Judas')
except Exception as e:
    print('sao_judas', e)

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

# Open the CSV file for reading and writing with the 'utf-8-sig' encoding
with open(filename, 'r', encoding='utf-8-sig') as input_file, open('output.csv', 'w', newline='', encoding='utf-8') as output_file:
    # Create a CSV reader and writer objects with the delimiter set to ';'
    reader = csv.reader(input_file, delimiter=';')
    writer = csv.writer(output_file, delimiter=';')
    # Loop through each row in the input CSV file
    for row in reader:
        # Replace all instances of ' ;' and '; ' with ';'
        new_row = [cell.strip() for cell in row]
        # Write the new row to the output CSV file
        writer.writerow(new_row)

# Overwrite the original CSV file with the modified version
os.replace('output.csv', filename)


print('Iniciando tratamento de nomes de bairros')
try:
    print('Inicio de tratamento de nomes de bairros')
    Tratamento.Nome_Bairro.run()
    print('Fim de tratamento de nomes de bairros')
except Exception as e:
    print('Nome_Bairro', e)