

import periodictable as PT
import periodictable.formulas
from collections import OrderedDict

import numpy as np


class superdict(OrderedDict):
    """
    Constructs an defaultDict with attribute and positional access to data.

    Setting a NEW attribute only creates it on the instance, not the dict.
    Setting an attribute that is a key in the data will set the dict data but 
    will not create a new instance attribute
    """
    
    
    
    def __init__(self,default=None,*args,**kwargs):
        
        super(superdict,self).__init__(*args,**kwargs)
        self._check_keys()
        self._default = default
        
    def _check_keys(self):
        for k in self.keys():
            if type(k) is int:
                raise IndexError('key cannot be ints')
                
    def _getkey(self,key):
        if type(key) is int:
            return self.keys()[key]
        else:
            return key
        
    def __getitem__(self,key):
        skey = self._getkey(key)
        if self.has_key(skey):
            return super(superdict,self).__getitem__(skey)#self._getkey[key])
        else:
            if self._default is None:
                raise IndexError('bad index',key)
            else:
                return self._default
    def __setitem__(self,key,value):
        skey = self._getkey(key)
        return super(superdict,self).__setitem__(skey,value)
    
    def __getattr__(self, attr):
        """
        Try to get the data. If attr is not a key, fall-back and get the attr
        """
        if self.has_key(attr):
            return super(superdict, self).__getitem__(attr)
        else:
            return super(superdict, self).__getattr__(attr)


    def __setattr__(self, attr, value):
        """
        Try to set the data. If attr is not a key, fall-back and set the attr
        """
        if self.has_key(attr):
            super(superdict, self).__setitem__(attr, value)
        else:
            super(superdict, self).__setattr__(attr, value)
            
            
    def __dir__(self):
        heritage = dir(super(self.__class__, self)) # inherited attributes
        hide = [] #attributes to hide
        new = self.keys()
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)    





def my_mix_by_weight(data,scale=False):
    """
    create a mix by weight from data
    
    Parameters
    ----------
    data : list or dict
     If list, [('atom',mass),...]
     If dict, {'atom':mass,...}
     
    Returns
    -------
    formula: periodictable.formulas.formula
     mixture formula
    """
    
    if isinstance(data,(list,tuple)):
        pairs = data[:]
    else:
        pairs = [(k,v) for k,v in data.iteritems()]
    
    pairs = [(PT.formula(f),q) for f,q in pairs if q > 0]

    
    result = PT.formula()
    if len(pairs) > 0:
        # cell mass = mass
        # target mass = q
        # cell mass * n = target mass
        #   => n = target mass / cell mass
        #        = q / mass
        if scale: 
            scale = min(q/f.mass for f,q in pairs)
        else:
            scale = 1.0
        for f,q in pairs:
            result += ((q/f.mass)/scale) * f
        if all(f.density for f,_ in pairs):
            volume = sum(q/f.density for f,q in pairs)/scale
            result.density = result.mass/volume
    return result


from collections import namedtuple  
_singleatom=namedtuple('singleatom',['mass_fraction','atoms'])



class MyFormula(object):
    """
    interface to periodictable
    """
    
    def __init__(self,formula=None,name=None,mass_fraction_volatile=None):
        """
        create a formula with string atom name access
        
        Parameters
        ----------
        formula: str/formula/dict
          if str or formula, single entry
          if dict: mix by mass
          {'atom':mass}
        """

        self.name = name
        self.mass_fraction_volatile = mass_fraction_volatile
        self.formula = formula

        
    def __getitem__(self,key):
        return _singleatom(mass_fraction=self.mass_fraction[key],atoms=self.atoms[key])

    @property
    def formula(self):
        if isinstance(self._formula,str):
            return PT.formula(self._formula)
        else:
            return my_mix_by_weight(self._formula)

    @formula.setter
    def formula(self,formula):
        if isinstance(formula,(str,unicode,PT.formulas.Formula)):
            self._formula = str(formula)
        elif isinstance(formula,(list,tuple)):
            self._formula = OrderedDict([(str(k),v) for k,v in formula])
        elif isinstance(formula,(dict,OrderedDict)):
            self._formula = formula
        elif isinstance(formula,MyFormula):
            self._formula = formula._formula
            self._name = formula._name
            self._mass_fraction_volatile = formula._mass_fraction_volatile
        else:
            raise ValueError('bad formula',formula,type(formula))
        
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,value):
        self._name = value

    @property
    def mass_fraction_volatile(self):
        if self._mass_fraction_volatile is None:
            return 0.0
        else:
            return self._mass_fraction_volatile
    @mass_fraction_volatile.setter
    def mass_fraction_volatile(self,value):
        self._mass_fraction_volatile = value

    @property
    def mass_fraction_non_volatile(self):
        return 1.0 - self.mass_fraction_volatile
        
        
    @property
    def longname(self):
        return str(self.formula)
            
    
    
    @property 
    def atoms(self):
        return superdict(0,[(str(k),v) for k,v in self.formula.atoms.iteritems()])
    
    @property
    def mass_fraction(self):
        return superdict(0.0,[(str(k),v) for k,v in self.formula.mass_fraction.iteritems()])
        
    
    def __repr__(self):
        return repr(self.formula)

    def __str__(self):
        return str(self.formula)
    
    def __getitem__(self,key):
        return _singleatom(mass_fraction=self.mass_fraction[key],atoms=self.atoms[key])
    
    def __getattr__(self,name):
        f = self.formula
        if hasattr(f,name):
            return getattr(f,name)

        if name in self.atoms.keys():
            return self[name]
                
        
    def __dir__(self):
        #heritage = dir(super(self.__class__, self)) # inherited attributes
        heritage = dir(type(self.formula))
        hide = [] #attributes to hide
        new = self.__dict__.keys() + self.atoms.keys() +dir(self.formula)
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)
    


class MyFormulaCollection(object):
    """
    collection of formulas
    """

    def __init__(self,formulas=[]):
        """
        create a collection of formulas
        """

        self.formulas = formulas

    @property
    def formulas(self):
        return [MyFormula(**x) for x in self._formulas]

    @formulas.setter
    def formulas(self,formulas):
        #parsing formulas
        self._formulas = [self._parse_formula(x) for x in formulas]

    def longnames(self):
        return [x.longname for x in self.formulas]

    def names(self):
        return [x.name for x in self.formulas]

    def _parse_formula(self,formula):
        #self._formulas contains dictionaries to
        #be passed to MyFormula
        #i.e, {formula=somthing,name=something}
        if isinstance(formula,dict) and 'formula' in formula.keys():
            return formula
        elif isinstance(formula,MyFormula):
            return dict(formula=formula._formula,name=formula.name,mass_fraction_volatile=formula.mass_fraction_volatile)
        else:
            return dict(formula=str(formula))

    def _parse_key(self,key):
        if type(key) is int:
            return key
        else:
            #first try on longnames
            f = self.formulas
            longnames = self.longnames()
            if key in longnames:
                return longnames.index(key)

            names = self.names()
            if key in names:
                return names.index(key)

        raise IndexError('no key found for',key)
        
    def __getitem__(self,key):        
        return self.formulas[self._parse_key(key)]

    def __setitem__(self,key,value):


        self._formulas[self._parse_key(key)] = self._parse_formula(value)

    def __delitem__(self,key):
        del self._formulas[key]

    def append(self,value):
        self._formulas.append(self._parse_formula(value))


    def __getattr__(self,name):
        if name in self.longnames()+self.names():
            return self.__getitem__(name)


    def __dir__(self):
        heritage = dir(super(self.__class__, self)) # inherited attributes
        hide = [] #attributes to hide
        new = list(set(self.names() + self.longnames()))
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)    

        
    def __repr__(self):
        return repr([repr(x) for x in self.formulas])

    def __str__(self):
        return str([str(x) for x in self.formulas])


class glass(object):
    """
    class for forward glass calculation
    """
    
    def __init__(self,targets={},sources=[],matrix='LiB4O7'):
        """
        initialize glass object
        
        Parameters
        ----------
        target : dict/orderedDict/list of tups
          Ordered{'atom':mass_fraction,...}
          
        source : list
          ['source1','source2',...]
          
        matrix : str
          string formula for matrix
        """
        
        self._targets = superdict(None,targets)
        self._sources = MyFormulaCollection(sources)
        self.matrix = matrix 


    @property
    def targets(self):
        return self._targets

    @property
    def sources(self):
        return self._sources

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self,value):
        self._matrix = MyFormula(value)


    def _get_LHS(self):
        #build matrix equation
        A = np.zeros([len(self._targets)+1]*2)
        print 'shape',A.shape

        for irow,atom in enumerate(self.targets.keys()):
            for icol,source in enumerate(self.sources):
                A[irow,icol] = source.mass_fraction[atom]

            #add in the mass fraction from the matrix?
            A[irow,-1] = self._matrix.mass_fraction[atom]

        #add in total mass row
        for icol,source in enumerate(self.sources):
            A[-1,icol] = source.mass_fraction_non_volatile
        #add in total mass row for matrix
        A[-1,-1] = self.matrix.mass_fraction_non_volatile
        return A
        if np.linalg.det(A)==0:
            raise ValueError('singular matrix')
        return A
    def _get_RHS(self,mass_total):
        y = np.zeros(len(self._targets)+1)
        for irow,atom in enumerate(self.targets):
            y[irow] = self.targets[atom]*mass_total

        y[-1] = mass_total

        return y

            

    
        
        
# from collections import OrderedDict 
# from collections import defaultdict 
# from collections import namedtuple  

# singleatom=namedtuple('singleatom',['mass_fraction','atoms'])



# class MyFormula(object):
#     """
#     interface to periodictable
#     """
    
#     def __init__(self,formula=None):
#         """
#         create a formula with string atom name access
        
#         Parameters
#         ----------
#         formula: input formula
#           -string (to be parsed by perodictable.formula)
#           -periodictable.formula
#         """
        
#         self.formula = formula
#         #self._formula = PT.formula(formula)
        
#     @property
#     def formula(self):
#         print 'hello'
#         return self._formula
    
#     @formula.setter
#     def formula(self,formula):
#         self._formula = PT.formula(formula)
    
#     @property
#     def atoms(self):
#         return defaultdict(int,{str(k):v for k,v in self.formula.atoms.iteritems()})
    
#     @property
#     def mass_fraction(self):
#         return defaultdict(float,{str(k):v for k,v in self.formula.mass_fraction.iteritems()})
        
    
#     def __repr__(self):
#         return repr(self._formula)
    
#     def __getitem__(self,key):
#         return singleatom(mass_fraction=self.mass_fraction[key],atoms=self.atoms[key])
    
#     def __getattr__(self,name):
#         if hasattr(self._formula,name):
#             return getattr(self._formula,name)
        
#     def __dir__(self):
#         #heritage = dir(super(self.__class__, self)) # inherited attributes
#         heritage = dir(type(f1))
#         hide = [] #attributes to hide
#         new = self.__dict__.keys() + dir(self._formula)
#         show = [k for k in new if k not in heritage + hide]
#         return sorted(heritage + show)    
    
            
    
# class MyMix(object):
#     """
#     interface to periodictable
#     """
    
#     def __init__(self,formula=None):
#         """
#         create a formula with string atom name access
        
#         Parameters
#         ----------
#         formula: dict
#           {'atom':mass}
#         """
        
#         self.formula = formula
        
#     def __getitem__(self,key):
#         return singleatom(mass_fraction=self.mass_fraction[key],atoms=self.atoms[key])
    
            
#     @property
#     def formula(self):
#         return PT.formula(self._formula)
    
#     @formula.setter
#     def formula(self,value):
#         if isinstance(value,(str,unicode,PT.formulas.Formula)):
#             self._mix_dic = {str(value):1.0}
#             self._formula = my_mix_by_weight(self._mix_dic)
#         elif isinstance(value,(list,tuple)):
#             self._mix_dic = {str(k):v for k,v in value}
#         else:
#             self._mix_dic = value
            
#         self._formula = my_mix_by_weight(self._mix_dic)
    
#     @property
#     def atoms(self):
#         return defaultdict(int,{str(k):v for k,v in self.formula.atoms.iteritems()})
    
#     @property
#     def mass_fraction(self):
#         return defaultdict(float,{str(k):v for k,v in self.formula.mass_fraction.iteritems()})
        
    
#     def __repr__(self):
#         return repr(self.formula)
    
#     def __getitem__(self,key):
#         return singleatom(mass_fraction=self.mass_fraction[key],atoms=self.atoms[key])
    
#     def __getattr__(self,name):
#         if hasattr(self._formula,name):
#             return getattr(self._formula,name)
        
#     def __dir__(self):
#         #heritage = dir(super(self.__class__, self)) # inherited attributes
#         heritage = dir(type(f1))
#         hide = [] #attributes to hide
#         new = self.__dict__.keys() + dir(self._formula)
#         show = [k for k in new if k not in heritage + hide]
#         return sorted(heritage + show)    
        
