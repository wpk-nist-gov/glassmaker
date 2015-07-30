"""
Class/routines to suggest compounds to give target elements
"""

import pandas as pd
import os
import periodictable as periodic

import MyDataFrame as MyDF


from collections import OrderedDict as OD

class CompoundSuggester(object):
    """
    Class to handle compound suggestions

    Parameters
    ----------
    rel_files : list
      Names of csv files to read from   glassmaker/src/data directory

    abs_files : list
      paths to csv files to load


    Attributes
    ----------
    self.df : dataframes
       `df` name corresponds to file name.  (E.g, if
       abs_files=['a/b/c.csv'], then have self.c).

    self.query

    """

    def __init__(self,rel_files=['acid.csv','oxide.csv','salt.csv'],
                       abs_files=[]):

        self._df_dict = OD()
        
        self._get_rel_dfs(rel_files)

        self._get_abs_dfs(abs_files)


        self._add_IDS()


    def _get_rel_dfs(self,files,encoding='utf-8'):
        this_dir, this_file = os.path.split(os.path.abspath(__file__))
        data_path = os.path.join(this_dir,'data')

        for f in files:
            path = os.path.join(data_path,f)
            key = os.path.splitext(os.path.basename(f))[0]
            df = pd.read_csv(path,encoding='utf-8')
            self._df_dict[key] = MyDF.MyDataFrame(df)


    def _add_IDS(self):
        """
        add ID column to DataFrames
        """

        for k,df in self._df_dict.iteritems():
            if 'ID' not in df.columns:
                df['ID'] = k


    def query_target_all(self,target,key='Target'):

        L=[]
        for k,df in self._df_dict.iteritems():

            L.append(df.query_target(target,key).basic())

        return pd.concat(L)

        

    def __getattr__(self,name):
        #print name
        return self._df_dict[name]
        
    def __dir__(self):
        heritage = dir(super(self.__class__, self)) # inherited attributes
        hide = []
        show = [k for k in self.__class__.__dict__.keys() +
                self.__dict__.keys() + self._df_dict.keys() if not k in heritage + hide]
        return sorted(heritage + show)    










