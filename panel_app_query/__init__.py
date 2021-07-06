from .basic import PanelAppQueryBasic
from .parsed import PanelAppQueryParsed
from .pandas import PanelAppQueryPandas

import io
import requests

class PanelAppQuery(PanelAppQueryParsed, PanelAppQueryPandas):
    """
    see GitHub readme.

    * ``get_raw_data(route)``  == ``get_data(route, formatted=False)``
    * get_formatted_data(route)  == ``get_data(route, formatted=True)``
    * get_dataframe(route)
    """

    def get_data(self, route, formatted: bool = True):
        """
        retrieves the data.

        :param route: string like "/panels/" see API page or ``.schemata.keys()``.
        :param formatted: unformatted is dicts while formatted is dataclasses
        :return:
        """
        if formatted:
            return self.get_raw_data(route)
        else:
            return self.get_formatted_data(route)

    @staticmethod
    def retrieve_web_panel(panel_id: int, confidences: str = '01234'):
        """
        Retrieves the panel from the web.
        The reason for this is that the data may differ.

        :param panel_id:
        :param confidences:
        :return:
        """
        import pandas as pd
        confidences = ''.join(sorted(confidences))
        reply = requests.get(f'https://panelapp.genomicsengland.co.uk/panels/{panel_id}/download/{confidences}/')
        table_handle = io.StringIO(reply.text)
        return pd.read_csv(table_handle, sep='\t')
