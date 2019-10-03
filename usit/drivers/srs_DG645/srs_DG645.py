#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supported instruments (identified):
- 
"""


class Driver():
    
    category = 'Function generator'
    
    def __init__(self):
        
        self.conv = ['T0','T1','A','B','C','D','E','F','G','H']
        self.conv2 = ['T0','AB','CD','EF','GH']
        
        for i in self.conv2:
            setattr(self,f'channel{i}',Channel(self,i))
    
        
    def set_frequency(self,frequency):
        self.write(f'TRAT{frequency}')
    def get_frequency(self):
        return self.query('TRAT?')
    
    def ad_delay(self,channel, delay):
        if len(channel) == 2:
            ch1 = str(self.conv.index(channel[0]))
            ch2 = str(self.conv.index(channel[1]))
        else:
            ch1 = '0'
            ch2 = str(self.conv.index(channel))
        self.write(f'DLAY{ch2},{ch1},{delay}')

#################################################################################
############################## Connections classes ##############################
class Driver_VXI11(Driver):
    def __init__(self,address='169.254.166.210', **kwargs):
        import vxi11 as v

        self.inst = v.Instrument(address)
        Driver.__init__(self, **kwargs)

    def query(self, cmd, nbytes=1000000):
        """Send command 'cmd' and read 'nbytes' bytes as answer."""
        self.write(cmd+'\n')
        r = self.read(nbytes)
        return r
    def read(self,nbytes=1000000):
        return self.inst.read(nbytes)
    def write(self,cmd):
        self.inst.write(cmd)
    def close(self):
        self.inst.close()
############################## Connections classes ##############################
#################################################################################


class Channel():
    def __init__(self,dev,channel):
        self.channel = str(channel)
        self.dev     = dev
    
    def set_amplitude(self,amplitude):
        self.dev.write(f'LAMP{self.dev.conv2.index(self.channel)},{amplitude}')
    def get_amplitude(self):
        return float(self.dev.query(f'LAMP?{self.dev.conv2.index(self.channel)}'))
    def set_polarity(self,polarity):
        self.dev.write(f'LPOL{self.dev.conv2.index(self.channel)},{polarity}')
    def get_polarity(self):
        return float(self.dev.query(f'LPOL?{self.dev.conv2.index(self.channel)}'))
    def set_offset(self,offset):
        self.dev.write(f'LOFF{self.dev.conv2.index(self.channel)},{offset}')
    def get_offset(self):
        return float(self.dev.query(f'LOFF?{self.dev.conv2.index(self.channel)}'))
    

            
    

if __name__ == '__main__':
    from optparse import OptionParser
    import inspect
    import sys
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                  offset change : DG645 AB -o 3     3v level offset on AB
                  delay change : DG645 AB -d 10e-6 
                  delay wrt t0 : DG645 A -d 10e-6
                  trigger      : DG645 -f 1000000    
                  polarity     : DG645 AB -p 1  / DG645 AB -p 0
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="command", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="query", default=None, help="Set the query to use." )
    parser.add_option("-d", "--delay", type="str", dest="delay", default=None, help="Set the delay (s)")
    parser.add_option("-x", "--display", action = "store_true", dest ="display", default=False, help="disp")
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the amplitude (V)")
    parser.add_option("-f", "--frequency", type="str", dest="frequency", default=None, help="Set the frequency (Hz)")
    parser.add_option("-p", "--polarity", type="str", dest="polarity", default=None, help="Set the level polarity if 1, then up if 0, then down")
    parser.add_option("-o", "--offset", type="str", dest="offset", default=None, help="Set the offset")
    parser.add_option("-i", "--address", type="string", dest="address", default='169.254.166.210', help="Set ip address" )
    (options, args) = parser.parse_args()

    chan = []
    conv = ['T0','T1','A','B','C','D','E','F','G','H']
    conv2 = ['T0','AB','CD','EF','GH']
    # Errors for options that do not require a channel input
    # command, query, display, amplitude, freq, polarity, level

    if (options.amplitude) or (options.delay) or (options.pol) or (options.offset):
        if (len(args) == 0):
            print('\nYou must provide at least one edge\n')
            sys.exit()
        if (options.pol) or (options.amplitude) or (options.offset):
            if (len(args[0])==1):
                print('\nYou must provide a channel')
                sys.exit()
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
        else:       
            print('\nYou must provide a channel or edge')
            sys.exit()
    if (options.display) and (len(args) !=0):
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
        else:       
            print('\nYou must provide a channel or edge')
            sys.exit()
    
    
    ### Start the talker ###
    I = Driver(address=options.address)
    
    if options.query:
        print('\nAnswer to query:',options.query)
        rep = I.query(options.query)
        print(rep,'\n')
    elif options.command:
        print('\nExecuting command',options.command)
        I.write(options.command)
        print('\n')
        
    if options.delay:
        I.ad_delay(chan, options.delay)
    if options.amplitude:
        I.amplitude(chan, options.amplitude)
    if options.frequency: 
        I.frequency(options.frequency)
    if options.polarity:
        I.polarity(chan,options.polarity)
    if options.offset: 
        I.offset(chan,options.offset)
    if options.display:
        I.display(chan)
    
    sys.exit()
    

