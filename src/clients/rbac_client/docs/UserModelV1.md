# UserModelV1

User model, used to define user

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 
**resource_status** | [**ResourceStatusEnum**](ResourceStatusEnum.md) |  | [optional] 
**uid** | **int** |  | 
**uuid** | **str** |  | 
**username** | **str** |  | 
**status** | [**UserStatusEnum**](UserStatusEnum.md) |  | [optional] 
**email** | **str** |  | 
**password** | **str** |  | 
**htpasswd** | **str** |  | [optional] 
**role** | [**UserRoleEnum**](UserRoleEnum.md) |  | 
**owned_pod_ids** | **List[str]** |  | 
**quota** | [**QuotaModel**](QuotaModel.md) |  | 
**extra_info** | **object** |  | [optional] 

## Example

```python
from clpl_apiserver_client.models.user_model_v1 import UserModelV1

# TODO update the JSON string below
json = "{}"
# create an instance of UserModelV1 from a JSON string
user_model_v1_instance = UserModelV1.from_json(json)
# print the JSON string representation of the object
print(UserModelV1.to_json())

# convert the object into a dict
user_model_v1_dict = user_model_v1_instance.to_dict()
# create an instance of UserModelV1 from a dict
user_model_v1_from_dict = UserModelV1.from_dict(user_model_v1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


