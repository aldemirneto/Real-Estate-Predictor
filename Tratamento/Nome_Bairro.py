import csv
import unicodedata
import os

# Function to replace accented characters with unaccented equivalents and spaces with underscores
def replace_chars(string):
    # Replace accented characters with their unaccented equivalents
    string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode('utf-8')
    # Replace spaces with underscores
    string = string.replace(', piracicaba', '').replace(', PIRACICABA', '')
    string = string.replace(' ', '_')
    string = string.capitalize()
    return string

def run():
    # Define the blacklisted substrings
    blacklist = {'condominio', 'chacara', 'conjunto', 'edificio', 'convivio', 'residencial', 'vivendas', 'terra', 'recanto',
                 'loteamento', '-', 'park', 'parque', 'nucleo'}

    # Open the CSV file for reading and writing with the 'utf-8-sig' encoding
    with open('imoveis.csv', 'r', encoding='utf-8-sig') as input_file, open('output.csv', 'w', newline='', encoding='utf-8') as output_file:
        # Create a CSV reader and writer objects
        reader = csv.DictReader(input_file, delimiter=';')
        writer = csv.writer(output_file, delimiter=';')
        # Write the header row to the output CSV file
        writer.writerow(reader.fieldnames)
        # Loop through each row in the input CSV file
        for row in reader:
            # Check if the 'bairro' column contains any of the blacklisted substrings
            if not any(word in replace_chars(row['bairro']).lower() for word in blacklist):
                # Check if the 'bairro' column contains the name 'artemis'
                if 'artemis' in replace_chars(row['bairro']).lower():
                    # Replace the name 'artemis' with the string 'artemis' itself
                    row['bairro'] = 'Artemis'
                if 'centro' in replace_chars(row['bairro']).lower():
                    # Replace the name 'artemis' with the string 'artemis' itself
                    row['bairro'] = 'Centro'
                else:
                    # Create a new row with the replaced characters in the 'bairro' column
                    row['bairro'] = replace_chars(row['bairro'])
                # Write the new row to the output CSV file
                writer.writerow(row.values())


    # Overwrite the original CSV file with the modified version
    os.replace('output.csv', 'imoveis.csv')
