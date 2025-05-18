# Oracle NetSuite SQL Query (SuiteQL) REST API (SuiteTalk) notes #

## General ##

SuiteTalk docs: [https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_158394344595.html](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_158394344595.html)

SuiteQL docs: [https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257770590.html](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257770590.html)

## URL ##

https://REALM.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql

Where:

- **REALM** - company/customer ID in the NetSuite API ecosystem, e.g., `1234567`.

## Request Body ##

```json
{
    "q": "SELECT top 2 id, col1, col2 FROM table1"
}
```

## Sample response payload ##

```json
{
  "links": [
    {
      "rel": "self",
      "href": "https://1234567.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    }
  ],
  "count": 2,
  "hasMore": false,
  "items": [
    {
      "links": [],
      "col1": "value_11",
      "col2": "value_12",
      "id": "id_01"
    },
    {
      "links": [],
      "col1": "value_21",
      "col2": "value_222",
      "id": "id_02"
    }
  ],
  "offset": 0,
  "totalResults": 2
}
```

## Output pagination ##

If `hasMore` is `true`, you can request the next page.

## API errors ##

The response payload may contain an error code. Although the error codes look like HTTP status codes, they are API errors.

|Error code|Description|
|---|---|
|402, 403, 404|No search name found|
|405|Field name(s) error|
|406|Unknown/undefined (that’s unclear to me)|
|301|No data found|
