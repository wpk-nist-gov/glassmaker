"""
wrap dataframe with some convenience functions
"""

import pandas as pd

class MyDataFrame(pd.DataFrame):

    def __init__(self, *args, **kw):
        super(MyDataFrame, self).__init__(*args, **kw)
        if len(args) == 1 and isinstance(args[0], MyDataFrame):
            args[0]._copy_attrs(self)

    def _copy_attrs(self, df):
        for attr in self._attributes_.split(","):
            df.__dict__[attr] = getattr(self, attr, None)

    def basic(self,rows=None,cols=['ID','Name','Formula',
                                   'CAS','Target','mass_frac']):
        """
        print basic info
        """
        if rows is None:
            rows = slice(None)
        return self.loc[rows,cols]


    def query_target(self,target,key='Target'):
        """
        return subframe with self[key] == target
        """
        return self[self[key] == target]
            
    def query_target_index(self,target,key='Target'):
        """
        find indicies for rows with self[key] == target
        """
        return self[self[key] == target].index
            
            
    @property
    def _constructor(self):
        return MyDataFrame
        #below no longer seems to work?
        # def f(*args, **kw):
        #     df = MyDataFrame(*args, **kw)
        #     self._copy_attrs(df)
        #     return df
        # return f

