"""

Init for the seperated applications and including those into a Domain

@author: Einar Huseby <einar.huseby@gmail.com>

"""

# Import settings files

# Melwin data
import melwin_clubs
import melwin_licenses
# Melwin merged data
import melwin_person

# User data (password, avatar, settings, acls etc)
# import users

# Authentication
# import authentication

# Incident Reporting
import incident_reports

# Files - just a test collection
import files

# A custom endpoint for developement flexibility!
import dev

# Build the Domain to be presented
DOMAIN = {
    'clubs': melwin_clubs.definition,
    'melwin': melwin_person.definition,
    'licenses': melwin_licenses.definition,
    'avvik' : incident_reports.definition,
    'dev' : dev.definition,
    'files' : files.definition,
    
}

