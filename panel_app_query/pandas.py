from .basic import PanelAppQueryBasic


class PanelAppQueryPandas(PanelAppQueryBasic):

    def get_dataframe(self, route):
        data = super().get_raw_data(route)
        if isinstance(data, dict):
            data = [data]
        flat_data = [self._flatted_entry(datum) for datum in data]
        import pandas as pd
        return pd.DataFrame(flat_data)

    def _flatted_entry(self, entry):
        flat = {}
        for k, v in entry.items():
            if isinstance(v, dict):
                for inner_k, inner_v in v.items():
                    flat[k+'_'+inner_k] = inner_v
            elif isinstance(v, list) and len(v) and isinstance(v[0], dict):
                flipped = {vvk: [] for vvk in v[0]}
                for vv in v:
                    for vvk, vvv in vv.items():
                        flipped[vvk].append(vvv)
                for inner_k, inner_vs in flipped.items():
                    flat[k + '_' + inner_k] = inner_vs
            elif k == 'confidence_level':
                flat[k] = int(v)
            else:
                flat[k] = v
        return flat
