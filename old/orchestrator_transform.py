import old.Tratamento.Nome_Bairro, old.Tratamento.Duplicatas

filename = '../imoveis.csv'

print('Iniciando tratamento de nomes de bairros')
try:
    old.Tratamento.Nome_Bairro.run(filename)
    print('Fim de tratamento de nomes de bairros')
except Exception as e:
    print('Nome_Bairro', e)

print('Iniciando tratamento de duplicatas')
try:
    old.Tratamento.Duplicatas.run(filename)
    print('Fim de tratamento de duplicatas')
except Exception as e:
    print('Duplicata', e)


filename = '../imoveis_aluguel.csv'

print('Iniciando tratamento aluguel de nomes de bairros')
try:
    old.Tratamento.Nome_Bairro.run(filename)
    print('Fim de tratamento de nomes de bairros')
except Exception as e:
    print('Nome_Bairro', e)

print('Iniciando tratamento aluguel de duplicatas')
try:
    old.Tratamento.Duplicatas.run(filename)
    print('Fim de tratamento de duplicatas')
except Exception as e:
    print('Duplicata', e)

