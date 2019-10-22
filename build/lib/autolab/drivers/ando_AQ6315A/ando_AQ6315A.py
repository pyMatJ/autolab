#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""

import os
from numpy import savetxt,linspace
import pandas


class Driver():
    
    category = 'Spectrum analyser'
    
    def __init__(self):

        for i in ['A','B','C']:
            setattr(self,f'trace{i}',Traces(self,i))
    
    
    ### User utilities
    def get_data_traces(self,traces=[],single=None):
        """Get all traces or the ones specified"""
        #if single: self.single()   # must verify whether finished sweeping
        if traces == []: traces = ['A','B','C']
        for i in traces:
            getattr(self,f'trace{i}').get_data()
        
    def save_data_traces(self,filename,traces=[],FORCE=False):
        if traces == []: traces = ['A','B','C']
        for i in traces:
            getattr(self,f'trace{i}').save_data(filename=filename,FORCE=FORCE)
        
    ### Trigger functions
    def single(self):
        s = self.write("SGL")
        return s
    def run(self):
        self.write('RPT')
        
        
    def get_driver_model(self):
        model = []
        for i in ['A','B','C']:
            model.append({'element':'module','name':f'line{i}','object':getattr(self,f'trace{i}'), 'help':'Traces'})
        model.append({'element':'action','name':'run','do':self.run,'help':'Set run mode'})
        model.append({'element':'action','name':'single','do':self.single,'help':'Set single mode'})
        return model
        

#################################################################################
############################## Connections classes ##############################
class Driver_VISA(Driver):
    def __init__(self, address='GPIB0::2::INSTR', **kwargs):
        import visa as v
    
        r          = v.ResourceManager()
        self.scope = r.get_instrument(address)
        Driver.__init__(self)

    def query(self,query,length=1000000):
        self.write(query)
        r = self.read(length=length)
        return r
    def write(self,query):
        self.string = query + '\n'
        self.scope.write(self.string)
    def read(self,length=10000000):
        rep = self.scope.read()
        return rep
        
############################## Connections classes ##############################
#################################################################################


class Traces():
    def __init__(self,dev,trace):
        self.trace     = str(trace)
        self.dev       = dev
        self.data_dict = {}
        
    def get_data(self):
        self.data        = self.query(f"LDAT{self.trace}").split(',')[1:]
        self.data        = [float(self.data[i]) for i in range(len(self.data))]
        self.frequencies = self.get_frequencies(self.data)
        return self.frequencies,self.data
    
    def get_data_dataframe(self):
        frequencies,data              = self.get_data()
        self.data_dict['frequencies'] = self.frequencies
        self.data_dict['amplitude']   = self.data
        return pandas.DataFrame(self.data_dict)
    
    def save_data(self,filename,FORCE=False):
        temp_filename = f'{filename}_AQ6315ATR{self.trace}.txt'
        if os.path.exists(os.path.join(os.getcwd(),temp_filename)) and not(FORCE):
            print('\nFile ', temp_filename, ' already exists, change filename or remove old file\n')
            return
        
        savetxt(temp_filename,(self.frequencies,self.data))

    def set_start_wavelength(self,value):
        self.dev.write(f'STAWL {value}')
    def set_stop_wavelength(self,value):
        self.dev.write(f'STPWL {value}')
    def get_start_frequency(self):
        return float(self.dev.query("STAWL?"))
    def get_stop_frequency(self):
        return float(self.dev.query("STPWL?"))
    def get_frequencies(self,data):
        start = self.get_start_frequency()
        stop  = self.get_stop_frequency()
        return linspace(start,stop,len(data))
    
    def get_driver_model(self):
        model = []
        model.append({'element':'variable','name':'start_wavelength','write':self.set_start_wavelength,'type':float,'help':'Start wavelength of the window'})
        model.append({'element':'variable','name':'stop_wavelength','write':self.set_stop_wavelength,'type':float,'help':'Stop wavelength of the window'})
        model.append({'element':'variable','name':'start_frequency','read':self.get_start_frequency,'type':float,'help':'Start frequency of the window'})
        model.append({'element':'variable','name':'stop_frequency','read':self.get_stop_frequency,'type':float,'help':'Stop frequency of the window'})
        model.append({'element':'variable','name':'spectrum','read':self.get_data_dataframe,'type':pandas.DataFrame,'help':'Current spectrum'})
        return model
    
    