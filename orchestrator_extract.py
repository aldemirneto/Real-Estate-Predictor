import imobiliárias.junqueira, imobiliárias.frias_neto, imobiliárias.sao_judas, piracicaba_json, imobiliárias.duo, imobiliárias.junqueira_aluguel, imobiliárias.frias_neto_aluguel, imobiliárias.duo_aluguel


filename = 'imoveis.csv'

print('Iniciando scrape de imobiliárias')
try:
    print('Inicio de scrape Junqueira')
    imobiliárias.junqueira.run()
    imobiliárias.junqueira_aluguel.run()
    print('Fim de scrape Junqueira')
except Exception as e:
    print('junqueira', e)
try:
    print('Inicio de scrape Frias Neto')
    imobiliárias.frias_neto.run()
    imobiliárias.frias_neto_aluguel.run()
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
    imobiliárias.duo_aluguel.run()
    print('Fim de scrape duo imoveis')
except Exception as e:
    print('duo', e)



