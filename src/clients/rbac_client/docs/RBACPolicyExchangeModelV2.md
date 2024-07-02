# RBACPolicyExchangeModelV2

RBAC policy model v2, used to define RBAC

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**policies** | [**List[PoliciesInner]**](PoliciesInner.md) |  | [optional] 

## Example

```python
from clpl_apiserver_client.models.rbac_policy_exchange_model_v2 import RBACPolicyExchangeModelV2

# TODO update the JSON string below
json = "{}"
# create an instance of RBACPolicyExchangeModelV2 from a JSON string
rbac_policy_exchange_model_v2_instance = RBACPolicyExchangeModelV2.from_json(json)
# print the JSON string representation of the object
print(RBACPolicyExchangeModelV2.to_json())

# convert the object into a dict
rbac_policy_exchange_model_v2_dict = rbac_policy_exchange_model_v2_instance.to_dict()
# create an instance of RBACPolicyExchangeModelV2 from a dict
rbac_policy_exchange_model_v2_from_dict = RBACPolicyExchangeModelV2.from_dict(rbac_policy_exchange_model_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


