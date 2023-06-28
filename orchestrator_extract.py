import imobiliárias.junqueira, imobiliárias.frias_neto, imobiliárias.sao_judas, piracicaba_json, imobiliárias.duo


filename = 'imoveis.csv'

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



