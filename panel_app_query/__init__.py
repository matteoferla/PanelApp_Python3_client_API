from .basic import PanelAppQueryBasic
from .parsed import PanelAppQueryParsed
from .pandas import PanelAppQueryPandas

import pandas as pd
import io
import requests

class PanelAppQuery(PanelAppQueryParsed, PanelAppQueryPandas):

    def get_data(self, route, formatted: bool = True):
        if formatted:
            return self.get_raw_data(route)
        else:
            return self.get_formatted_data(route)

    @staticmethod
    def retrieve_web_panel(panel_id: int, confidences: str = '01234'):
        confidences = ''.join(sorted(confidences))
        reply = requests.get(f'https://panelapp.genomicsengland.co.uk/panels/{panel_id}/download/{confidences}/')
        table_handle = io.StringIO(reply.text)
        return pd.read_csv(table_handle, sep='\t')
