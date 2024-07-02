# PodModelV1

Pod model, used to define pod

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | 
**resource_status** | [**ResourceStatusEnum**](ResourceStatusEnum.md) |  | [optional] 
**pod_id** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**template_ref** | **str** |  | 
**template_str** | **str** |  | 
**cpu_lim_m_cpu** | **int** |  | 
**mem_lim_mb** | **int** |  | 
**storage_lim_mb** | **int** |  | 
**username** | **str** |  | 
**user_uuid** | **str** |  | 
**created_at** | **datetime** |  | 
**started_at** | **datetime** |  | 
**accessed_at** | **datetime** |  | 
**timeout_s** | **int** |  | 
**current_status** | [**PodStatusEnum**](PodStatusEnum.md) |  | 
**target_status** | [**PodStatusEnum**](PodStatusEnum.md) |  | 

## Example

```python
from clpl_apiserver_client.models.pod_model_v1 import PodModelV1

# TODO update the JSON string below
json = "{}"
# create an instance of PodModelV1 from a JSON string
pod_model_v1_instance = PodModelV1.from_json(json)
# print the JSON string representation of the object
print(PodModelV1.to_json())

# convert the object into a dict
pod_model_v1_dict = pod_model_v1_instance.to_dict()
# create an instance of PodModelV1 from a dict
pod_model_v1_from_dict = PodModelV1.from_dict(pod_model_v1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


