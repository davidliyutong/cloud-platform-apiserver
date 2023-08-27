# DataModels

## User

- **uid**: unique id, integer, immutable, autogen
- **uuid**: unique id, integer, immutable, autogen
- **username**: unique usernmae, string, immutable
- **status**: 'active'|'inactive', string, immutable(user)
- **email**: email, string(email), mutable
- **password**: password, hash, mutable
- **htpasswd**: httpasswd, hash, mutable, autogen
- **role**: 'user'|'admin'|'super_admin', string, immutable(user)
- **owned_pod_ids**: unique pod ids owned by this user, list(uuid), mutable, autogen
- **quota**: quota of this user, Quato struct, immutable(user)

## Pod

- **pod_id**: unique id, uuid, immutable, autogen
- **name**: name, string, mutable
- **description**: name, string, mutable
- **image_ref**: reference of image, string, mutable
- **template_ref**: unique id of template, uuid, immutable 
- **template_str**: string copy of template, string, immutable
- **cpu_lim_m_cpu**: limit of cpu, integer, immutable
- **mem_lim_mb**: limit of memory, integer, immutable
- **storage_lim_mb**: limit of storage, integer, immutable
- **username**: username of owner, string, immutable
- **user_uuid**: unique id of owner, uuid, immutable
- **created_at**: timestamp, date, immutable, autogen
- **started_at**: timestamp, date, mutable, autogen
- **timeout_s**: timeout in terms of second, integer, mutable
- **current_status**: 'creating'|'running'|'stopped'|'deleting', string, mutable, autogen
- **target_status**: target status, string, mutable

## Template

- **name**: name, str, immutable(user)
- **description**: description, str, immutable(user)
- **template_id**: unique id, uuid, immutable, autogen
- **image_ref**: reference to which image, string, mutable
- **template_str**: string of template, string, immutable(user)
- **fields**: other fields, dict, immutable(user)
- **defaults**: default value of fields, dict, immutable(user)

## Quota

- **cpu**: micro cpus, int, mutable
- **memory**: number of MBs, int, mutable
- **storage**: number of MBs, int, mutable
- **gpu**: TBD
- **network**: TBD
- **pod**: number of pods, int, mutable
