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
p, role::group_owner, resources::/groups/.private/*, read
p, role::group_owner, resources::/groups/.private/*, update
p, role::group_owner, resources::/groups/.private/*, delete

p, role::pods_owner, resources::/pods/*, create
p, role::pods_owner, resources::/pods/*, read
p, role::pods_owner, resources::/pods/*, update
p, role::pods_owner, resources::/pods/*, delete
p, role::pods_owner, resources::/pods/*, list
p, role::pods_creator, resources::/pods/*, create
p, role::pod_owner, resources::/pods/.private/*, read
p, role::pod_owner, resources::/pods/.private/*, update
p, role::pod_owner, resources::/pods/.private/*, delete

p, role::projects_owner, resources::/projects/*, create
p, role::projects_owner, resources::/projects/*, read
p, role::projects_owner, resources::/projects/*, update
p, role::projects_owner, resources::/projects/*, delete
p, role::projects_owner, resources::/projects/*, list
p, role::projects_creator, resources::/projects/*, create
p, role::projects_reader, resources::/projects/.public/*, read
p, role::projects_reader, resources::/projects/.public/*, list
p, role::project_owner, resources::/projects/.private/*, read
p, role::project_owner, resources::/projects/.private/*, update
p, role::project_owner, resources::/projects/.private/*, delete
p, role::project_reader, resources::/projects/:pod_id, read

p, role::system_owner, resources::/system/*, create
p, role::system_owner, resources::/system/*, read
p, role::system_owner, resources::/system/*, update
p, role::system_owner, resources::/system/*, delete
p, role::system_owner, resources::/system/*, list
p, role::system_reader, resources::/system/*, read

p, role::rbac_owner, resources::/rbacserver/*, create
p, role::rbac_owner, resources::/rbacserver/*, read
p, role::rbac_owner, resources::/rbacserver/*, update
p, role::rbac_owner, resources::/rbacserver/*, delete
p, role::rbac_owner, resources::/rbacserver/*, list

p, role::templates_owner, resources::/templates/*, create
p, role::templates_owner, resources::/templates/*, read
p, role::templates_owner, resources::/templates/*, update
p, role::templates_owner, resources::/templates/*, delete
p, role::templates_owner, resources::/templates/*, list
p, role::templates_creator, resources::/templates/*, create
p, role::templates_reader, resources::/templates/.public/*, read
p, role::templates_reader, resources::/templates/.public/*, list
p, role::template_owner, resources::/templates/.private/*, read
p, role::template_owner, resources::/templates/.private/*, update
p, role::template_owner, resources::/templates/.private/*, delete
p, role::template_reader, resources::/templates/.private/*, read

p, role::users_owner, resources::/users/*, create
p, role::users_owner, resources::/users/*, read
p, role::users_owner, resources::/users/*, update
p, role::users_owner, resources::/users/*, delete
p, role::users_owner, resources::/users/*, list
p, role::users_creator, resources::/users/*, create
p, role::user_owner, resources::/users/.private/*, read
p, role::user_owner, resources::/users/.private/*, update
p, role::user_owner, resources::/users/.private/*, delete

p, role::volumes_owner, resources::/volumes/*, create
p, role::volumes_owner, resources::/volumes/*, read
p, role::volumes_owner, resources::/volumes/*, update
p, role::volumes_owner, resources::/volumes/*, delete
p, role::volumes_owner, resources::/volumes/*, list
p, role::volumes_creator, resources::/volumes/*, create
p, role::volumes_reader, resources::/volumes/.public/*, read
p, role::volumes_reader, resources::/volumes/.public/*, list
p, role::volume_owner, resources::/volumes/.private/*, read
p, role::volume_owner, resources::/volumes/.private/*, update
p, role::volume_owner, resources::/volumes/.private/*, delete
p, role::volume_reader, resources::/volumes/.private/*, read

g, role::super_admin, role::resources_owner

g, role::admin, role::resources_reader
g, role::admin, role::groups_owner
g, role::admin, role::pods_owner
g, role::admin, role::projects_owner
g, role::admin, role::rbac_owner
g, role::admin, role::templates_owner
g, role::admin, role::users_owner
g, role::admin, role::volumes_owner

g, role::user, role::groups_reader
g, role::user, role::pods_creator
g, role::user, role::pod_owner
g, role::user, role::projects_reader
g, role::user, role::project_reader
g, role::user, role::templates_reader
g, role::user, role::user_owner
g, role::user, role::volumes_creator
g, role::user, role::volumes_reader
g, role::user, role::volume_owner
g, role::user, role::volume_reader

g, role::power_user, role::user
g, role::power_user, role::groups_creator
g, role::power_user, role::group_owner
g, role::power_user, role::projects_creator
g, role::power_user, role::project_owner
g, role::power_user, role::templates_creator
g, role::power_user, role::template_owner
g, role::power_user, role::template_reader
g, role::power_user, role::users_creator

g, admin, role::super_admin
"""

system_test_policy_text = """
g, alice, role::super_admin
g, bob, role::admin
g, charlie, role::power_user
g, david, role::user
g, eve, role::user
g, eve, role::groups_creator
"""
