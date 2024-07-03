system_config_text = """
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, obj, act

# Role definition
[role_definition]
g = _, _
g2 = _, _

# Policy effect
[policy_effect]
e = some(where (p.eft == allow))

# Matchers
[matchers]
m = g(r.sub, p.sub) && keyMatch(r.obj, p.obj) && r.act == p.act || r.sub == "root"

"""

system_policy_text = """
p, role::resources_owner, resources::/*, create
p, role::resources_owner, resources::/*, read
p, role::resources_owner, resources::/*, update
p, role::resources_owner, resources::/*, delete
p, role::resources_owner, resources::/*, list
p, role::resources_reader, resources::/*, read
p, role::resources_reader, resources::/*, list

p, role::groups_owner, resources::/groups/*, create
p, role::groups_owner, resources::/groups/*, read
p, role::groups_owner, resources::/groups/*, update
p, role::groups_owner, resources::/groups/*, delete
p, role::groups_owner, resources::/groups/*, list
p, role::groups_creator, resources::/groups/*, create
p, role::groups_reader, resources::/groups/*, read
p, role::groups_reader, resources::/groups/*, list

p, role::pods_owner, resources::/pods/*, create
p, role::pods_owner, resources::/pods/*, read
p, role::pods_owner, resources::/pods/*, update
p, role::pods_owner, resources::/pods/*, delete
p, role::pods_owner, resources::/pods/*, list
p, role::pods_creator, resources::/pods/*, create

p, role::projects_owner, resources::/projects/*, create
p, role::projects_owner, resources::/projects/*, read
p, role::projects_owner, resources::/projects/*, update
p, role::projects_owner, resources::/projects/*, delete
p, role::projects_owner, resources::/projects/*, list
p, role::projects_creator, resources::/projects/*, create
p, role::projects_reader, resources::/projects/*, read
p, role::projects_reader, resources::/projects/*, list
p, role::projects_public_reader, resources::/projects/.public/*, read
p, role::projects_public_reader, resources::/projects/.public/*, list

p, role::system_owner, resources::/system/*, create
p, role::system_owner, resources::/system/*, read
p, role::system_owner, resources::/system/*, update
p, role::system_owner, resources::/system/*, delete
p, role::system_owner, resources::/system/*, list
p, role::system_reader, resources::/system/*, read

p, role::policies_owner, resources::/policies/*, create
p, role::policies_owner, resources::/policies/*, read
p, role::policies_owner, resources::/policies/*, update
p, role::policies_owner, resources::/policies/*, delete
p, role::policies_owner, resources::/policies/*, list

p, role::templates_owner, resources::/templates/*, create
p, role::templates_owner, resources::/templates/*, read
p, role::templates_owner, resources::/templates/*, update
p, role::templates_owner, resources::/templates/*, delete
p, role::templates_owner, resources::/templates/*, list
p, role::templates_reader, resources::/templates/*, read
p, role::templates_reader, resources::/templates/*, list

p, role::users_owner, resources::/users/*, create
p, role::users_owner, resources::/users/*, read
p, role::users_owner, resources::/users/*, update
p, role::users_owner, resources::/users/*, delete
p, role::users_owner, resources::/users/*, list
p, role::users_creator, resources::/users/*, create
p, role::users_reader, resources::/users/*, read
p, role::users_reader, resources::/users/*, list

p, role::volumes_owner, resources::/volumes/*, create
p, role::volumes_owner, resources::/volumes/*, read
p, role::volumes_owner, resources::/volumes/*, update
p, role::volumes_owner, resources::/volumes/*, delete
p, role::volumes_owner, resources::/volumes/*, list
p, role::volumes_creator, resources::/volumes/*, create
p, role::volumes_reader, resources::/volumes/*, read
p, role::volumes_reader, resources::/volumes/*, list
p, role::volumes_public_reader, resources::/volumes/.public/*, read
p, role::volumes_public_reader, resources::/volumes/.public/*, list

g, role::super_admin, role::resources_owner

g, role::admin, role::resources_reader
g, role::admin, role::groups_owner
g, role::admin, role::pods_owner
g, role::admin, role::projects_owner
g, role::admin, role::policies_owner
g, role::admin, role::templates_owner
g, role::admin, role::users_owner
g, role::admin, role::volumes_owner

g, role::user, role::groups_reader
g, role::user, role::pods_creator
g, role::user, role::pod_owner
g, role::user, role::projects_public_reader
g, role::user, role::templates_reader
g, role::user, role::volumes_creator
g, role::user, role::volumes_public_reader

g, role::power_user, role::user
g, role::power_user, role::groups_creator
g, role::power_user, role::groups_reader
g, role::power_user, role::projects_creator
g, role::power_user, role::projects_reader
g, role::power_user, role::template_reader
g, role::power_user, role::volumes_reader
g, role::power_user, role::users_creator
g, role::power_user, role::users_reader

g, group::admin, role::admin
g, group::student, role::user
g, group::professor, role::power_user
g, group::default, role::user

g, user::admin, role::super_admin
"""

system_test_policy_text = """
g, user::alice, role::super_admin
g, user::bob, role::admin
g, user::charlie, role::power_user
g, user::david, role::user
g, user::eve, role::user
g, user::eve, role::groups_creator
"""