#from __future__ import absolute_import

import suggester

_Global_suggester = suggester.CompoundSuggester()


def get_compound_list(element, compound_type, S=None, drop_duplicates=True):
    """
    given an element and compound type, return list of known compounds
    
    Parameters
    ----------
    element : str
        name of element to query
        
    compound_type : str
        type of compounds to return
        one of ['acid','oxide','salt','all']
        
    S : CompoundSuggester or None
        CompoundSuggester to query.  If None, use default suggester
        
        
    Returns
    -------
    out : list
        list of compound formulas with element
    """

    if S is None:
        S = _Global_suggester

    if compound_type == 'acid':
        df = S.acid

    elif compound_type == 'oxide':
        df = S.oxide

    elif compound_type == 'salt':
        df = S.salt

    elif compound_type == 'all':
        df = S

    else:
        raise ValueError(
            'compound_type must be one of ["acid","oxide","salt","all"]')

    out = df.query_target(element)['Formula']  #.tolist()
    if drop_duplicates:
        out = out.drop_duplicates()

    return out.tolist()
