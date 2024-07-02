# QuotaModel

Quota model, used to define user quota

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 
**committed** | **bool** |  | [optional] [default to False]
**cpu_m** | **int** |  | 
**memory_mb** | **int** |  | 
**storage_mb** | **int** |  | 
**gpu** | **int** |  | 
**network_mb** | **int** |  | 
**pod_n** | **int** |  | 

## Example

```python
from clpl_apiserver_client.models.quota_model import QuotaModel

# TODO update the JSON string below
json = "{}"
# create an instance of QuotaModel from a JSON string
quota_model_instance = QuotaModel.from_json(json)
# print the JSON string representation of the object
print(QuotaModel.to_json())

# convert the object into a dict
quota_model_dict = quota_model_instance.to_dict()
# create an instance of QuotaModel from a dict
quota_model_from_dict = QuotaModel.from_dict(quota_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


