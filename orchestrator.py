import imobiliárias.junqueira, imobiliárias.frias_neto

try:
    imobiliárias.junqueira.run()
except Exception as e:
    print('junqueira', e)
try:
    imobiliárias.frias_neto.run()
except Exception as e:
    print('frias_neto', e)

