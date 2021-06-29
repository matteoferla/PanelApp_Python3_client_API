# PanelApp_Python3_client_API
A preliminary _unofficial_ Python3 client API (SDK) for PanelApp.

PanelApp has an OpenAPI whose specs also have [json definitions](https://panelapp.genomicsengland.co.uk/api/docs/?format=openapi).

It is a Swagger 2.0 app, which means that there would be obsolescence problems 
with the codegens to make a Python3 client API (an SDK).
However, there is an incomplete definitions issue, 
done so from GEL's point of view I am guessing to avoid a circular reference problem. 
That or I have misunderstood what is going on!
Namely in a returned Panel object (from a panel request) the keys `strs`, `genes`, `regions` are returned,
which are arrays of objects that follow the `Str`, `Gene` and `Region` definitions.

## Basics of the API
There are two forms of successful (200) responses.
For a single entry response, the object returned is a `Panel`, `Gene` etc. while for a list of entries, 
the response is a typical Django API or PHP generated one, with `counts`, `previous`, `next`, `results`,
where the parameter `page` controls which subset and is in the URL in `previous`/`next` (or None if absent).

In [panel_app_query/basic.py](panel_app_query/basic.py) is a barebone retriever that returns a dict or a list of dicts.

```python
from panel_app_query import PanelAppQueryBasic

pa = PanelAppQueryBasic()
panels = pa.get_data('/panels/')
panel = pa.get_data('/panels/234/')
genes = pa.get_data('/genes/')
```
A panel from the list contains the keys:
`['id', 'hash_id', 'name', 'disease_group', 'disease_sub_group', 'status', 'version', 'version_created', 'relevant_disorders', 'stats', 'types']`
while from a single query there are additionally `genes`, `strs`, `regions`.

For a gene from a list the keys are:
`['gene_data', 'entity_type', 'entity_name', 'confidence_level', 'penetrance', 'mode_of_pathogenicity', 'publications', 'evidence', 'phenotypes', 'mode_of_inheritance', 'tags', 'panel', 'transcript']`
while `gene_data` dictionary contains the 
keys `['alias', 'biotype', 'hgnc_id', 'gene_name', 'omim_gene', 'alias_name', 'gene_symbol', 'hgnc_symbol', 'hgnc_release', 'ensembl_genes', 'hgnc_date_symbol_changed']`


Note that `confidence_level` for a gene is a string as opposed to an integer and
works like star-ratings, that is it goes from 0 (no support) to 4, and potentially 5 (not implemented as far as I can say).

Note also that for each instance of a gene in a panel there is a new gene instance (which will have the same gene data).

## Dataclasses

If something more advanced is required In [panel_app_query/basic.py](panel_app_query/parsed.py)
is a retriever that returns a list of dataclass instances.

```python
from panel_app_query import PanelAppQuery
pa = PanelAppQuery()
panels = pa.get_data('/panels/234/', formatted=True)  # returns a list of types.Panel
# equivalent to .get_formatted_data
first_panel_gene = panels[0].genes[0]
print(first_panel_gene.entity_name)  # dot notation!
assert isinstance(first_panel_gene, pa.dataclasses['Gene'])
genes = pa.get_data('/genes/')
assert isinstance(genes[0], pa.dataclasses['Gene'])
```

The list of dataclasses are in the attribute `.dataclasses`.

The attribute `swagger` contains the dictionary of definitions. 
Derived from which is `schemata`, which contains the schema for each path.

The class attribute `extra_fields`
(`Dict[str, List[Tuple]]` as accepted by the `dataclasses.make_dataclass` factory)
can be (and is) used to add custom fields (in addition to the openAPI defined one) for a given dataclass name.
The class attribute `extra_namespaces` (`Dict[str, Dict[str, Callable]]`) is used to assign methods to a given dataclass.
See [Python documentation for dataclasses](https://docs.python.org/3/library/dataclasses.html) for more.
The latter can be used therefore to add methods to the dataclasses for extra functionality.
Do note `__post_init__` is not used. And the PanelAppQueryParsed method `_post_init_results` is called after 
all the results are initialised —the lists of dataclass instances aren't handed 
within the dataclass definitions (sloppy coding).

## Pandas

```python
from panel_app_query import PanelAppQuery
pa = PanelAppQuery()
genes = pa.get_dataframe('/genes/')
subset = genes.loc[(genes.panel_id == 234) & (genes.confidence_level >= 3)]
# in a Jupyter notebook:
subset
```

## Uptodateness

The data one can download from the browser for a panel may differ from that from the API.
The gene list for the panel (`len(subset)`) above contained 54 green genes while the website listed 57!
To get the web version:

```python
from panel_app_query import PanelAppQuery
web = PanelAppQuery.retrieve_web_panel(234, '34')
print( len(web) ) # pd.DataFrame   # 57
print( len(web['Entity Name'].unique()) )  # 57
```
However, on further investigation the next day it was 57 for gene, but that is deceiving!

Whereas querying a panel 56 were found:

```python
from panel_app_query import PanelAppQuery
import pandas as pd

pa = PanelAppQuery()
panels = pa.get_dataframe('/panels/234/')
confidence_levels = pd.Series(panels.genes_confidence_level[0]).astype(int)
print(sum(confidence_levels >=3))
```
returns 56.

However... as mentioned a gene is not a single entity.

```python
from panel_app_query import PanelAppQuery
pa = PanelAppQuery()
genes = pa.get_dataframe('/genes/')
subset = genes.loc[(genes.panel_id == 234) & (genes.confidence_level >= 3)]
len(subset.entity_name.unique())
```

returns 52 unique genes (not 57).

Whereas
```python
from panel_app_query import PanelAppQuery
import pandas as pd

pa = PanelAppQuery()
panels = pa.get_dataframe('/panels/234/')
entity_names = pd.Series(panels.genes_entity_name[0])
confidence_levels = pd.Series(panels.genes_confidence_level[0]).astype(int)
len(entity_names[confidence_levels >=3].unique())
```
returns 56 (all).

The odd one out in web is 'ISCA-37432-Loss', which is a region not a gene.

So the `/panels/` route is up-to-date, while `/genes/` is not, but returns redundancies.

The genes that are absent cannot be explained by me.

```python
absentees = set(web['Entity Name'].unique()) - set(subset.entity_name.unique())
web.loc[web['Entity Name'].isin(absentees)]\
    [['Entity Name', 'Entity type', 'ready', 'Flagged', 'GEL_Status', 'UserRatings_Green_amber_red' ]]\
    .sort_values('Entity Name').to_markdown()
```


|    | Entity Name     | Entity type   | ready   | Flagged   |   GEL_Status | UserRatings_Green_amber_red   |
|---:|:----------------|:--------------|:--------|:----------|-------------:|:------------------------------|
| 12 | EYA1            | gene          | True    | False     |            3 | 100;0;0                       |
| 14 | FRAS1           | gene          | True    | False     |            3 | 100;0;0                       |
| 15 | FREM1           | gene          | True    | False     |            3 | 100;0;0                       |
| 56 | ISCA-37432-Loss | region        | False   | False     |            3 | 0;0;0                         |
| 32 | LRIG2           | gene          | True    | False     |            3 | 100;0;0                       |

These genes do exist, but for other panels in the gene list:

```python
absentee_subset = genes.loc[(genes.entity_name.isin(absentees))]
print(subset[['entity_name', 'panel_name', 'panel_id']].sort_values('entity_name').to_markdown())
```

|       | entity_name   | panel_name                                           |   panel_id |
|------:|:--------------|:-----------------------------------------------------|-----------:|
| 32444 | EYA1          | Severe Paediatric Disorders                          |        921 |
| 21614 | EYA1          | Hearing loss                                         |        126 |
| 21981 | EYA1          | Hearing loss                                         |        126 |
| 17354 | EYA1          | Fetal anomalies                                      |        478 |
| 23902 | EYA1          | Intellectual disability                              |        285 |
| 10395 | EYA1          | Unexplained kidney failure in young people           |        156 |
| 24413 | EYA1          | Intellectual disability                              |        285 |
| 25726 | EYA1          | Intellectual disability                              |        285 |
| 19728 | EYA1          | DDG2P                                                |        484 |
| 19804 | EYA1          | DDG2P                                                |        484 |
|  7552 | EYA1          | Ductal plate malformation                            |        209 |
| 27371 | EYA1          | Structural eye disease                               |        509 |
|  5319 | EYA1          | Deafness and congenital structural abnormalities     |        251 |
| 28071 | EYA1          | Groopman et al 2019 - Genes with diagnostic variants |        720 |
| 30178 | EYA1          | Severe Paediatric Disorders                          |        921 |
| 10274 | EYA1          | Unexplained kidney failure in young people           |        156 |
| ....  | ....          |    ....  | ....          |      
