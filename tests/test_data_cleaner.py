import pytest
from tests.factories import PropertyFactory, BrokenPropertyFactory
from Transform.DataCleaner import DataCleaner


# ── replace_chars ────────────────────────────────────────────────────────────

def test_replace_chars_strips_accents():
    assert DataCleaner.replace_chars("São João") == "Sao_joao"

def test_replace_chars_normalizes_spaces_to_underscores():
    assert DataCleaner.replace_chars("Vila Monteiro") == "Vila_monteiro"

def test_replace_chars_capitalizes():
    result = DataCleaner.replace_chars("centro")
    assert result[0].isupper()

def test_replace_chars_handles_piracicaba_suffix():
    result = DataCleaner.replace_chars("Alto, Piracicaba")
    assert "piracicaba" not in result.lower()

def test_replace_chars_centro_normalization():
    assert DataCleaner.replace_chars("centro") == "Centro"

def test_replace_chars_artemis_normalization():
    assert DataCleaner.replace_chars("artemis") == "Artemis"


# ── validate_data ────────────────────────────────────────────────────────────

def test_validate_data_flattens_nested_lists():
    data = [[PropertyFactory()], [PropertyFactory()]]
    cleaner = DataCleaner(data)
    result = cleaner.validate_data()
    assert len(result) == 2

def test_validate_data_removes_blacklisted_bairro():
    good  = PropertyFactory(bairro="Jardim Elite")
    bad   = PropertyFactory(bairro="Condomínio das Rosas")
    cleaner = DataCleaner([[good], [bad]])
    result = cleaner.validate_data()
    assert len(result) == 1
    assert result[0]["bairro"] == "Jardim_elite"

def test_validate_data_removes_loteamento():
    prop = PropertyFactory(bairro="Loteamento Bela Vista")
    cleaner = DataCleaner([[prop]])
    assert cleaner.validate_data() == []

def test_validate_data_normalizes_bairro_field():
    prop = PropertyFactory(bairro="São Dimas")
    cleaner = DataCleaner([[prop]])
    result = cleaner.validate_data()
    assert result[0]["bairro"] == "Sao_dimas"

def test_validate_data_empty_input():
    cleaner = DataCleaner([])
    assert cleaner.validate_data() == []

def test_validate_data_multiple_scrapers():
    """Simulates data arriving as a list-of-lists from multiple scrapers."""
    data = [
        [PropertyFactory(bairro="Centro"), PropertyFactory(bairro="Loteamento X")],
        [PropertyFactory(bairro="Alto"),   PropertyFactory(bairro="Parque Industrial")],
    ]
    cleaner = DataCleaner(data)
    result = cleaner.validate_data()
    bairros = {r["bairro"] for r in result}
    assert "Centro" in bairros
    assert "Alto" in bairros
    assert len(result) == 2
