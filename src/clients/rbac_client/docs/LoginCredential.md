# LoginCredential


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** |  | 
**password** | **str** |  | 

## Example

```python
from clpl_apiserver_client.models.login_credential import LoginCredential

# TODO update the JSON string below
json = "{}"
# create an instance of LoginCredential from a JSON string
login_credential_instance = LoginCredential.from_json(json)
# print the JSON string representation of the object
print(LoginCredential.to_json())

# convert the object into a dict
login_credential_dict = login_credential_instance.to_dict()
# create an instance of LoginCredential from a dict
login_credential_from_dict = LoginCredential.from_dict(login_credential_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


