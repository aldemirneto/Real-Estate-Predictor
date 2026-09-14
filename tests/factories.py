import factory


class PropertyFactory(factory.Factory):
    class Meta:
        model = dict

    preco = factory.Faker("pyfloat", min_value=150_000, max_value=3_000_000, right_digits=2)
    area = factory.Faker("pyfloat", min_value=40.0, max_value=600.0, right_digits=1)
    quartos = factory.Faker("random_element", elements=["1", "2", "3", "4"])
    vagas = factory.Faker("random_element", elements=["1", "2", "3"])
    banheiros = factory.Faker("random_element", elements=["1", "2", "3"])
    bairro = factory.Faker("random_element", elements=[
        "Centro", "Jardim_elite", "Pauliceia", "Alto", "Nova_piracicaba",
        "Sao_dimas", "Areiao", "Vila_monteiro",
    ])
    tipo = factory.Faker("random_element", elements=["Casa", "Apartamento", "Terreno"])
    Status = "Compra"
    link = factory.Sequence(lambda n: f"https://imobiliaria.com.br/imovel/{n}")
    Imobiliaria = "Test_imobiliaria"


class BrokenPropertyFactory(PropertyFactory):
    """Simulates a property dict with missing / bad data."""
    preco = None
    bairro = "Condomínio das Rosas"
    area = "N/A"
