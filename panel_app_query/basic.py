import requests
import re


class PanelAppQueryBasic:
    """
    The ``get_data`` method is what counts.
    If a route returns a ``results`` entry that is returned, else the whole return.

    This class does not parse the data into dataclasses.
    """

    def __init__(self):
        self.base_url = 'https://panelapp.genomicsengland.co.uk/api/v1'

    def get_data(self, route):
        # overridden...
        return self.get_raw_data(route)

    def get_raw_data(self, route):
        if route[0] != '/':
            route = '/'+route
        url = f'{self.base_url}{route}'
        done = False
        # typical output...
        # {'count': 32688,
        #  'next': 'https://panelapp.genomicsengland.co.uk/api/v1/genes/?format=json&page=2',
        #  'previous': None,
        #  'results':
        data = []
        params = dict(format='json')
        while not done:
            reply = requests.get(url, params=params)
            assert reply.status_code == 200, f'{url}?{"&".join(k + "=" + v for k, v in params.items())} gave status_code {reply.status_code}'
            reply_data = reply.json()
            if 'results' not in reply_data:
                return reply_data  # its a single entry anyway.
            else:
                # its a multivalue
                data.extend(reply_data['results'])
                ## proceed
                if 'next' in reply_data and reply_data['next']:  ##the last one is None/null.
                    params['page'] = int(re.search('page=(\d+)', reply_data['next']).group(1))
                else:
                    done = True
        return data
