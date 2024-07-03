# EnforceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] [default to '']
**status** | **int** |  | 
**message** | **str** |  | 
**result** | **bool** |  | [optional] [default to False]

## Example

```python
from clpl_rbacserver_client.models.enforce_response import EnforceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EnforceResponse from a JSON string
enforce_response_instance = EnforceResponse.from_json(json)
# print the JSON string representation of the object
print(EnforceResponse.to_json())

# convert the object into a dict
enforce_response_dict = enforce_response_instance.to_dict()
# create an instance of EnforceResponse from a dict
enforce_response_from_dict = EnforceResponse.from_dict(enforce_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


