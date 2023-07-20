# DataModels

## User

- **uid**: unique id, integer, immutable, autogen
- **uuid**: unique id, integer, immutable, autogen
- **username**: unique usernmae, string, immutable
- **status**: 'active'|'inactive', string, immutable(user)
- **email**: email, string(email), mutable
- **password**: password, hash, mutable
- **role**: 'user'|'admin'|'super_admin', string, immutable(user)
- **owned_pod_ids**: unique pod ids owned by this user, list(uuid), mutable, autogen
- **quota**: quota of this user, Quato struct, immutable(usdr)

## Pod

- **pod_id**: unique id, uuid, immutable, autogen
- **name**: name, string, mutable
- **description**: name, string, mutable
- **template_ref**: unique id of template, uuid, immutable
- **auth**: internal auth string, string, mutable, insecure
- **uid**: unique id of ownner, integer, immutable
- **created_at**: timestamp, date, immutable, autogen
- **started_at**: timestamp, date, mutable, autogen
- **timeout_s**: timeout in terms of second, integer, mutable
- **current_status**: 'creating'|'running'|'stopped'|'deleting', string, mutable, autogen
- **target_status**: target status, string, mutable

## Template (TBD)

- **template_id**: unique id, uuid, immutable, autogen
- **image_ref**: reference to which image, string, mutable

## Quota

- **cpu**: micro cpus, int, mutable
- **memory**: number of MBs, int, mutable
- **storage**: number of MBs, int, mutable
- **gpu**: TBD
- **network**: TBD
- **pod**: number of pods, int, mutable
