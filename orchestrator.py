import imobiliárias.junqueira, imobiliárias.frias_neto, imobiliárias.sao_judas, piracicaba_json, imobiliárias.duo
import Tratamento.Nome_Bairro, Tratamento.Duplicatas

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

try:
    print('Inicio de scrape duo imoveis')
    imobiliárias.duo.run()
    print('Fim de scrape duo imoveis')
except Exception as e:
    print('duo', e)

# Read the CSV file and store the header row

print('Iniciando tratamento de duplicatas')
try:
    Tratamento.Duplicatas.run(filename)
    print('Fim de tratamento de duplicatas')
except Exception as e:
    print('Duplicata', e)


print('Iniciando tratamento de nomes de bairros')
try:
    Tratamento.Nome_Bairro.run()
    print('Fim de tratamento de nomes de bairros')
except Exception as e:
    print('Nome_Bairro', e)