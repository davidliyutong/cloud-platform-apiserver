# ResponseBaseModel

Base model for response

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] [default to '']
**status** | **int** |  | 
**message** | **str** |  | 

## Example

```python
from clpl_rbacserver_client.models.response_base_model import ResponseBaseModel

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseBaseModel from a JSON string
response_base_model_instance = ResponseBaseModel.from_json(json)
# print the JSON string representation of the object
print(ResponseBaseModel.to_json())

# convert the object into a dict
response_base_model_dict = response_base_model_instance.to_dict()
# create an instance of ResponseBaseModel from a dict
response_base_model_from_dict = ResponseBaseModel.from_dict(response_base_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


