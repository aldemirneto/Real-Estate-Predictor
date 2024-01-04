import old.imobiliárias.junqueira_aluguel, old.imobiliárias.duo_aluguel



print('Iniciando scrape de imobiliárias')
try:
    print('Inicio de scrape Junqueira')
    old.imobiliárias.junqueira.run()
    old.imobiliárias.junqueira_aluguel.run()
    print('Fim de scrape Junqueira')
except Exception as e:
    print('junqueira', e)
try:
    print('Inicio de scrape Frias Neto')
    # imobiliárias.frias_neto.run()
    old.imobiliárias.frias_neto_aluguel.run()
    print('Fim de scrape Frias Neto')
except Exception as e:
    print('frias_neto', e)
try:
    print('Inicio de scrape São Judas')
    old.imobiliárias.sao_judas.run()
    print('Fim de scrape São Judas')
except Exception as e:
    print('sao_judas', e)

try:
    print('Inicio de scrape duo imoveis')
    old.imobiliárias.duo.run()
    old.imobiliárias.duo_aluguel.run()
    print('Fim de scrape duo imoveis')
except Exception as e:
    print('duo', e)



