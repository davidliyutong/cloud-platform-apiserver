# TemplateModel

Template model, used to define template

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 
**resource_status** | [**ResourceStatusEnum**](ResourceStatusEnum.md) |  | [optional] 
**template_id** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**image_ref** | **str** |  | 
**template_str** | **str** |  | 
**fields** | [**Dict[str, FieldTypeEnum]**](FieldTypeEnum.md) |  | 
**defaults** | **object** |  | 

## Example

```python
from clpl_rbacserver_client.models.template_model import TemplateModel

# TODO update the JSON string below
json = "{}"
# create an instance of TemplateModel from a JSON string
template_model_instance = TemplateModel.from_json(json)
# print the JSON string representation of the object
print(TemplateModel.to_json())

# convert the object into a dict
template_model_dict = template_model_instance.to_dict()
# create an instance of TemplateModel from a dict
template_model_from_dict = TemplateModel.from_dict(template_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


