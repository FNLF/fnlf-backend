"""

Init for the seperated applications and including those into a Domain

@author: Einar Huseby <einar.huseby@gmail.com>

"""

# Import settings files

# Melwin data
import melwin_clubs
import melwin_licenses
# Melwin merged data
import melwin_users

# User data (avatar, settings, acls etc)
import users
import users_auth

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
    #'users' : users.definition,
    #'users_auth': users_auth.definition, No, pure Flask
    'melwin/clubs': melwin_clubs.definition,
    'melwin/users': melwin_users.definition,
    'melwin/licenses': melwin_licenses.definition,
    'observations' : incident_reports.definition,
    'dev' : dev.definition,
    'files' : files.definition,
   
}

