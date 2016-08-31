import ipywidgets as widgets
from IPython.display import clear_output, HTML, display, Javascript
import pandas as pd
import periodictable as PT
from suggester_interface import get_compound_list, _Global_suggester
from collections import defaultdict


import mix

# visibility stuff
cells_visable = True
def toggle_code_cells(btn):
    global cells_visable
    if cells_visable:
        display(Javascript("$('div.input').hide();"))
        btn.description = "Show Code Cells"
    else:
        display(Javascript("$('div.input').show();"))
        btn.description = "Hide Code Cells"
    cells_visable = not cells_visable


def run_all(ev):
    display(Javascript('IPython.notebook.execute_cells_below()'))


run_button = widgets.Button(description="Create next input")
run_button.on_click(run_all)

toggle_btn = widgets.Button(description="Hide Code Cells")
toggle_btn.on_click(toggle_code_cells)


def display_init():
    """
    code to add run/toggle buttons
    """
    display(run_button)
    display(toggle_btn)



#--------------------------------------------------
# parameters for below
#--------------------------------------------------

_global_element_list = [str(v)
                        for k, v in PT.elements._element.iteritems() if k > 0]


def _sort_element_list(input):
    return sorted(input, key=lambda x: _number_element_map[x])


_number_element_map = defaultdict(lambda: 200, ((str(v),k) for k,v in PT.elements._element.iteritems()))

# element lists
_compound_element_list = {}
for k in ['salt','oxide']:
    _compound_element_list[k] = _sort_element_list(
        _Global_suggester._df_dict[k].Target.unique().tolist()
    )


_element_width = '150px'
_element_height = '55px'

_num_width = '100px'
_num_height = '55px'




#--------------------------------------------------
# element definitions
#--------------------------------------------------
class _single_element(object):
    """
    create a row
    """

    def __init__(self):

        #elemenets
        self._element = widgets.Select(options=_global_element_list,
                                       description='Element',
                                       layout=widgets.Layout(
                                           #flex='0 1 auto',
                                           #height=_element_height,
                                           width=_element_width,
                                           height=_element_height,
                                           #width='60px'
                                       ))

        #blank min
        self._massfrac_min = widgets.BoundedFloatText(min=0., max=1.,description='Min'#  layout=widgets.Layout(
                                                      #     flex='0 1 auto',
                                                      #     width='auto'
                                                      # )
        )

        #blank max
        self._massfrac_max = widgets.BoundedFloatText(min=0., max=1.,description='Max'# ,layout=widgets.Layout(
                                                      #     flex='0 1 auto',
                                                      #     width='auto'
                                                      # )
        )

        # for x in ['massfrac_min', 'massfrac_max']:
        #     getattr(self, '_' + x).margin = 0

        box_layout = widgets.Layout(
            overflow_x='scroll',
            #border='1px solid black',
            width='80%',
            flex_direction='row',
            display='flex'

        )

        self._box = widgets.HBox(layout=box_layout)  #width=(_element_width + 2* _num_width))
        self._box.children = (self._element, self._massfrac_min,
                              self._massfrac_max)

    @property
    def _widget(self):
        return self._box

    @property
    def element(self):
        return self._element.value

    @property
    def massfrac_min(self):
        return self._massfrac_min.value

    @property
    def massfrac_max(self):
        return self._massfrac_max.value

    def display(self):
        return self._box

    @property
    def widget(self):
        return self._box

    def to_dict(self):
        return dict(element=self.element,
                    massfrac_min=self.massfrac_min,
                    massfrac_max=self.massfrac_max)

    def set_by_values(self, element, massfrac_min, massfrac_max):
        self._element.value = element
        self._massfrac_min.value = massfrac_min
        self._massfrac_max.value = massfrac_max

    @classmethod
    def from_values(cls, element, massfrac_min, massfrac_max):
        new = cls()
        new.set_by_values(element, massfrac_min, massfrac_max)
        return new


class _single_element_del(_single_element):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._button_del = widgets.Button(description='remove',
                                          width='80px')
        self._box.children =  (self._button_del, ) + self._box.children 


class elements(object):
    def __init__(self, ncomp=0):

        self._ncomp = widgets.Text(value='0',width='100px')
        self._ncomp.on_submit(self.update_rows)
        self._button_add = widgets.Button(description='add')
        self._button_add.on_click(self._click_button_add)
        self._head = widgets.HBox(children=(widgets.Label(value='Components'),
                                            self._ncomp, self._button_add),
                                  layout=widgets.Layout(width='100%',flex_direction='row'))


        #intial box setup
        self._rows = []
        self._ring = []

        self._box = widgets.VBox()

        self.ncomp = ncomp
        self.update_rows()
        self.update_box()

    def __getitem__(self, i):
        return self._rows[i]

    @property
    def ncomp(self):
        try:
            v = int(self._ncomp.value)
        except:
            v = None
        return v

    @ncomp.setter
    def ncomp(self, val):
        self._ncomp.value = str(val)
        #update
        self.update_rows()

    @property
    def nrow(self):
        return len(self._rows)

    def new_row(self):
        if len(self._ring) > 0:
            return self._ring.pop()
        else:
            new = _single_element_del()
        return new

    def add_row(self):
        #from ring?
        new = self.new_row()
        self._rows.append(new)
        new._button_del.on_click(self._click_button_del_row)

    def pop_row(self, index=-1):
        row = self._rows.pop(index)
        self._ring.append(row)

    def update_rows(self, *args):
        v = self.ncomp
        if v is None:
            return

        while self.nrow < self.ncomp:
            self.add_row()

        while self.nrow > self.ncomp:
            self.pop_row()

        self.update_box()

    def _click_button_add(self, *args):
        self.add_row()
        self.ncomp = self.nrow

    def _click_button_del_row(self, d):
        L = [r._button_del for r in self._rows]
        index = L.index(d)

        self.pop_row()
        self.ncomp = self.nrow

    def update_box(self):
        L = [self._head] + [r._box for r in self._rows]
        self._box.children = tuple(L)

    def display(self):
        return self._box

    @property
    def widget(self):
        return self._box


    def to_df(self):
        return pd.DataFrame([x.to_dict() for x in self])

    def to_dicts(self):
        return [x.to_dict() for x in self]


    def to_list_of_tuples(self):
        out = []
        for x in self.to_dicts():
            t = (x['element'], (x['massfrac_min'], x['massfrac_max']))
            out.append(t)
        return out
        

    def set_by_df(self, df):
        self.ncomp = len(df)
        for row_num, (i, g) in enumerate(df.iterrows()):
            self._rows[row_num].set_by_values(**g.to_dict())

    def set_by_dicts(self,L):
        self.ncomp = len(L)
        for i,d in enumerate(L):
            self[i].set_by_values(**d)

    @classmethod
    def from_df(cls, df):
        new = cls()
        new.set_by_df(df)
        return new


    @property
    def elements(self):
        """list of elements"""
        return [x.element for x in self]



#--------------------------------------------------
# compound stuff
#--------------------------------------------------

class _compound_list_element(object):
    """
    element
    """
    def __init__(self):
        self._element = widgets.Select(options=_global_element_list,
                                       layout=widgets.Layout(
                                           flex='1 1 auto',
                                           width='auto',
                                           height=_element_height
                                       ))
                                       # height=_element_height,
                                       # width='70px')
    @property
    def formula(self):
        return self._element.value

    @property
    def widget(self):
        return self._element

    def set_by_values(self,element):
        try:
            self._element.value = element
        except:
            pass

    def to_dict(self):
        return dict(element=self.formula)



class _compound_list_select(object):
    """
    selector for compound from list
    """

    def __init__(self, compound_type):

        assert compound_type in ['oxide','salt']
        self._compound_type = compound_type

        # element selector
        # options from 
        self._element = widgets.Select(options=_compound_element_list[self._compound_type],
                                       layout=widgets.Layout(
                                           flex='0 0 auto',
                                           width='80px',
                                           height=_element_height
                                       ))

        # compound selector
        self._compound = widgets.Select(options=[],
                                        layout=widgets.Layout(
                                            flex='1 1 auto',
                                            width='auto',
                                            height=_element_height
                                        ))
        self._box = widgets.HBox(children=(self._element, self._compound))

        # monitor events
        self._element.observe(self._populate)

    def _populate(self, sender, *args, **kwargs):
        element_name = self._element.value
        out = get_compound_list(element_name, self._compound_type)

        if out is not None:
            self._compound.options = list(map(str, out))


    @property
    def formula(self):
        return self._compound.value

    def to_dict(self):
        return dict(element=self._element.value, compound=self._compound.value)

    def set_by_values(self, element, compound):
        self._element.value = element
        self._compound.value = compound

    @classmethod
    def from_values(cls, element, compound):
        new = cls()
        new.set_by_values(element, compound)
        return new

    @property
    def widget(self):
        return self._box

    def display(self):
        return self._box


class _compound_list_select_acid(object):
    """
    selector for acid with weight frac of water
    """

    def __init__(self):
        self._compound_type = 'acid'

        # compound selector
        options = get_compound_list('H', 'acid')
        self._compound = widgets.Select(options=options,
                                        layout=widgets.Layout(flex='0 0 auto',
                                                              width='120px',
                                                              height=_element_height))
        self._massfrac = widgets.BoundedFloatText(min=0., max=1.,
                                                  layout=widgets.Layout(flex='2 1 auto'),
                                                  width='auto')

        self._box = widgets.HBox(children=(self._compound,
                                           widgets.Label('MF acid'), self._massfrac),
                                 layout=widgets.Layout(display='flex',
                                                       flex_direction='row'))

    @property
    def massfrac(self):
        return float(self._massfrac.value)


    @property
    def formula(self):
        return [(self._compound.value, self.massfrac),
                ('H2O', 1.0 - self.massfrac)]


    def set_by_values(self, compound, massfrac):
        self._compound.value = compound
        self._massfrac.value = massfrac


    def to_dict(self):
        return dict(compound=self._compound.value, massfrac=self.massfrac)

    @property
    def widget(self):
        return self._box

    def display(self):
        return self._box


class _compound_list_select_manual(object):

    def __init__(self):
        self._compound = widgets.Text(layout=widgets.Layout(flex='1 1 auto',width='auto'))

    def set_by_values(self, compound):
        self._compound.value = compound

    def to_dict(self):
        return dict(compound=self._compound.value)

    @property
    def formula(self):
        return self._compound.value

    @property
    def widget(self):
        return self._compound

    def set_by_values(self, compound):
        self._compound.value = compound



class _compound_generic(object):
    """
    generic compound type
    """

    def __init__(self):
        #compound type
        self._compound_type = widgets.Dropdown(
            options = ['manual','element', 'oxide','salt','acid'],
            layout=widgets.Layout(flex='0 0 auto',
                                  width='100px',
                                  height=_element_height))


        self._button_volatile = widgets.ToggleButton(description='volatile',
                                                     value=False,
                                                     layout=widgets.Layout(
                                                         flex='0 0 auto',
                                                         width='80px'))

        self._button_del = widgets.Button(description='remove',
                                          layout=widgets.Layout(flex='0 0 auto',
                                                                width='80px'))


        self._mass = widgets.Text(layout=widgets.Layout(flex='0 0 auto',
                                                        width='80px'),value='1.0')

        self._box = widgets.HBox(layout=widgets.Layout(
            width='800px',
            height='',
            flex_direction='row',
            display='flex'))

        self._head = (self._button_del, self._button_volatile, widgets.Label('mass'), self._mass,
                      self._compound_type)

        #monitor _compound_type
        self._compound_type.observe(self._populate)

        #init to manual
        self._compound_type.value = 'manual'
        self._populate(None)

    def _populate(self, sender, *args, **kwargs):

        compound_type = self._compound_type.value

        if compound_type == 'manual':
            self._compound =  _compound_list_select_manual()

        elif compound_type == 'element':
            self._compound = _compound_list_element()

        elif compound_type == 'acid':
            self._compound = _compound_list_select_acid()

        else:
            self._compound = _compound_list_select(compound_type)

        self._box.children = self._head + (self._compound.widget,)


    @property
    def widget(self):
        return self._box

    @property
    def formula(self):
        return self._compound.formula

    @property
    def formula_tuple(self):
        return (self.formula, self.mass)

    @property
    def volatile(self):
        return self._button_volatile.value

    @property
    def mass(self):
        return float(self._mass.value)


    def to_dict(self):
        d = self._compound.to_dict()
        d['type'] = self._compound_type.value
        d['mass'] = self._mass.value
        d['volatile'] = self.volatile

        return d

    def set_by_dict(self,d):
        d = d.copy()
        self._compound_type.value = d.pop('type')
        self._mass.value = d.pop('mass')
        self._button_volatile.value = d.pop('volatile')

        self._populate(None)
        self._compound.set_by_values(**d)


    @property
    def volatile(self):
        return self._button_volatile.value

    @property
    def mass(self):
        return float(self._mass.value)




class compound_mix(object):
    """
    create a mixture
    """

    def __init__(self,ncomp=1,name=''):
        self._ncomp = widgets.Text(value='0',
                                   width='100px')

        self._ncomp.on_submit(self.update_rows)
        self._button_add = widgets.Button(description='add')
        self._button_add.on_click(self._click_button_add)

        # a blank delete button for use later
        self._button_del = widgets.Button(description='remove source')

        self._name = widgets.Text(value=name)
        self._head = widgets.HBox(children=(widgets.Label(value='Components'),
                                            self._ncomp, self._button_add,
                                            self._button_del,
                                            self._name))




        # initial setup
        self._rows = []
        self._ring = []

        self._box = widgets.VBox()

        self.ncomp = ncomp
        self.update_rows()
        self.update_box()

    def __getitem__(self,i):
        return self._rows[i]


    @property
    def ncomp(self):
        try:
            v = int(self._ncomp.value)
        except:
            v = None
        return v

    @ncomp.setter
    def ncomp(self, val):
        self._ncomp.value = str(val)
        #update
        self.update_rows()

    @property
    def nrow(self):
        return len(self._rows)

    def new_row(self):
        if len(self._ring) > 0:
            return self._ring.pop()
        else:
            new = _compound_generic()
        return new

    def add_row(self):
        #from ring?
        new = self.new_row()
        self._rows.append(new)
        new._button_del.on_click(self._click_button_del_row)

    def pop_row(self, index=-1):
        row = self._rows.pop(index)
        self._ring.append(row)

    def update_rows(self, *args):
        v = self.ncomp
        if v is None:
            return

        while self.nrow < self.ncomp:
            self.add_row()

        while self.nrow > self.ncomp:
            self.pop_row()

        self.update_box()

    def _click_button_add(self, *args):
        self.add_row()
        self.ncomp = self.nrow 


    def _click_button_del_row(self, d):

        L = [r._button_del for r in self._rows]
        index = L.index(d)

        self.pop_row(index)
        self.ncomp = self.nrow

        #self.update_box()

    def update_box(self):
        L = [self._head] + [r.widget for r in self._rows]
        self._box.children = tuple(L)

    def display(self):
        return self._box

    @property
    def widget(self):
        return self._box


    def to_dicts(self):
        #return {'name':self._name.value, }
        return [x.to_dict() for x in self]

    def set_by_dicts(self,L):
        self.ncomp = len(L)
        for i,x in enumerate(L):
            self[i].set_by_dict(x)


    @property
    def formula(self):
        return [x.formula for x in self]


    @property
    def formula_measured(self):
        return [x.formula_tuple for x in self]


    @property
    def formula_final(self):
        return [x.formula_tuple for x in self if not x.volatile]


    def to_CompoundVolatile(self):
        return mix.CompoundVolatile(measured=self.formula_measured,
                                    final=self.formula_final,
                                    name=None)



class TabSources(object):
    """
    Tab of sources
    """

    def __init__(self,nsource=1):

        self._internal_count = 10000


        # setup header
        self._nsource = widgets.Text(value=str(nsource), width='100px')
        self._nsource.on_submit(self._update_sources)
        self._button_add = widgets.Button(description='add')
        self._button_add.on_click(self._click_button_add_source)
        self._head = widgets.HBox(children=(widgets.Label(value='Sources'),
                                            self._nsource, self._button_add))

        # empty tab widget
        self._sources_widget = widgets.Tab()

        # top level widget is an vbox
        self._widget = widgets.VBox(children=(self._head, self._sources_widget))


        self._sources = []
        self._ring = []



        self._update_sources()


    def _dummy(self, *args):
        self._update_sources()

    def __getitem__(self,i):
        return self._sources[i]


    @property
    def nsources(self):
        try:
            return int(self._nsource.value)
        except:
            return None

    @nsources.setter
    def nsources(self, val):
        self._nsource.value = str(val)
        self._update_sources()


    def _new_source(self):
        # if len(self._ring) > 0 :
        #     return self._ring.pop()
        # else:
        #     return compound_mix()
        return compound_mix()


    def _add_source(self):
        new = self._new_source()
        # tie in deletion
        new._button_del.on_click(self._click_button_del_source)
        self._sources.append(new)

    def _remove_source(self, index=-1):
        row = self._sources.pop(index)
        #self._ring.append(row)

        #activate new
        pos = index - 1
        if pos < 0:
            pos = 0
        if pos >= self.nsources:
            pos = self.nsources - 1

        self._sources_widget.selected_index = pos


    def _update_sources(self,*args):
        v = self.nsources
        if v is None:
            return

        while len(self._sources) < v:
            self._add_source()

        while len(self._sources) > v:
            self._remove_source()

        # update sources_widget
        sw = self._sources_widget
        sw.children = [r.widget for r in self._sources]

        # update title
        # for i in range(self.nsources):
        #     if sw.get_title(i) is None:
        #         sw.set_title(i,self._internal_count)
        #         self._internal_count += 1


        # titles = [self._sources_widgets.get_title(i) for i in range(self.nsources)]

        # print titles

        # for i in range(self.nsources):
        #     self._internal_count += 1
        #     self._sources_widget.set_title(i,str(self._internal_count))



        # for i in range(self.nsources):
        #     self._sources_widget.set_title(i,'Source %i'%i)



    def _click_button_del_source(self, d):
        L = [r._button_del for r in self._sources]
        index = L.index(d)

        self._remove_source(index)

        #self._nsource.value = str(self.nsources - 1)
        self.nsources = len(self._sources)

    def _click_button_add_source(self, *args):
        self._add_source()
        self.nsources = len(self._sources)

    @property
    def widget(self):
        return self._widget


    def to_dicts(self):
        return [x.to_dicts() for x in self]

    def set_by_dicts(self,L):
        self.nsources = len(L)
        for i,x in enumerate(L):
            self[i].set_by_dicts(x)


    def to_CompoundVolatile_list(self):
        return [x.to_CompoundVolatile() for x in self]

    def to_CompoundCollection(self):
        return mix.CompoundCollection(self.to_CompoundVolatile_list())

class _source_line(object):
    """
    container for formula, mass suggested, mass measured
    """

    


class SingleBead(object):
    """
    A simple container for stuff
    """

    def __init__(self,targets, sources):

        self._target_elements = targets
        self._sources = sources


        #black suggestion button
        self._button_suggest_target_mass_fraction = widgets.Button(description='Suggest Target')
        self._button_delete = widgets.Button(description='Delete')
        self._control_widget = widgets.HBox(children=(self._button_suggest_target_mass_fraction,
                                                      self._button_delete))
        

        # targets
        text_layout = widgets.Layout(flex='1 0 auto',width='150px')
        self._target_widget = widgets.HBox(children=tuple(widgets.Text(description=x, layout=text_layout)   for x in targets),
                     layout=widgets.Layout(overflow_x='scroll', width='800px',height='',flex_direction='row',display='flex')
        )

        # button to calculate suggested mass
        self._button_suggest =  widgets.Button(description='Target')
        self._button_suggest.on_click(self._make_suggestion)


        #each row
        self._header = widgets.HBox(children=(widgets.Label(value='ID',width=_num_width),
                                              widgets.Label(value='Measured',width='300px'),
                                              #widgets.Label(value='Final',width='300px'),
                                              widgets.Label(value='Mass Suggested',width=_num_width),
                                              widgets.Label(value='Mass Measured',width=_num_width)))

        self._total_row = self._get_single_row('','Final Total', '', '')
        self._source_rows = [self._get_single_row(str(i), s.name, '', '') for
                             i,s in enumerate(sources)]


        #button to calculate final
        self._button_final = widgets.Button(description='Final')
        self._button_final.on_click(self._get_final)
        self._final = widgets.Text(width='500px')

        items = [self._control_widget, self._target_widget, self._header,  self._total_row] + self._source_rows + \
                [self._button_suggest,self._button_final,self._final]

        self._widgets = widgets.VBox(children=items)


    @property
    def widget(self):
        return self._widgets

    @staticmethod
    def _get_single_row(name, formula_measured, formula_final, suggested='', measured=''):

        items = (widgets.Label(value=name,width=_num_width),
                 widgets.Label(value=formula_measured, width='300px'),
                 #widgets.Label(value=formula_final, width='300px'),
                 widgets.Text(value=suggested, width=_num_width),
                 widgets.Text(value=measured, width=_num_width))

        return widgets.HBox(children=items,
                            layout=widgets.Layout(display='flex',flex_direction='row'))


    def _get_masses(self, col=-2):
        return [_float_or_string(x.children[col].value) for x in self._source_rows]


    def _get_mass_total(self, col=-2):
        return _float_or_string(self._total_row.children[col].value)

    def _get_target_dict(self):
        return {x.description: _float_or_string(x.value) for x in self._target_widget.children}


    def _make_suggestion(self,*args,**kwargs):
        try:
            # self._targets_dict_sug  = {x.description: float(x.value)
            #                            for x in self._target_widget.children}
            # self._mass_total_sug  = float(self._total_row.children[-2].value)
            self._bead_sug = mix.SingleBead.from_targets(self._get_target_dict(),
                                                         self._get_mass_total(col=-2),
                                                         self._sources)
            for i,mass in enumerate(self._bead_sug.masses):
                self._source_rows[i].children[-2].value = str(mass)
        except:
            pass

    def _get_final_bead(self):
        masses = self._get_masses(col=-1)
        mass_tot = self._get_mass_total(col=-1)
        bead_final = mix.SingleBead(self._sources, masses)
        return bead_final

    def _get_final_mass_fraction(self):
        return (self._get_final_bead()
                .final_compound_filtered(elements=self._target_elements,
                                         mass=self._get_mass_total(col=-1))
                .mass_fraction)



    def _get_final(self,*args,**kwargs):
        try:
            # populate box with final info
            mass_frac = (self._get_final_bead()
                         .final_compound_filtered(elements=self._target_elements,
                                                  mass=self._get_mass_total(col=-1))
                         .mass_fraction)

            self._final.value = str(dict(
                self._get_final_mass_fraction()
            ))


        except:
            pass

    def set_by_values(self,target_masses=None,
                      mass_total_suggested=None,
                      mass_total_measured=None,
                      source_masses_suggested=None,
                      source_masses_measured=None,
                      **kwargs):


        if target_masses:
            for i,m in enumerate(target_masses):
                self._target_widget.children[i].value = str(m)


        if mass_total_suggested:
            self._total_row.children[-2].value = str(mass_total_suggested)

        if mass_total_measured:
            self._total_row.children[-1].value = str(mass_total_measured)

        if source_masses_suggested:
            for i,m in enumerate(source_masses_suggested):
                self._source_rows[i].children[-2].value = str(m)

        if source_masses_measured:
            for i,m in enumerate(source_masses_measured):
                self._source_rows[i].children[-1].value = str(m)


        # if done is not None:
        #     self._button_done.value = done




    def to_dicts(self,include_targets=False, include_sources=False):
        out = {}

        if include_targets:
            out['targets'] = self._target_elements
        if include_sources:
            out['sources'] = [x.to_dict() for x in self._sources]

        target_dict = self._get_target_dict()

        out['target_masses'] = [target_dict[k] for k in self._target_elements]

        out['mass_total_suggested'] = self._get_mass_total(col=-2)
        out['mass_total_measured'] = self._get_mass_total(col=-1)

        out['source_masses_suggested'] = self._get_masses(col=-2)
        out['source_masses_measured'] = self._get_masses(col=-1)

        out['done'] = self._button_done.value
        return out



class TabSuggester(object):

    def __init__(self, targets, sources, nsamples=5):

        self._targets = targets
        self._sources = sources



        #setup widget
        self._nsample = widgets.Text(value=str(nsamples), width='100px')
        self._nsample.on_submit(self._update_samples)
        self._button_add_sample = widgets.Button(description='add')
        self._button_add_sample.on_click(self._click_add_sample)

        self._head = widgets.HBox(children=(self._nsample,
                                            self._button_add_sample))

        #empty tab widget
        self._samples_widget = widgets.Tab()


        #progress frame
        self._button_update_progress = widgets.Button(description='update')
        self._button_update_progress.on_click(self._update_progress)
        self._progress_frame = widgets.HTML()

        self._progress_widget = widgets.VBox(children=(
            self._button_update_progress,
            self._progress_frame
        ))

        #top level box
        self._widget = widgets.VBox(children=(self._head,
                                              self._samples_widget,
                                              self._progress_widget))
        self._samples = []

        self._update_samples()


    def __getitem__(self,i):
        return self._samples[i]


    def _update_progress(self,*args,**kwargs):
        self._progress_frame.value = (self
                                      .suggester
                                      .get_state()
                                      .style
                                      .set_table_attributes('class="table"')
                                      .render())

    @property
    def nsamples(self):
        try:
            return int(self._nsample.value)
        except:
            return None

    @nsamples.setter
    def nsamples(self,val):
        self._nsample.value = str(val)
        self._update_samples()

    def _update_suggester(self):
        self._suggester = mix.TargetMassFracSuggester(targets=self._targets,
                                                nsamples=self.nsamples)
        
        self._suggester._samples = []
        for x in self._samples:
            try:
                val = x._get_final_mass_fraction()
                self._suggester.add_sample(**val)
            except:
                pass


    @property
    def suggester(self):
        #only add sources which give complete mass fraction back
        self._update_suggester()
        return self._suggester

    def _new_sample(self):
        return SingleBead(self.suggester.targets.keys(), self._sources)

    def _add_sample(self):
        new = self._new_sample()
        # add click events
        new._button_delete.on_click(self._click_button_delete_sample)
        new._button_suggest_target_mass_fraction.on_click(
            self._click_button_suggest_target_mass_fraction)

        self._samples.append(new)


    def _remove_sample(self, index=-1):
        row = self._samples.pop(index)

    def _click_button_delete_sample(self,d):
        L = [r._button_delete for r in self._samples]
        index = L.index(d)
        self._remove_sample(index)
        self.nsources = len(self._sources)

    def _click_button_suggest_target_mass_fraction(self,d):
        L = [r._button_suggest_target_mass_fraction
             for r in self._samples]
        index = L.index(d)

        d=self.suggester.make_suggestion()
        x = {d[k] for k in self.suggester.targets.keys()}
        self._samples[index].set_by_values(target_masses=x)

    def _update_samples(self,*args,**kwargs):
        v = self.nsamples
        if v is None:
            return

        while len(self._samples) < v:
            self._add_sample()

        while len(self._samples) > v:
            self._remove_sample()

        sw = self._samples_widget
        sw.children = [s.widget for s in self._samples]

    def _click_add_sample(self,*args,**kwargs):
        self._add_sample()
        self.nsamples = len(self._samples)

    @property
    def widget(self):
        return self._widget






#utilities
def _float_or_string(x):
    try:
        val = float(x)
    except:
        val = x

    return val
