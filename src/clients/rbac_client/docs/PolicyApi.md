# clpl_apiserver_client.PolicyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**postpolicy_policy_add**](PolicyApi.md#postpolicy_policy_add) | **POST** /v1/policy/add | Add a raw policy to enforcer cache
[**postpolicy_policy_reload**](PolicyApi.md#postpolicy_policy_reload) | **POST** /v1/policy/reload | Reload the policy from the database.


# **postpolicy_policy_add**
> ResponseBaseModel postpolicy_policy_add(rbac_policy_exchange_model_v2=rbac_policy_exchange_model_v2)

Add a raw policy to enforcer cache

Add new policies, sync them across workers, will not modify the database.

### Example


```python
import clpl_apiserver_client
from clpl_apiserver_client.models.rbac_policy_exchange_model_v2 import RBACPolicyExchangeModelV2
from clpl_apiserver_client.models.response_base_model import ResponseBaseModel
from clpl_apiserver_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = clpl_apiserver_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with clpl_apiserver_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = clpl_apiserver_client.PolicyApi(api_client)
    rbac_policy_exchange_model_v2 = clpl_apiserver_client.RBACPolicyExchangeModelV2() # RBACPolicyExchangeModelV2 |  (optional)

    try:
        # Add a raw policy to enforcer cache
        api_response = await api_instance.postpolicy_policy_add(rbac_policy_exchange_model_v2=rbac_policy_exchange_model_v2)
        print("The response of PolicyApi->postpolicy_policy_add:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyApi->postpolicy_policy_add: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rbac_policy_exchange_model_v2** | [**RBACPolicyExchangeModelV2**](RBACPolicyExchangeModelV2.md)|  | [optional] 

### Return type

[**ResponseBaseModel**](ResponseBaseModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Default Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **postpolicy_policy_reload**
> ResponseBaseModel postpolicy_policy_reload()

Reload the policy from the database.

Reload the policy from the database.

### Example


```python
import clpl_apiserver_client
from clpl_apiserver_client.models.response_base_model import ResponseBaseModel
from clpl_apiserver_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = clpl_apiserver_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with clpl_apiserver_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = clpl_apiserver_client.PolicyApi(api_client)

    try:
        # Reload the policy from the database.
        api_response = await api_instance.postpolicy_policy_reload()
        print("The response of PolicyApi->postpolicy_policy_reload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyApi->postpolicy_policy_reload: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ResponseBaseModel**](ResponseBaseModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Default Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

