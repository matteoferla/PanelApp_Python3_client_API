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
However, on further investigation the next day it was 57 for gene also...
Whereas quering a panel 56 were found:

```python
from panel_app_query import PanelAppQuery
import pandas as pd

pa = PanelAppQuery()
panels = pa.get_dataframe('/panels/234/')
print(sum(pd.Series(panels.genes_confidence_level[0]).astype(int) >=3))
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

returns 49 unique genes (not 57).

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