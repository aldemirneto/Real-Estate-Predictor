from types import SimpleNamespace
from pathlib import Path
import importlib.util
import json
from unittest.mock import Mock
from Extract.SPImovelScraper import parse_agency_page, parse_directory_html

AGENCY = {'id': 123, 'nome': 'Imobiliária de teste', 'url': 'https://www.spimovel.com.br/imobiliaria/teste/sao-paulo/123/'}


def html(page=1, operation='1', city='São Paulo', identity=123, count=2, size=1):
    return f'''<div class="imobiliaria"><h1>Imobiliária de teste</h1></div>
    <input id="ImobiliariaId" value="{identity}"><input name="txtCount" value="{count}"><input name="txtItens" value="{size}">
    <div class="lista-anuncio"><div class="anuncio">
      <h2 class="h2-tipo"><a href="/imovel/teste/{page}/" data-imovelid="{page}">Apartamento para Venda no Centro</a></h2>
      <h3 class="h2-regiao titulo">Centro - {city}</h3><h3 class="valor">R$ 1.250.000,50</h3>
      <div class="especificacoes-mobile"><div><i class="ico-quartos"></i>3 quartos</div><div><i class="ico-area"></i>186,96 m²</div><div><i class="ico-vagas"></i>- vaga</div></div>
      <button data-finalidadeid="{operation}"></button>
    </div></div>'''


def test_sale_fields_and_brazilian_numbers():
    rows, pages, ids, expected = parse_agency_page(html(), AGENCY)
    assert rows[0]['preco'] == 1250000.50
    assert rows[0]['area'] == 186.96
    assert rows[0]['quartos'] == 3
    assert rows[0]['vagas'] is None
    assert rows[0]['banheiros'] is None
    assert rows[0]['imobiliaria'] == AGENCY['nome']
    assert rows[0]['cidade'] == 'São Paulo'
    assert pages == 2 and expected == 2 and ids == ('1',)


def test_rentals_and_other_cities_not_loaded():
    assert parse_agency_page(html(operation='2'), AGENCY)[0] == []
    assert parse_agency_page(html(city='Osasco'), AGENCY)[0] == []


def test_wrong_agency_is_rejected():
    import pytest
    with pytest.raises(ValueError, match='não corresponde'):
        parse_agency_page(html(identity=999), AGENCY)


def test_directory_duplicate_links_and_people_are_classified():
    link = '<a href="/imobiliaria/teste/sao-paulo/123/"><p>Teste</p><p>Centro, São Paulo</p><p class="creci">CRECI: 123-J</p></a>'
    rows = parse_directory_html(link + link)
    assert len(rows) == 1 and rows[0]['tipo_registro'] == 'empresa'
    assert parse_directory_html(link.replace('123-J', '123-F'))[0]['tipo_registro'] == 'corretor'


def crawler():
    spec = importlib.util.spec_from_file_location('sp_crawler', Path(__file__).parents[1] / 'scripts/crawl_sao_paulo.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_second_page_zero_counts_keep_first_page_pagination(tmp_path):
    fetcher = Mock()
    fetcher.get.side_effect = [SimpleNamespace(text=html()), SimpleNamespace(text=html(page=2, count=0, size=0))]
    result = crawler().crawl_agency(AGENCY, fetcher, tmp_path, False)
    assert result['status'] == 'complete'
    assert len(result['properties']) == 2
    assert result['expected_ads'] == 2
    assert json.loads((tmp_path / '123.json').read_text())['next_page'] == 3


def test_repeated_page_is_partial_not_complete(tmp_path):
    fetcher = Mock()
    fetcher.get.side_effect = [SimpleNamespace(text=html())] * 5
    result = crawler().crawl_agency(AGENCY, fetcher, tmp_path, False)
    assert result['status'] == 'partial'
    assert 'repetida' in result['error']
    assert len(result['properties']) == 1


def test_temporary_repeated_page_does_not_end_catalog_early(tmp_path):
    fetcher = Mock()
    fetcher.get.side_effect = [SimpleNamespace(text=html(count=3)),
        SimpleNamespace(text=html(page=2, count=0, size=0)),
        SimpleNamespace(text=html(page=2, count=0, size=0)),
        SimpleNamespace(text=html(page=3, count=0, size=0))]
    result = crawler().crawl_agency(AGENCY, fetcher, tmp_path, False)
    assert result['status'] == 'complete'
    assert len(result['properties']) == 3
    assert fetcher.get.call_count == 4
