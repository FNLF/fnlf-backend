"""

Avviksrapportering applikasjon

@note: workflow kan feks være readonly, så kan dette rutes via en egen (flask) ressurs for å sette den!

@todo: Observations need an initializing pre_insert/POST to init workflows! 
       Or rather a after with partc_internal since it's a readonly field
       
id    referanse index    int    Et nummer eller alpha som menneskelig referanse                    
type    type    dict    Type som i uheldig event/næruhell/uhell/ulykke    Referanse               
when    når    isodate    Tid og dato                    
involved[{}]    involverte    dict    

Snapshot av involverte personer

{medlemsnr, lisenser[], hopp{tot, år}, utstyr {evt ref utstyrsdb, bekledning etc}, medlemsskap[], forsikring[], lokal hi (fra hovedmedlemsskapet, alle medlemsklubbenes hi'er legges også til som wathcers) Pakket selv her?
    Snapshot               
organisation[{}]    organisering    dict    

Organiserende klubb og aktuelle roller - klubbinfo

{hl, hfl, hi, hm, pilot, lokalisasjon, fly}
    Snapshot               
weather    været    dict    Kan også hente fra nærmeste flyplass (definert i klubbdefinisjonen), api.met.no for gjeldende tidspunkt samt manuell innlegging av temperatur både bakke og oppe, vindforhold samt skydekke    Snapshot samt manuellt               
rating    gradering    int    Gradering av avviket fra 1-10(?)                    
event[]    avvik/hendelsesforløp    dict    Tidlinje med root cause(s), "tennpunkt" og konsekvenser. Baserer på snapshots fra template for avvik. Her kan også utstyr hentes fra utstyrsdatabasen direkte (når den kommer) ved å legge til "Utstyr" under eventen. Samme for ...    Objekt med kopier av faktor maler som manuellt blir tilpasset               
related[]    andre relaterte    list    Relaterte avvik    Referanser               
labels[]    labels    list    Liste med labels for å merke avviket                    
watchers[]    watchers    dict    Alle involverte i rapporten blir automatisk lagt til, andre kan legge seg til. Varsles ved hver endring (bruker diff funksjonen i eve) Eller er dette "watchers" collection??                    
files    fil vedlegg    media    (warning) Skal være "list of media" Vedlegg til rapporten, alle format tilgjengelige. NB: prøv å hente mest mulig metadata, feks pdf2txt etc. Kan dette legges til for hver event også kanskje??    Referanser (gridfs)               
owner    nåværnde eier    int    medlemsnummer. Eller bør denne inn i workflow direkte??    Referanse               
audit    audit    dict    En audit trail? Overføring av eierskap via workflow? Hvor kommer Oplog inn?                    
workflow[{}]    workflow    dict    Et workflow objekt fra en workflow template    Initiell snapshot               
     Fritekst    dict    Fritekst felter for HL, HI, Fagsjef, SU (andre?)                    
     Kommentarer    dict    Standard kommentarfelt, timestamped, medlemsnummer (ref), timestamp, kommentar (filer?)                    
actions[{}]    Tiltak    dict    

En liste over tiltak, lokalt og sentralt

{tiltak beskrivelse (task), av, for [], opprettet, frist, gjennomført, gjennomført av}
                    
acl[{}]    acl    dict    Liste over tilgang via verb


    @todo: Add autogenerating id for observation in pre hook
    @todo: add schema for organisation or club + location
"""

import observation_components

_schema = {'id': {'type': 'integer',
                  'required': True},
           'title': {'type': 'string'},
           'type': {'type': 'dict'},
           'owner': {'type': 'integer'}, # user_id this post/patch
           'when': {'type': 'datetime'},
           'involved': {'type': 'list'},
           'organisation': {'type': 'dict'},
           'rating': {'type': 'dict',
                      'schema': {'actual': {'type': 'integer'},
                                 'potential': {'type': 'integer'}
                                 }
                      },
           'weather': {'type': 'dict',
                       'schema': {'auto': {'type': 'dict'},
                                  'manual': {'type': 'dict'},
                                  }
                       },
           
           'events': {'type': 'list',
                      'schema': observation_components._schema
                      #'schema': {''} # Possibly the same as components
                      },
           
           'files': {'type': 'list', 
                     'schema': {'type': 'media'}
                     },
           'freetext': {'type': 'dict',
                        'schema': {'jumper': {'type': 'string'},
                                   'hl': {'type': 'string'},
                                   'hi': {'type': 'string'},
                                   'fs': {'type': 'string'},
                                   'su': {'type': 'string'},
                                   }
                        },
           
           'related': {'type': 'list'},
           'labels': {'type': 'list'},
           'comments': {'type': 'list',
                        'schema': {'date': 'datetime',
                                   'user': 'integer',
                                   'comment': 'string'
                                   }
                        },
           'workflow': {'type': 'dict', 'readonly': True},
           'watchers': {'type': 'list', 'readonly': True},
           'actions': {'type': 'dict'},
           'audit': {'type': 'list'},
           'acl': {'type': 'dict'},
           
           
           }

definition = {
        'item_title': 'observations',
        'datasource': {'source': 'observations',
                       'projection': {'files': 0, 'acl': 0} },
        
        # Make a counter so we can have a lookup for #455
        'additional_lookup': {
            'url': 'regex("[\d{1,9}]+")',
            'field': 'id',
        },
        
        'versioning': True,
        
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT'],
        
        'schema': _schema
        
       }