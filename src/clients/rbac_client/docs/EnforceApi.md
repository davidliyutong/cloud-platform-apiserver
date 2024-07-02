# clpl_apiserver_client.EnforceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**postenforce_enforce_post**](EnforceApi.md#postenforce_enforce_post) | **POST** /v1/enforce | Enforce the request against the policy and model, return the result.


# **postenforce_enforce_post**
> EnforceResponse postenforce_enforce_post(enforce_request=enforce_request)

Enforce the request against the policy and model, return the result.

### Example


```python
import clpl_apiserver_client
from clpl_apiserver_client.models.enforce_request import EnforceRequest
from clpl_apiserver_client.models.enforce_response import EnforceResponse
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
    api_instance = clpl_apiserver_client.EnforceApi(api_client)
    enforce_request = clpl_apiserver_client.EnforceRequest() # EnforceRequest |  (optional)

    try:
        # Enforce the request against the policy and model, return the result.
        api_response = await api_instance.postenforce_enforce_post(enforce_request=enforce_request)
        print("The response of EnforceApi->postenforce_enforce_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnforceApi->postenforce_enforce_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **enforce_request** | [**EnforceRequest**](EnforceRequest.md)|  | [optional] 

### Return type

[**EnforceResponse**](EnforceResponse.md)

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

