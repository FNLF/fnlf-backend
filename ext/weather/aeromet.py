"""

    Aeromet
    =======
    
    Just download metar and taf (raw data) from NOAA
    
    No parsing here
    
"""

from urllib.request import urlopen

class Aeromet():
    
    airport = None
    
    def __init__(self, airport):
        
        self.airport = airport.upper()
        

    def metar(self):
        metar = ""
        for line in urlopen('http://tgftp.nws.noaa.gov/data/observations/metar/stations/%s.TXT' % self.airport):
            metar += "%s " % line.decode("utf-8").strip()
                
        return metar.strip()

    def taf(self):
        taf = ""
        for line in urlopen('http://tgftp.nws.noaa.gov/pub/data/forecasts/taf/stations/%s.TXT' % self.airport):
            taf += "%s " % line.decode("utf-8").strip()
                
        return taf.strip()
    
    def shorttaf(self):
        shorttaf = ""
        for line in urlopen('http://tgftp.nws.noaa.gov/pub/data/forecasts/shorttaf/stations/%s.TXT' % self.airport):
            shorttaf += "%s " % line.decode("utf-8").strip()
                
        return shorttaf.strip()