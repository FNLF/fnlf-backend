"""

    Aeromet
    =======
    
    Just download metar and taf (raw data) from NOAA
    
    No parsing here
    
"""

from urllib.request import urlopen
import datetime

class Aeromet():
    
    airport = None
    
    def __init__(self, icao):
        
        self.icao = icao.upper()
        self.noaa = 'http://tgftp.nws.noaa.gov/data'
        

    def metar(self):
        metar = ""
        for line in urlopen('%s/observations/metar/stations/%s.TXT' % (self.noaa, self.icao)):
            metar += "%s " % line.decode("utf-8").strip()
                
        return metar.strip()

    def taf(self):
        taf = ""
        for line in urlopen('%s/forecasts/taf/stations/%s.TXT' % (self.noaa, self.icao)):
            taf += "%s " % line.decode("utf-8").strip()
                
        return taf.strip()
    
    def shorttaf(self):
        shorttaf = ""
        for line in urlopen('%s/forecasts/shorttaf/stations/%s.TXT' % (self.noaa, self.icao)):
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

        for line in urlopen('http://api.met.no/weatherapi/tafmetar/1.0/?icao=%s;content_type=text/plain;content=tafmetar;date=%s' % (self.icao, datetime.datetime.now().strftime('%Y-%m-%d'))):
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
