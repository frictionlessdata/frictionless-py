# type: ignore
from _pytest._code.code import ExceptionInfo
import pytest

from datetime import datetime, time
from dateutil.tz import tzoffset, tzutc
from frictionless import Package, Catalog, Resource, portals
from frictionless.exception import FrictionlessException


OUTPUT = {
    "name": "dicionario-de-dados",
    "description": "Pagamentos",
    "path": "https://www.portaltransparencia.gov.br/pagina-interna/603397-dicionario-de-dados-bolsa-familia-pagamentos",
    "format": "html",
    "hash": "",
    "package_id": "f63dd0f4-fa56-45ec-811b-4509e6b54643",
    "created": "2018-11-21T12:39:43.066625",
    "revision_id": "2bd875f0-1c9b-4819-aae6-88ed68e2333f",
    "id": "dad8154b-7e1c-457c-aa2c-f1fbb61c51d4",
}

OUTPUT_DATA_CSV = [
    {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
    {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
    {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
    {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    {"id": 5, "neighbor_id": None, "name": None, "population": None},
]


# Read


@pytest.mark.vcr
def test_ckan_adapter_read(options_datasets):
    url = options_datasets.pop("bolsa-familia-pagamentos")
    package = Package(url)
    assert package.resources[0].to_descriptor() == OUTPUT
    assert len(package.resources) == 59


@pytest.mark.vcr
def test_ckan_adapter_read_without_apikey(options_datasets):
    url = options_datasets.pop("bolsa-familia-pagamentos")
    package = Package(url, control=portals.CkanControl(apikey=None))
    assert package.resources[0].to_descriptor() == OUTPUT
    assert len(package.resources) == 59


@pytest.mark.vcr
def test_ckan_adapter_read_specific_dataset(options_br):
    url = options_br.pop("url")
    ckan_control = portals.CkanControl(baseurl=url)
    package = Package("bolsa-familia-pagamentos", control=ckan_control)
    assert package.resources[0].to_descriptor() == OUTPUT
    assert len(package.resources) == 59


@pytest.mark.vcr
def test_ckan_adapter_read_invalid_url(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url, dataset="no-dataset")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(control=control)
    error = excinfo.value.error
    assert "Not Found Error" in error.message


@pytest.mark.vcr
def test_ckan_adapter_read_ignore_schema_if_errors(options_br):
    url = options_br.pop("url")
    dataset = options_br.pop("dataset")
    control = portals.CkanControl(baseurl=url, ignore_schema=True)
    package = Package(dataset, control=control)
    assert "schema" not in package.resources[0].to_descriptor().keys()


@pytest.mark.vcr
def test_ckan_adapter_read_with_controls_only(options_br):
    url = options_br.pop("url")
    dataset = options_br.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert package.resources[0].to_descriptor() == OUTPUT


@pytest.mark.vcr
def test_ckan_adapter_read_without_dataset(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url)
    with pytest.raises(AssertionError) as excinfo:
        Package(control=control)
    assert isinstance(excinfo, ExceptionInfo)


@pytest.mark.vcr
def test_ckan_adapter_read_noparams():
    control = portals.CkanControl()
    with pytest.raises(AssertionError) as excinfo:
        Package(control=control)
    assert isinstance(excinfo, ExceptionInfo)


# Read - Data


@pytest.mark.vcr
def test_ckan_adapter_read_data(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert package.resources[0].read_rows() == OUTPUT_DATA_CSV
    assert package.resources[0].name == "countries-csv"


@pytest.mark.vcr
def test_ckan_adapter_read_data_xls(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert package.resources[1].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert package.resources[1].name == "table-xls"


@pytest.mark.vcr
def test_ckan_adapter_read_data_ods(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert package.resources[2].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert package.resources[2].name == "table-ods"


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to read json file")
def test_ckan_adapter_read_data_json(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert package.resources[3].read_rows() == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": 67},
        {"id": 2, "neighbor_id": 3, "name": "France", "population": "n/a"},
        {"id": 3, "neighbor_id": 22, "name": "Germany", "population": 83},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": 60},
    ]


@pytest.mark.vcr
def test_ckan_adapter_read_data_check_path_is_valid(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert (
        package.resources[0].path
        == "http://localhost:5000/dataset/1b26c9fe-1869-4999-954f-0f276d4bea02/resource/5de110e5-6ef9-4282-9866-9201a0014dea/download/___"
    )


# Read Catalog


@pytest.mark.vcr
def test_ckan_adapter_catalog(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url)
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert len(catalog.packages) == 10
    assert packages == [
        "corridas-do-taxigov",
        "comprasnet-contratos",
        "raio-x-da-administracao-publica-federal",
        "siorg",
        "http-www-funarte-gov-br-preservacaofotografica",
        "cadastro-nacional-da-pessoa-juridica-cnpj",
        "codigos-de-vaga",
        "projetos-de-pesquisa-ifg",
        "contratos-ifg",
        "programas-editais-de-iniciacao-cientifica",
    ]


@pytest.mark.vcr
def test_ckan_adapter_catalog_check_package_resources(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url)
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 10
    assert len(catalog.packages[0].resources) == 47


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to read data")
def test_ckan_adapter_catalog_read_package_resources(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url)
    catalog = Catalog(control=control)
    rows = catalog.packages[1].resources[3].read_rows(size=2)
    data = [[field["id"], field["receita_despesa"]] for field in rows]
    assert data == [[149633, "Despesa"], [149661, "Despesa"]]


@pytest.mark.vcr
def test_ckan_adapter_catalog_limit_packages(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url, num_packages=2)
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert len(catalog.packages) == 2
    assert packages == ["corridas-do-taxigov", "comprasnet-contratos"]


@pytest.mark.vcr
def test_ckan_adapter_catalog_check_ignore_packages(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, ignore_package_errors=True, num_packages=800
    )
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 797


@pytest.mark.vcr
def test_ckan_adapter_catalog_read_packages_by_organization(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, organization_name="agencia-espacial-brasileira-aeb"
    )
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert len(catalog.packages) == 6
    assert packages == [
        "catalogo-industria-espacial",
        "dados-abertos-de-contratos-administrativos",
        "dados-abertos-de-recursos-humanos-da-aeb",
        "objetos-espaciais-brasileiro",
        "ciclo-de-avaliacao-de-desempenho-institucional-da-aeb",
        "dados-abertos-de-orcamento-da-aeb",
    ]


@pytest.mark.vcr
def test_ckan_adapter_catalog_read_packages_by_groupid(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, group_id="agricultura-extrativismo-e-pesca"
    )
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert len(catalog.packages) == 9
    assert packages == [
        "seguro-da-agricultura-familiar-seaf",
        "apoio-a-unidade-de-ensino-em-aquicultura",
        "aquicultura-familiar",
        "credito-para-pesca-e-aquicultura",
        "pesca-e-aquicultura-capacitacao-e-incubacao",
        "pesquisa-e-tecnologia-na-pesca-e-aquicultura",
        "regime-geral-da-pesca",
        "pronaf-programa-nacional-de-fortalecimento-da-agricultura-familiar",
        "paa-programa-de-aquisicao-de-alimentos-da-agricultura-familiar",
    ]


@pytest.mark.vcr
def test_ckan_adapter_catalog_read_packages_by_invalid_group(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, group_id="agricultura-extrativismo-e-pescaa"
    )
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(control=control)
    error = excinfo.value.error
    assert "Not Found Error" in error.message


@pytest.mark.vcr
def test_ckan_adapter_catalog_read_packages_by_invalid_organization_name(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, organization_name="agricultura-extrativismo-e-pescaa"
    )
    catalog = Catalog(control=control)
    assert catalog.packages == []


@pytest.mark.vcr
def test_ckan_adapter_catalog_search(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url, search={"q": "name:bolsa*"})
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert packages == [
        "bolsa-familia-saques",
        "bolsa-familia-pagamentos",
        "bolsa-familia-misocial",
        "bolsas-projetos-solicitacao-criterios",
        "bolsas-projetos-pqa",
        "bolsas-projetos-epem-avaliacoes",
        "bolsas-projetos-aprovados-solicitacao-bolsistas-fapergs",
        "bolsas-projetos-aprovados-solicitacao-bolsistas-e-p-e-c",
        "bolsas-projetos-aprovados-solicitacao-bolsistas-cnpq",
        "bolsas-periodos-fapergs",
    ]


@pytest.mark.vcr
def test_ckan_adapter_catalog_search_or_query(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, search={"q": "title:Contratos || title:Federal"}
    )
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert packages == [
        "licitacoes-e-contratos-do-governo-federal",
        "dados-dos-contratos-vigentes-do-servico-de-limpeza-urbana-do-distrito-federal",
        "contratos-ifg",
        "contratos14",
        "contratos10",
        "contratos-unb",
        "contratoshuufgd1",
        "contratos16",
        "ifes-contratos",
        "contratos5",
    ]


@pytest.mark.vcr
def test_ckan_adapter_catalog_search_with_results_offset(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, results_offset=3, search={"q": "title:Contratos || title:Federal"}
    )
    catalog = Catalog(control=control)
    packages = [package.name for package in catalog.packages]
    assert packages == [
        "contratos14",
        "contratos10",
        "contratos-unb",
        "contratoshuufgd1",
        "contratos16",
        "ifes-contratos",
        "contratos5",
        "contratos1",
        "contratos-ifb",
        "contratos12",
    ]


# Publish


@pytest.mark.vcr
def test_ckan_adapter_publish_minimal_package_info(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(baseurl=url, apikey="env:CKAN_APIKEY")
    package = Package("data/package.json")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/effc1c30-f165-4b2f-a169-eeba0b13c7fb" in response

    # Read
    control = portals.CkanControl(baseurl=url, dataset="name")
    package = Package(control=control)
    assert package.name == package_name


@pytest.mark.vcr
def test_ckan_adapter_publish_with_detail_info(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(baseurl=url, apikey="env:CKAN_APIKEY")
    package = Package("data/detailed.package.json")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/755cfcac-cd87-4522-9a81-99e82298047b" in response

    # Read
    control = portals.CkanControl(
        baseurl=url, dataset="dataset-test-package-with-organization"
    )
    package = Package(control=control)
    assert package.name == package_name


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to read package file with schema")
def test_ckan_adapter_publish_with_detail_info_with_schema(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(baseurl=url, apikey="env:CKAN_APIKEY")
    package = Package("data/detailed-with-schema.package.json")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/2a02c167-589f-42da-866b-67fd29895d5b" in response

    # Read
    control = portals.CkanControl(baseurl=url, dataset="dataset-test-package-with-schema")
    package = Package(control=control)
    assert package.name == package_name


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to update")
def test_ckan_adapter_publish_update_info(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(baseurl=url, apikey="env:CKAN_APIKEY")
    package = Package("data/detailed-with-id.package.json")
    response = package.publish(control=control)
    assert "dataset/dataset-test-detailed-with-id" in response

    # Update
    control = portals.CkanControl(
        baseurl=url, dataset="dataset-test-detailed-with-id", allow_update=True
    )
    response = package.publish(control=control)
    assert "dataset/dataset-test-detailed-with-id" in response


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to write")
def test_ckan_parser(options_lh):
    baseurl = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(
        baseurl=baseurl, dataset=dataset, apikey="env:CKAN_APIKEY"
    )
    source = Resource("data/table.csv")
    target = source.write(baseurl, control=control, format="csv")
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to write")
def test_ckan_parser_timezone(options_lh):
    baseurl = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(
        baseurl=baseurl, dataset=dataset, apikey="env:CKAN_APIKEY"
    )
    source = Resource("data/timezone.csv")
    target = source.write(baseurl, control=control, format="csv")
    with target:
        assert target.read_rows() == [
            {
                "datetime": datetime(2020, 1, 1, 15),
                "time": time(15),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzutc()),
                "time": time(15, 0, tzinfo=tzutc()),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, 10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, 10800)),
            },
            {
                "datetime": datetime(2020, 1, 1, 15, 0, tzinfo=tzoffset(None, -10800)),
                "time": time(15, 0, tzinfo=tzoffset(None, -10800)),
            },
        ]
