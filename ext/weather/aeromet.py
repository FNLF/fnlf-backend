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

    def tafmetar(self):
        """Uses api.met.no for retrival of norwegian airport codes
        Other:
        http://api.met.no/weatherapi/tafmetar/1.0/?icao=ENTO;content_type=text/plain;content=info

        content:
        tafmetar
        taf
        metar
        info

        """

        metar = []
        taf = []
        finished_metar = False

        for line in urlopen('http://api.met.no/weatherapi/tafmetar/1.0/?icao=%s;content_type=text/plain;content=tafmetar;date=2015-12-14' % self.airport):
            line = line.strip().decode('utf-8')
            if not finished_metar and len(line.strip()) != 0:
                metar.append("%s" % line[:-1])
            elif len(line.strip()) == 0:
                finished_metar = True
                pass
            else:
                if len(line.strip()) != 0:
                    taf.append("TAF %s" % line[:-1])

        return taf, metar
