import  piracicaba_json
import Tratamento.Nome_Bairro, Tratamento.Duplicatas

filename = 'imoveis.csv'
try:
    piracicaba_json.run()
except:
    pass

print('Iniciando tratamento de nomes de bairros')
try:
    Tratamento.Nome_Bairro.run()
    print('Fim de tratamento de nomes de bairros')
except Exception as e:
    print('Nome_Bairro', e)

print('Iniciando tratamento de duplicatas')
try:
    Tratamento.Duplicatas.run(filename)
    print('Fim de tratamento de duplicatas')
except Exception as e:
    print('Duplicata', e)


