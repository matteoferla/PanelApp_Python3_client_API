import requests
import dataclasses
import re
from collections import defaultdict

from .basic import PanelAppQueryBasic


class PanelAppQueryParsed(PanelAppQueryBasic):
    """
    The PanelApp API uses Swagger 2.0,
    which is problematic for generating a Python3 SDK (client API)

    The ``get_data`` method is what counts.
    If a route returns a ``results`` entry that is returned, else the whole return.
    """
    # non-defined fields
    extra_fields = defaultdict(list, **{'Panel': [('strs', list, dataclasses.field(default_factory=list)),
                                                  ('genes', list, dataclasses.field(default_factory=list)),
                                                  ('regions', list, dataclasses.field(default_factory=list))],
                                        })
    extra_namespaces = defaultdict(dict, **{})

    def __init__(self):
        # no super!
        self.swagger = requests.get('https://panelapp.genomicsengland.co.uk/api/docs/',
                                    params=dict(format='openapi')).json()
        self.base_url = self.swagger['schemes'][0] + '://' + \
                        self.swagger['host'] + \
                        self.swagger['basePath']
        self.schemata = {route_name: route['get']['responses']['200']['schema'] for route_name, route in
                         self.swagger['paths'].items()}
        self.dataclasses = self._make_dataclasses()

    def get_data(self, route):
        return self.get_formatted_data(route)

    def get_formatted_data(self, route):
        # determine the route name
        if route in self.swagger['paths']:
            route_name = route
        else:
            for route_name in self.swagger['paths']:
                rex = re.sub('\{.*\}', '.*', route_name) + '$'
                if re.match(rex, route):
                    break
            else:
                raise ValueError('Could not match route')
        data = self.get_raw_data(route)
        schema = self.schemata[route_name]
        if '$ref' in schema:
            dc_name = schema['$ref'].split('/')[-1]
            data = [data]
        else:
            dc_name = schema['properties']['results']['items']['$ref'].split('/')[-1]
            # data = data (already a list)
        dc = self.dataclasses[dc_name]
        if len(data):
            datum = data[0]
            self.assert_expected(dc_name, dc, datum)
        results = [dc(**datum) for datum in data]
        self._post_init_results(results)
        return results

    def _make_dataclasses(self):
        """Gene, Panel etc.
        Not implemented.
        """
        # define dataclasses
        dcs = {}
        revisit = []
        for defined in self.swagger['definitions'].keys():
            details = self.swagger['definitions'][defined]
            type_mapper = {'object': dict, 'string': str, 'array': list, 'integer': int, 'boolean': bool}
            fields = []
            for k, v in details['properties'].items():
                if '$ref' in v:
                    defaulter = dataclasses.field(default_factory=dict)
                    fields.append((k, dict, defaulter))
                    # to be corrected later...
                    revisit.append((defined, k, v['$ref']))
                else:
                    typo = type_mapper[v['type']]
                    # if 'required' in details and k in details['required']:
                    # is not good: the required are often missing.
                    defaulter = dataclasses.field(default_factory=typo)
                    fields.append((k, typo, defaulter))
            fields += self.extra_fields[defined]
            namespace = self.extra_namespaces[defined]
            dcs[defined] = dataclasses.make_dataclass(cls_name=defined,
                                                      fields=fields,
                                                      namespace=namespace)
        for defined, attr, instance in revisit:
            child = instance.split('/')[-1]
            dcs[defined].__dataclass_fields__['entity_type'].default_factory = dcs[child]
        return dcs

    def _post_init_results(self, results):
        # sort out crossreferences that are in lists
        pluralised_crosses = {k.lower() + 's': self.dataclasses[k] for k in self.dataclasses.keys()}
        for result in results:
            # a fake postinit
            for pc, cross in pluralised_crosses.items():
                if hasattr(result, pc) and len(getattr(result, pc)):
                    setattr(result, pc, [cross(**item) for item in getattr(result, pc)])
            if hasattr(result, 'confidence_level'):
                cl = getattr(result, 'confidence_level')
                setattr(result, 'confidence_level', int(cl))

    def assert_expected(self, dc_name, dc, datum):
        expected_keys = dc.__dataclass_fields__.keys()
        novel_keys = {k for k in datum.keys() if k not in expected_keys}
        if len(novel_keys):
            raise ValueError(f'{novel_keys} unexpected for {dc_name}')
