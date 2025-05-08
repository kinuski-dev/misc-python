# Oracle NetSuite Saved Search REST (restnl) API notes #

## General ##

There seems to be too little information about the Saved Search API on NetSuite web pages. There are many other API that are described well, though.

## URI & parameters ##

https://REALM.restlets.api.netsuite.com/app/site/hosting/restlet.nl?deploy=1&script=1341&searchname=3751&start=0&page=5000

Where:

- **REALM** - company/customer ID in the NetSuite API ecosystem
- **deploy** - unknown to me ATM
- **script** - likely a script that implements queries (*searchnames*)
- **searchname** - data entity - a table or a query result
- **start** - pagination parameter; defines the starting object in the output (in other words, how many objects to skip)
- **page** - pagination parameter; defines the number of objects in the output (default and max values are 10000, it seems)

## Entities vs. Search names ##

|Entity|*searchname*|
|---|---:|
|Account Master|3751|
|Cost Center Master|3752|
|Currency Master|3766|
|Payment Terms Master|3757|
|Transactions Vendor Bill & Credit|3750|
|Vendor Master|3753|

## Output pagination ##

The sample response payload is below. As long as *more* equals *true*, you can request the next page.

```json
{
  "more": true,
  "lines": [
    {
      "Bill ID": "12345678",
      "Bill Number": "BILL0510022",
      ...
    }
  ]
}
```

## API errors ##

The response payload may contain an error code. Although the error codes look like HTTP status codes, they are API errors.

|Error code|Description|
|---|---|
|402, 403, 404|No search name found|
|405|Field name(s) error|
|406|Unknown/undefined (that’s unclear to me)|
|301|No data found|

## Sample output ##

```json
{
  "more": false,
  "lines": [
    {
      "Term ID": "30",
      "Term Name": "30 Days netto",
      "Days Till Net Due": "30",
      "Discount Percentage": "",
      "Days Till Discount Expires": ""
    },
    {
      "Term ID": "31",
      "Term Name": "20 Days netto",
      "Days Till Net Due": "20",
      "Discount Percentage": "10",
      "Days Till Discount Expires": ""
    },
    {
      "Term ID": "32",
      "Term Name": "10 Days netto",
      "Days Till Net Due": "10",
      "Discount Percentage": "20",
      "Days Till Discount Expires": "5"
    }
  ]
}
```
