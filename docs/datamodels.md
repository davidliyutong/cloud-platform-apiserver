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
- **template_ref**: unique id of template, uuid, mutable when pod is `stopped` (must reference a `committed` template)
- **template_str**: string copy of template, string, immutable
- **cpu_lim_m_cpu**: limit of cpu (mCPU), integer, mutable when pod is `stopped`
- **mem_lim_mb**: limit of memory (MB), integer, mutable when pod is `stopped`
- **storage_lim_mb**: limit of storage (MB), integer, mutable when pod is `stopped`
- **gpu**: limit of gpu, integer, mutable when pod is `stopped`
- **username**: username of owner, string, immutable
- **user_uuid**: unique id of owner, uuid, immutable
- **created_at**: timestamp, date, immutable, autogen
- **started_at**: timestamp, date, mutable, autogen
- **timeout_s**: timeout in terms of second, integer, mutable
- **current_status**: 'pending'|'creating'|'running'|'stopped'|'deleting'|'failed'|'unknown', string, mutable, autogen
- **target_status**: target status ('running' or 'stopped'), string, mutable
- **current_status_reason**: short human-readable reason populated when a pod fails to reach `target_status` (e.g. `Unschedulable: 0/3 nodes available: 3 Insufficient memory`, `ImagePullBackOff: ...`). Cleared on any subsequent non-failed status transition (a successful start *or* a successful stop). string|null, autogen

## Template

- **name**: name, str, immutable(user)
- **description**: description, str, immutable(user)
- **template_id**: unique id, uuid, immutable, autogen
- **image_ref**: reference to which image, string, mutable
- **template_str**: string of template, string, immutable(user)
- **fields**: other fields, dict, immutable(user)
- **defaults**: default value of fields, dict, immutable(user)

## Quota

- **cpu_m**: total cpu allowance in mCPU. Charged only for pods whose `current_status == running`. int, mutable
- **memory_mb**: total memory allowance in MB. Charged only for running pods. int, mutable
- **storage_mb**: total storage allowance in MB. Charged for **all** pods regardless of running state. int, mutable
- **gpu**: total gpu allowance. Charged only for running pods. int, mutable
- **network_mb**: TBD
- **pod_n**: maximum number of pods (any state), int, mutable
