# clpl_rbacserver_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**gethealth**](DefaultApi.md#gethealth) | **GET** /health | Health check. Return a 200 OK response.


# **gethealth**
> gethealth()

Health check. Return a 200 OK response.

### Example


```python
import clpl_rbacserver_client
from clpl_rbacserver_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = clpl_rbacserver_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with clpl_rbacserver_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = clpl_rbacserver_client.DefaultApi(api_client)

    try:
        # Health check. Return a 200 OK response.
        await api_instance.gethealth()
    except Exception as e:
        print("Exception when calling DefaultApi->gethealth: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**0** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

