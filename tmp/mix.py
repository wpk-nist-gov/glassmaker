import periodictable as PT
from  periodictable.formulas import Formula as PTFormula
from collections import OrderedDict,defaultdict
import numpy as np


#todo : consider changing _formula representation in Compound to list
#of tuples


#dict class wich has order and default values
class superdict(OrderedDict):
    """
    Constructs an OrderedDict with default values that can be accessed by key or position

    Attributes
    ----------
    loc: access by location
    
    """
    
    def __init__(self,default=None,*args,**kwargs):
        super(superdict,self).__init__(*args,**kwargs)
        self._default = default
        
        
    def __getitem__(self,key):
        if self.has_key(key):
            return super(superdict,self).__getitem__(key)#self._getkey[key])
        else:
            if self._default is None:
                raise IndexError('bad index',key)
            else:
                return self._default
            
    def loc(self,key):
        """
        access dict by location
        """
        return self.values()[key]


    def to_list(self):
        return zip(self.keys(),self.values())


def get_formula(data,scale=False):
    """
    recursivily create formula
    
    Parameters
    ----------
    data : list, dict, or string
     if string, get formula of string.
     if list, of form [(formula,mass_frac),...]
     if dict, of form {formula:mass_frac,...}
     
    scale : bool
     if false, don't scale mix (default)
     if true, scale mix
     
    Returns
    -------
    formula : periodic.table.Formula
    """
    if isinstance(data,PTFormula):
        return data
    elif isinstance(data,Compound):
        return data.formula
    elif _is_string_like(data):
        return PT.formula(data)
    elif _is_list_like(data):
        pairs = data[:]
    elif _is_dict_like(data):
        pairs = list(data.iteritems())
    
    else:
        raise ValueError('bad formula',data)


    pairs = [(get_formula(f),m) for f,m in pairs if m>0]

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
    

    

# def my_mix_by_weight(data,scale=False):
#     """
#     create a mix by weight from data
    
#     Parameters
#     ----------
#     data : list or dict
#      If list, [('atom',mass),...]
#      If dict, {'atom':mass,...}
     
#     Returns
#     -------
#     formula: periodictable.formulas.formula
#      mixture formula
#     """
    
#     if isinstance(data,(list,tuple)):
#         pairs = data[:]
#     else:
#         pairs = [(k,v) for k,v in data.iteritems()]
    
#     pairs = [(PT.formula(f),q) for f,q in pairs if q > 0]

    
#     result = PT.formula()
#     if len(pairs) > 0:
#         # cell mass = mass
#         # target mass = q
#         # cell mass * n = target mass
#         #   => n = target mass / cell mass
#         #        = q / mass
#         if scale: 
#             scale = min(q/f.mass for f,q in pairs)
#         else:
#             scale = 1.0
#         for f,q in pairs:
#             result += ((q/f.mass)/scale) * f
#         if all(f.density for f,_ in pairs):
#             volume = sum(q/f.density for f,q in pairs)/scale
#             result.density = result.mass/volume
#     return result


##################################################
#tests
from collections import Mapping
from collections import Iterable

def _is_dict_like(x):
    return isinstance(x,Mapping)

def _is_list_like(x):
    return isinstance(x,(np.ndarray,list,tuple))

def _is_string_like(val):
    """Returns True if val acts like a string"""
    try: val+''
    except: return False
    return True

def _is_iterable(x):
    return isinstance(x,Iterable)    

    
class Compound(object):
    """
    basic Compound container

    Attributes
    ----------
    formula : formula

    name : formula name

    atoms : number of atoms of each element

    mass_fraction : mass fraction of each element



    #internal storage:
    _formula : string, or list of tuples

    _name : string or None
    
    """
    
    
    def __init__(self,formula=None,name=None):
        """
        init

        Parameters
        ----------
        formula : formula like
         formula string, formula dict {string:mass_frac,..},
         Compound, or Compound.to_dict()

        name : name of compound
        """
        self.formula = formula
        #overide name?
        self.name = name


    ###################################################
    #formula
    @property
    def formula(self):
        if isinstance(self._formula,OrderedDict):
            return get_formula(self._formula)
        else:
            return PT.formula(self._formula)

    @formula.setter
    def formula(self,formula):
        if formula is None:
            self._formula = ''

        elif _is_string_like(formula):
            self._formula = str(formula)

        elif _is_list_like(formula):
            self._formula = OrderedDict(formula)

        elif _is_dict_like(formula):
            if 'formula' in formula:
                #is a dictionary to be sent to Compound
                self.__dict__ = Compound(**formula).__dict__
            else:
                self._formula = OrderedDict(formula)
            

        elif isinstance(formula,Compound):
            #compy data
            self.__dict__ = formula.__dict__.copy()

        elif isinstance(formula,PTFormula):
            self._formula = str(formula)
            
        else:
            raise ValueError('bad formula',formula)
            

        if isinstance(self._formula,str):
            #all good
            pass
        
        elif isinstance(self._formula,OrderedDict):
            #make sure have string rep for each formula
            self._formula = OrderedDict([(str(k),v) for k,v in self._formula.iteritems()])
        else:
            raise ValueError('bad formula')
            


    @property
    def sformula(self):
        return self._formula
        
    @property
    def atoms(self):
        return superdict(0,[(str(k),v) for k,v in self.formula.atoms.iteritems()])
        #return defaultdict(int,[(str(k),v) for k,v in self.formula.atoms.iteritems()])        
    
    @property
    def mass_fraction(self):
        return superdict(0.0,[(str(k),v) for k,v in self.formula.mass_fraction.iteritems()])
        #return defaultdict(float,[(str(k),v) for k,v in self.formula.mass_fraction.iteritems()])


    ###################################################
    #name
    @property
    def name(self):
        return self.__dict__.get('_name',None)

    @name.setter
    def name(self,value):
        if value is not None:
            self._name = value
        

    @property
    def longname(self):
        """
        formula longname
        """
        return str(self.formula)
        
    
    def copy(self):
        """
        copy data to new Compound object
        """
        r = Compound()
        r.__dict__ = self.__dict__.copy()
        return r
        
    def __getattr__(self,name):
        if hasattr(self.formula,name):
            return getattr(self.formula,name)


    def to_dict(self):
        return {k.lstrip('_'):v for k,v in self.__dict__.iteritems()}
        
    def __repr__(self):
        return "Compound(%s)"%repr(self.to_dict())

    def __str__(self):
        return str(self.to_dict())

        
    def __dir__(self):
        heritage = dir(type(self.formula))
        hide = [] #attributes to hide
        new = self.__dict__.keys() + dir(self.formula)
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)
        




class CompoundVolatile(object):
    """
    container for volatile formulas

    Attributes
    ----------
    measured : measured compound

    final : final compound
    """

    def __init__(self,measured=None,final=None,name=None):
        """
        create

        Parameters
        ----------
        measured,final : formula like
         formula for measured and final compounds (string, mass_mix dict, Compound)

        Notes
        -----
        if pass CompoundVolatile.to_dict() or CompoundVolatile, will create a copied object
        """

        if _is_dict_like(measured) and 'measured' in measured:
            self.__dict__ = CompoundVolatile(**measured).__dict__
        elif isinstance(measured,CompoundVolatile):
            self.__dict__ = measured.__dict__.copy()
        else:
            self.measured = measured
            self.final = final

        #overide name?
        self.name = name

    @property
    def measured(self):
        #return self.__dict__.get('_measured',None)
        return self._measured

    @measured.setter
    def measured(self,value):
        self._measured = Compound(value)

    @property
    def final(self):
        if self.__dict__.get('_final',None) is None:
            return self.measured
        else:
            return self._final

    @final.setter
    def final(self,value):
        if value is not None:
            self._final = Compound(value)

    @property
    def name(self):
        """
        return, in order, name, measured.name, measured.longname
        """
        if self.__dict__.get('_name',None) is not None:
            return self._name
        elif self.measured.name is not None:
            return self.measured.name
        else:
            return self.measured.longname

    @name.setter
    def name(self,value):
        if value is not None:
            self._name = value

            
    def copy(self):
        """
        copy data to new object
        """
        r = CompoundVolatile()
        r.__dict__ = self.__dict__.copy()
        return r
        
            
    def check_atom(self,atom,significant=5):
        """
        check if specified atom changes between measured and final to
        significant figures
        """

        x0 = self.measured.mass_fraction[atom] * self.measured.mass
        x1 = self.final.mass_fraction[atom] *self.final.mass
        try:
            np.testing.assert_approx_equal(x0,x1,significant=significant)
        except:
            raise ValueError('atom %s chanes by %.5e'%(atom,x0-x1))


    @property
    def measured_to_final_conversion(self):
        """
        conversion from measured to final
        """
        return self.final.mass/self.measured.mass
        
    def mass_final(self,mass_measured):
        """
        get the mass that ends up in bead
        """
        return mass_measured * self.measured_to_final_conversion

    @property
    def final_to_measured_conversion(self):
        return self.measured.mass/self.final.mass
        
    def mass_measured(self,mass_final=1.0):
        """
        get mass measured of mass_final
        """
        return mass_final * self.final_to_measured_conversion

    def to_dict(self):
        d={}
        for k,v in self.__dict__.iteritems():
            kk = k.lstrip('_')
            try:
                vv = v.to_dict()
            except:
                vv = v
            d[kk] = vv
        return d
        
    def __repr__(self):
        return "CompoundVolatile(%s)"%repr(self.to_dict())

    def __str__(self):
        return str(self.to_dict())



#TODO: copy or reference to stuff?
    
class CompoundCollection(object):
    """
    collection of compounds
    """


    def __init__(self,formulas=[]):
        """
        Parameters
        ----------
        formulas : list
          list of strings, compounds, or dicts to be passed to CompoundVolatile
        """
        if _is_dict_like(formulas) and 'formulas' in formulas:
            self.formulas = formulas['formulas']
        else:
            self.formulas = formulas


    @property
    def formulas(self):
        return self._formulas 

    @formulas.setter
    def formulas(self,formulas):
        #parsing formulas
        self._formulas = [self._parse_formula(x) for x in formulas]


    def _parse_formula(self,formula):
        
        try:
            return CompoundVolatile(formula)
        except:
            raise ValueError('bad formula',formula)
        

    @property
    def names(self):
        return [x.name for x in self.formulas]

    def keys(self):
        return self.names
    
    def _parse_key(self,key):
        if type(key) is int:
            return key
        else:
            #first try on longnames
            names = self.names
            if key in names:
                return names.index(key)
            else:
                raise IndexError('key not found',key)

    def __getitem__(self,key):
        if isinstance(key,slice):
            d = self.to_dict()
            d['formulas'] = d['formulas'][key]
            return CompoundCollection(**d)
        else:
            return self.formulas[self._parse_key(key)]

    def __setitem__(self,key,value):
        self._formulas[self._parse_key(key)] = self._parse_formula(value)

    def __delitem__(self,key):
        del self._formulas[key]

    def append(self,value):
        self._formuals.append(self._parse_key(value))


    def __getattr__(self,name):
        if name in self.keys():
            return self.__getitem__(name)

    def __add__(self,value):
        """
        add formula and return new collections
        """
        return CompoundCollection(self._formulas + value)

    def copy(self):
        r = CompoundCollection()
        r.__dict__ = self.__dir__.copy()
        
    def __dir__(self):
        heritage = dir(super(self.__class__, self)) # inherited attributes
        hide = [] #attributes to hide
        new = self.keys()
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)    
    
    def to_dict(self):
        # d={}
        # for k,v in self.__dict__.iteritems():
        #     kk = k.lstrip('_')
        #     try:
        #         vv = v.to_dict()
        #     except:
        #         vv = v
        #     d[kk] = vv
        # return d
        # return {k.lstrip('_'):v for k,v in
        # self.__dict__.iteritems()}
        return dict(formulas=self.to_list())

    def to_list(self):
        return [x.to_dict() for x in self.formulas]

    def __repr__(self):
        return "CompoundCollection(%s)"%repr(self.to_dict())
    
    def __str__(self):
        return str(self.to_dict())
        

    def append(self,value):
        self._formulas.append(self._parse_formula(value))

    



class glass(object):
    """
    class for forward glass calculation
    """
    
    def __init__(self,targets={},sources=[],matrix=Compound('LiB4O7',name='lithium_borate')):
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
        self._sources = CompoundCollection(sources)
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
        self._matrix = CompoundVolatile(value)


    def check_atom(self):
        """
        check sources for changes in target atoms
        """
        for atom in self.targets.keys():
            for source in self.sources + [self.matrix]:
                try:
                    source.check_atom(atom)
                except:
                    raise ValueError('change from measure to final',atom,source)

    def _get_LHS(self):
        """
        get RHS of linear system
        
        RHS is RHS of following system:
        
        rows[0:natoms_spec]:
        sum_{y: x in y}(MF(x,y)*M(y))=MF(x,mix)*mass_total
        
        row[-1]:
        sum(M(y)*final(y)/measured(y))=mass_total
        
        where 
        M(y)=mass of mol y
        MF(x,y)=mass fraction of x in mol y=(nu_x MW_x)/MW_y
        """
        
        #build matrix equation
        
        A = np.zeros([len(self._targets)+1]*2)
        #

        for icol,source in enumerate(self.sources + [self.matrix]):
            for irow,atom in enumerate(self.targets.keys()):
                A[irow,icol] = source.measured.mass_fraction[atom]

            #add in total mass row
            A[-1,icol] = source.measured_to_final_conversion
        
        if np.linalg.det(A)==0:
            raise ValueError('singular matrix')
        return A
    
    def _get_RHS(self,mass_total):
        y = np.zeros(len(self._targets)+1)
        for irow,atom in enumerate(self.targets):
            y[irow] = self.targets[atom]*mass_total

        y[-1] = mass_total

        return y



    def get_solution(self,mass_bead):
        """
        find solution
        """
        
        x=np.linalg.solve(self._get_LHS(),self._get_RHS(total))
        return OrderedDict(zip(self.sources.names+[self.matrix.name],x))

    # def to_dict(self):
    #     return {k.lstrip('_'):v for k,v in self.__dict__.iteritems()}


    def to_dict(self):
        return dict(targets=self.targets.to_list(),sources=self.sources.to_dict(),matrix=self.matrix.to_dict())

    
