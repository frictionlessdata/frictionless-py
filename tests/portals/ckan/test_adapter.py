from datetime import datetime, time

import pytest
import requests
from _pytest._code.code import ExceptionInfo
from dateutil.tz import tzoffset, tzutc

from frictionless import Catalog, FrictionlessException, Package, portals
from frictionless.resources import TableResource

OUTPUT = {
    "name": "dicionario-de-dados",
    "type": "text",
    "description": "Pagamentos",
    "path": "https://www.portaltransparencia.gov.br/pagina-interna/603397-dicionario-de-dados-bolsa-familia-pagamentos",
    "scheme": "https",
    "format": "html",
    "mediatype": "text/html",
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


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_adapter_read_data(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert isinstance(package.resources[0], TableResource)
    assert package.resources[0].read_rows() == OUTPUT_DATA_CSV
    assert package.resources[0].name == "countries-csv"


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_adapter_read_data_xls(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert isinstance(package.resources[1], TableResource)
    assert package.resources[1].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
    assert package.resources[1].name == "table-xls"


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_adapter_read_data_ods(options_lh):
    url = options_lh.pop("url")
    dataset = options_lh.pop("dataset")
    control = portals.CkanControl(baseurl=url, dataset=dataset)
    package = Package(control=control)
    assert isinstance(package.resources[2], TableResource)
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
    assert isinstance(package.resources[3], TableResource)
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
    names = [dataset.name for dataset in catalog.datasets]
    assert len(names) == 10
    assert names == [
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
    assert len(catalog.datasets) == 10
    assert len(catalog.datasets[0].package.resources) == 47


@pytest.mark.vcr
@pytest.mark.skip(reason="Fails to read data")
def test_ckan_adapter_catalog_read_package_resources(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url)
    catalog = Catalog(control=control)
    assert isinstance(catalog.datasets[1].package.resources[3], TableResource)
    rows = catalog.datasets[1].package.resources[3].read_rows(size=2)
    data = [[field["id"], field["receita_despesa"]] for field in rows]
    assert data == [[149633, "Despesa"], [149661, "Despesa"]]


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_adapter_catalog_limit_packages(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url, num_packages=2)
    catalog = Catalog(control=control)
    names = [dataset.name for dataset in catalog.datasets]
    assert len(names) == 2
    assert names == ["corridas-do-taxigov", "comprasnet-contratos"]


@pytest.mark.skip
@pytest.mark.vcr
def test_ckan_adapter_catalog_check_ignore_packages(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, ignore_package_errors=True, num_packages=800
    )
    catalog = Catalog(control=control)
    assert len(catalog.datasets) == 797


@pytest.mark.vcr
def test_ckan_adapter_catalog_read_packages_by_organization(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(
        baseurl=url, organization_name="agencia-espacial-brasileira-aeb"
    )
    catalog = Catalog(control=control)
    names = [dataset.name for dataset in catalog.datasets]
    assert len(names) == 6
    assert names == [
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
    names = [dataset.name for dataset in catalog.datasets]
    assert len(names) == 9
    assert names == [
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
    assert catalog.datasets == []


@pytest.mark.vcr
def test_ckan_adapter_catalog_search(options_br):
    url = options_br.pop("url")
    control = portals.CkanControl(baseurl=url, search={"q": "name:bolsa*"})
    catalog = Catalog(control=control)
    names = [dataset.name for dataset in catalog.datasets]
    assert names == [
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
    names = [dataset.name for dataset in catalog.datasets]
    assert names == [
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
    names = [dataset.name for dataset in catalog.datasets]
    assert names == [
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
    control = portals.CkanControl(
        baseurl=url,
        apikey="env:CKAN_APIKEY",
        organization_name="frictionless-organization",
    )
    package = Package("data/package.json")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/0696c380-3fe6-4a62-9948-c0f09f17b389" in response

    # Read
    control = portals.CkanControl(baseurl=url, dataset="name")
    package = Package(control=control)
    assert package.name == package_name


@pytest.mark.vcr
def test_ckan_adapter_publish_with_detail_info(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(
        baseurl=url, apikey="env:CKAN_APIKEY", organization_name="frictionless-data"
    )
    package = Package("data/detailed.package.json")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/e1c26a30-5689-450f-af0a-262afba1e55c" in response

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
def test_ckan_adapter_publish_list_published_files(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(
        baseurl=url,
        apikey="env:CKAN_APIKEY",
        organization_name="frictionless-data",
    )
    package = Package("data/ckan.package.json")
    response = package.publish(control=control)
    assert "dataset/f1228d08-f1bd-4974-bae5-935d4dae331d" in response

    # Read
    dataset_dict = {"id": "dataset-test-package-file-write"}
    url = url + "api/action/package_show"
    response = requests.get(url, params=dataset_dict).json()
    package_data = response["result"]["resources"][0]
    assert package_data["name"] == "package"
    assert package_data["format"] == "JSON"
    assert len(response["result"]["resources"]) == 2


@pytest.mark.vcr
def test_ckan_adapter_publish_list_resources(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(
        baseurl=url,
        apikey="env:CKAN_APIKEY",
        organization_name="frictionless-data",
    )
    package = Package("data/ckan.package.yaml")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/ea8fbe1b-3702-47f1-a958-fa22db4b5a76" in response

    # Read
    control = portals.CkanControl(
        baseurl=url, dataset="test-package-file-write-with-resources-inside-folder"
    )
    package = Package(control=control)
    assert package.name == package_name
    assert len(package.resources) == 2
    assert package.resources[0].name == "chunk1"
    assert package.resources[0].path == "chunk1.csv"
    assert package.resources[1].path == "chunk2.csv"


@pytest.mark.vcr
def test_ckan_adapter_publish_list_resources_same_name_in_different_folder(options_lh):
    # Write
    url = options_lh.pop("url")
    control = portals.CkanControl(
        baseurl=url,
        apikey="env:CKAN_APIKEY",
        organization_name="frictionless-data",
    )
    package = Package("data/ckan.package-sameresourcename.yaml")
    package_name = package.name
    response = package.publish(control=control)
    assert "dataset/c979b90a-6662-4b60-b53c-ab5200ca9369" in response

    # Read
    control = portals.CkanControl(
        baseurl=url,
        dataset="test-package-file-write-with-same-resource-name-inside-different-folder",
    )
    package = Package(control=control)
    assert package.name == package_name
    assert len(package.resources) == 2
    assert package.resources[0].name == "chunkf1"
    assert package.resources[0].path == "chunkf1.csv"
    assert package.resources[1].name == "chunkf2"
    assert package.resources[1].path == "chunkf2.csv"


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
    source = TableResource(path="data/table.csv")
    target = source.write(path=baseurl, control=control, format="csv")
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
    source = TableResource(path="data/timezone.csv")
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


# Bugs


def test_ckan_adapter_detects_ckan_wrongly_issue_1479():
    plugin = portals.CkanPlugin()
    adapter = plugin.create_adapter(
        "https://opendata.schleswig-holstein.de/dataset/8049b860-6d5c-4ad8-a584-43bec41a6220/resource/13269a62-71af-499e-b4b2-e28882c4d6c1/download/badegewasser-stammdaten-aktuell.json"
    )
    assert adapter is None
