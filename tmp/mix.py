import periodictable as PT
from  periodictable.formulas import Formula as PTFormula
from collections import OrderedDict,defaultdict
import numpy as np

import pandas as pd
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
        # if not isinstance(self._formula,str):
        #     raise ValueError('bad _formula',self._formula)
        #if isinstance(self._formula,OrderedDict):
        if _is_list_like(self._formula):
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
            #self._formula = str(get_formula(formula))#OrderedDict(formula)
            self._formula = formula
            
        elif _is_dict_like(formula):
            if 'formula' in formula:
                #is a dictionary to be sent to Compound
                self.__dict__ = Compound(**formula).__dict__
            else:
                #self._formula =
                #str(get_formula(formula))#OrderedDict(formula)
                self._formula = [(k,v) for k,v in formula.iteritems()]
            

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
        
        #elif isinstance(self._formula):
            #self._formula = OrderedDict([(str(k),v) for k,v in self._formula.iteritems()])
        elif _is_list_like(self._formula):
            #make sure have string rep for each formula
            pass
        else:
            raise ValueError('bad formula')
            


    @property
    def strformula(self):
        """
        return string formula
        """
        return str(self.formula)#self._formula
        
    @property
    def atoms(self):
        return superdict(0,[(str(k),v) for k,v in self.formula.atoms.iteritems()])
        #return defaultdict(int,[(str(k),v) for k,v in self.formula.atoms.iteritems()])        
    
    @property
    def mass_fraction(self):
        return superdict(0.0,[(str(k),v) for k,v in self.formula.mass_fraction.iteritems()])
        #return defaultdict(float,[(str(k),v) for k,v in self.formula.mass_fraction.iteritems()])

    def mass_fraction_round(self,round=5):
        return superdict(0.0,[(str(k),np.round(v,round)) for k,v in self.formula.mass_fraction.iteritems()])
        
        
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

    def _repr_html_(self):
        return "<p> Compound('{0}',{1}) </p>".format(self._formula,self.name)

        
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


    def to_frame(self):
        measured = self.measured.strformula
        final = self.final.strformula

        if final == measured:
            final = '--'
            
        return pd.DataFrame(np.array([self.name,
                                      measured,
                                      final]).reshape(1,-1),
                                columns=['name','measured','final'])


    def _repr_html_(self):
        """
        table representation
        """

        return self.to_frame()._repr_html_()        


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


    def __getattr__(self,name):
        if name in self.keys():
            return self.__getitem__(name)

    def __add__(self,value):
        """
        add formula and return new collections
        """
        return CompoundCollection(self._formulas + value)

    def append(self,value):
        self._formulas.append(self._parse_formula(value))


    def __len__(self):
        return len(self._formulas)

    
    def copy(self):
        r = CompoundCollection()
        r.__dict__ = self.__dict__.copy()
        
    def __dir__(self):
        heritage = dir(super(self.__class__, self)) # inherited attributes
        hide = [] #attributes to hide
        new = self.keys()
        show = [k for k in new if k not in heritage + hide]
        return sorted(heritage + show)    
    
    def to_dict(self):
        return dict(formulas=self.to_list())

    def to_list(self):
        return [x.to_dict() for x in self.formulas]

    def __repr__(self):
        return "CompoundCollection(%s)"%repr(self.to_dict())
    
    def __str__(self):
        return str(self.to_dict())
        

    def to_frame(self):
        if len(self._formulas)>0:
            return pd.concat([x.to_frame() for x in
                               self.formulas]).reset_index(drop=True)
        else:
            return pd.DataFrame()
        

    def _repr_html_(self):
        return self.to_frame()._repr_html_()





def get_LHS(targets,sources,checks=True):
    """
    build `A` matrix for `A*M=y` equations

    Parameters
    ----------
    targets: list like
      list of target elements

    sources: CompoundCollection
      collection of source molecules and matrix


    checks: bool
      perform checks?


    Returns
    -------
    A: array of dimension (len(targets)+1,len(targets)+1)
      to solve for x=[mass_target[0],mass_target[1],....,mass_matrix]
      solve A*x=y, where y=[mass_final_target[0],...mass_total]
    """

    A = np.zeros([len(targets)+1]*2)

    

    #print len(sources),len(targets),len(sources)
    assert(isinstance(sources,CompoundCollection))
    assert(len(targets)+1 == len(sources))

    #build matrix

    for icol,source in enumerate(sources):
        for irow,atom in enumerate(targets):
            A[irow,icol] = source.measured.mass_fraction[atom]

        #add in total mass row
        A[-1,icol] = source.measured_to_final_conversion

    if checks and np.linalg.det(A) == 0:
        raise ValueError('singular matrix')

    
    return A

def get_RHS(mass_fracs,mass_total,checks=True):
    """
    get y of A*x=y

    Parameters
    ----------
    mass_fracs : list
     should be in order of `targets` in `get_LHS`

    mass_total : float
     total mass of bead

    checks : bool
     perform checks?

    Returns
    -------
    y: array
    """

    y = [mf*mass_total for mf in mass_fracs]
    y.append(mass_total)

    return np.array(y)



def _get_masses(targets,mass_fracs,mass_total,sources,checks=True):
    """
    create system to hit target mass fractions
    """
    
    LHS = get_LHS(targets,sources,checks)
    RHS = get_RHS(mass_fracs,mass_total,checks)

    x = np.linalg.solve(LHS,RHS)
    return x
    



class SingleBead(object):
    """
    container for mix solution
    """

    def __init__(self,sources,masses):
        """
        initialize mix

        Parameters
        ----------
        souces: Compound collection like
          sources (plus matrix) for mixture

        mass_measured:
          masses of each source and matrix
        """


        self._sources = CompoundCollection(sources)
        self.masses = masses


    @staticmethod
    def from_targets(targets,mass,sources,matrix=None,checks=True):
        """
        create a single bead from sources to hit target mass fractions

        Parameters
        ----------
        targets : dict
         {atom:mass_frac}

        mass : float
         total mass of final bead

        sources : CompoundCollection
         sources

        matrix : CompoundVolatile or None
         if None, assume matrix in sources

        check : bool
         perform checks?

        Returns
        -------
        b : SingleBead
        """
        if matrix is None:
            sources_all = sources
        else:
            sources_all = sources +[matrix]

        elements = targets.keys()
        mf = [targets[k] for k in elements]

        masses = _get_masses(elements,mf,mass,sources_all,checks)
        
        return SingleBead(sources_all,masses)


    @property
    def sources(self):
        return self._sources

    @property
    def masses(self):
        assert(len(self._masses)==len(self._sources))
        return self._masses
        
    @masses.setter
    def masses(self,value):
        self._masses = value

    @property
    def masses_final(self):
        """
        masses of each source.final
        """
        return np.array([s.mass_final(m) for m,s in
                 zip(self.masses,self.sources)])

    @property
    def measured_formula(self):
        """
        get measured compound
        """
        return np.array([(s.measured,m) for m,s in
             zip(self.masses,self.sources)])
    @property
    def measured_compound(self):
        return Compound(self.measured_formula)
    
    @property
    def final_formula(self):
        return [(s.final,m) for m,s in
                zip(self.masses_final,self.sources)]
            

    @property
    def final_compound(self):
        """
        mix by mass
        """
        return Compound(self.final_formula)

    def measured_compound_filtered(self,elements,mass,fill='No'):
        """
        get final compound with only selected elements

        Parameters
        ----------
        elements : list
         list of elements to keep

        mass : float
         total mass of final bead

        fill : str
         fill element (placeholder)

        Returns
        -------
        c : Compound
         final bead compound
        """
        c = self.measured_compound
        d={}
        for k in elements:
            d[k] = c.mass_fraction[k]*c.mass

        d[fill] = mass - sum(d.values())

        return Compound(d)



    def final_compound_filtered(self,elements,mass,fill='No'):
        """
        same as measured_compound_filtered, but based on final_formula
        """
        c = self.final_compound

        d={}
        for k in elements:
            d[k] = c.mass_fraction[k]*c.mass

        d[fill] = mass - sum(d.values())

        return Compound(d)
        
        

    def to_frame(self):
        df = self.sources.to_frame()
        df['mass'] = self.masses
        return df

    def _repr_html_(self):
        return self.to_frame()._repr_html_()



def _condition_list(edges,centers,samples):
    """
    condition centers taking sample into account
    """
    assert(len(edges)==len(centers)+1)
    
    
    edges = np.array(edges)
    centers = np.array(centers)
    msk = np.ones(len(centers),dtype=bool)
    
    #make new centers array excluding those already hit by samples
    for s in samples:
        idx = np.digitize([s],edges)-1
#        print s,idx
        if idx<0:
            #lower than LB
            pass
        elif idx==len(centers):
            #above UB
            pass
        else:
            #in edges
            #get rid of old center
            msk[idx] = False
    return centers[msk]
    

class Suggester(object):
    """
    create a series of glasses
    """

    def __init__(self,targets,nsamples=1):
    
        self.targets = targets
        self.nsamples = nsamples
        
        self._samples = []

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self,value):
        self._targets = value
        
    @property
    def samples(self):
        return self._samples
        
    def add_sample(self,**kwargs):
        self.samples.append(kwargs)


    def _digitize_sample(self,sample):
        d={}
        for k,v in sample.iteritems():
            d[k] = np.digitize([v],self._edges[k])[0]
        return d
    

    def set_edges(self):
        self._edges = {}
        self._centers = {}
        
        for k,r in self.targets.iteritems():
            if isinstance(r,float):
                edges  = np.array([-np.inf,np.inf])
                centers = np.linspace(r,r,self.nsamples)
            else:
                edges =np.linspace(r[0],r[1],self.nsamples+1)
                centers = 0.5*(edges[:-1]+edges[1:])

            self._edges[k] = edges
            self._centers[k] = centers
            
            
            
    def make_suggestion(self,force=False):
        self.set_edges()
        d = {}
        for k in self.targets.keys():
            samples = [s[k] for s in self.samples]
            
            #condition centers
            centers = _condition_list(self._edges[k][:],self._centers[k][:],samples)
            if force and len(centers)==0:
                centers = self._centers[k][:]
                
            d[k] = random.sample(centers,1)[0]
        return d

    def get_state(self):
        self.set_edges()
        D = {}
        for k in self.targets.keys():
            #bounds
            edges = list(self._edges[k])
            lb = [-np.inf]+edges
            ub = edges+['np.inf']

            y = [[]]*(self.nsamples+2)

            if len(self.samples)>0:
                for isamp,s in enumerate(self.samples):
                    idx = np.digitize([s[k]],edges)[0]
                    y[idx] = y[idx] + [str(isamp)]

            y = [','.join(yy) for yy in y]
            d={}
            d['lb']=lb
            d['ub']=ub
            d['sample'] = y
            D[k] = pd.DataFrame(d)

        return pd.concat(D,axis=1)#pd.DataFrame(d)
            
        
                

# import random
# def build_suggestions(targets,ranges,nsamples,seed=None):
#     """
#     build random samples for target elements

#     Parameters
#     ----------
#     targets : list
#      list of target elements

#     ranges : list of tuples or floats
#      list of target ranges (min,max) or values (if float)

#     nsamples : int
#      number of samples

#     seed : int
#      random seed.  If None, no seeding.

#     Returns
#     -------
#     y : list of dicts
#      [{target : mass_Fraction,..},...]
#     """

#     if seed is not None:
#         random.seed(seed)


#     L = []
#     for r in ranges:
#         if isinstance(r,float):
#             y = np.linspace(r,r,nsamples)
#         else:
#             y = np.linspace(r[0],r[1],nsamples)


#         L.append(random.sample(y,nsamples))

#     return [dict(zip(targets,v)) for v in zip(*L)]
        
            

# class Suggester(object):
#     """
#     create a series of glasses
#     """

#     def __init__(self,targets,ranges,nsamples=1,seed=None):


#         if _is_dict_like(targets):
#             self.targets = targets.keys()
#             self.ranges = [targets[k] for k in self.targets]
#         else:
#             self.targets = targets
#             self.ranges = ranges
#         self.nsamples = nsamples

#         if seed is None:
#             pass
#         else
#             random.seed(seed)
        

#     @property
#     def targets(self):
#         return self._targets

#     @targets.setter
#     def targets(self,value):
#         self._targets = value

#     @property
#     def ranges(self):
#         return self._ranges

#     @ranges.setter
#     def ranges(self,value):
#         self._ranges = value


#     def set_edges(self):
#         self._edges = []
#         self._centers = []
        
#         for r in self.ranges:
#             if isinstance(r,float):
#                 edges  = np.array([-np.inf,np.inf])
#                 centers = np.linspace(r,r,nsamples)
#             else:
#                 edges =np.linspace(r[0],r[1],nssamples+1)
#                 centers = 0.5*(edges[:-1]+edges[1:])

#             self._edges.append(edges)
#             self._centers.append(centers)

    
    

class glass2(object):
    """
    class for forward glass calculation
    """
    
    def __init__(self,targets={},sources=[],matrix=Compound('LiB4O7',name='lithium_borate')):
        """
        initialize glass object
        
        Parameters
        ----------
        target : list
          list of target elements
          
        source : list
          ['source1','source2',...]
          
        matrix : str
          string formula for matrix (default Compound('LiB4O7',name='lithium_borate'))
        """
        
        self._targets = superdict(targets)
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
        
        x=np.linalg.solve(self._get_LHS(),self._get_RHS(mass_bead))
        return OrderedDict(zip(self.sources.names+[self.matrix.name],x))

    # def to_dict(self):
    #     return {k.lstrip('_'):v for k,v in self.__dict__.iteritems()}


    def to_dict(self):
        return dict(targets=self.targets.to_list(),sources=self.sources.to_dict(),matrix=self.matrix.to_dict())

    
