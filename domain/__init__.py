"""

Init for the seperated applications and including those into a Domain

@author: Einar Huseby <einar.huseby@gmail.com>

"""

# Import settings files

# Melwin data (simulate the melwin service)
import melwin_clubs
import melwin_licenses
import melwin_users
import melwin_membership

# User data (avatar, settings, acls etc)
import users, users_auth
import licenses
import clubs

# Gear
import gear
import gear_manufacturers

# Definitions
import jump_categories
import jumps_quarterly_reports

# Incident Reporting
import observations
import observation_components
import observation_comments
# Files - just a test collection
import files

import tags

import acl_groups, acl_roles, users_acl

# A custom endpoint for developement flexibility!
import dev

import test

import help

import content, content_aggregations

# Build the Domain to be presented
DOMAIN = {

    # "users_auth": users_auth.definition, No, pure Flask
    "melwin/clubs": melwin_clubs.definition,
    "melwin/users": melwin_users.definition,
    "melwin/licenses": melwin_licenses.definition,
    "melwin/memberships": melwin_membership.definition,
    "licenses": licenses.definition,
    "clubs": clubs.definition,
    "gear": gear.definition,
    "gear/manufacturers": gear_manufacturers.definition,
    "observations": observations.definition,
    "observations/components": observation_components.definition,
    "jumps/categories": jump_categories.definition,
    "jumps/quarterly/reports": jumps_quarterly_reports.definition,
    "dev": dev.definition,
    "files": files.definition,
    "tags": tags.definition,
    "acl/groups": acl_groups.definition,
    "acl/roles": acl_roles.definition,
    "users": users.definition,
    "users/acl": users_acl.definition,
    "users/auth": users_auth.definition,
    "observation/comments": observation_comments.definition,
    "observation/agg": test.definition,
    "help": help.definition,
    "content": content.definition,
    "content/aggregate/parents": content_aggregations.parents,
    "content/aggregate/children": content_aggregations.children,
    "content/aggregate/siblings": content_aggregations.siblings,
}
