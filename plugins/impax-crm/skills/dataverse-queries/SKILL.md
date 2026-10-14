---
name: dataverse-queries
description: "Writes and debugs queries against Dataverse / Dynamics 365: FetchXML (joins, aggregates, paging), Web API OData URLs, Power Automate Filter rows expressions, and read-only SQL over the TDS endpoint. Use when the user needs a query, report data, record counts, a view filter, a blast-radius count, or a broken FetchXML or OData expression fixed."
---

# Dataverse Queries

**Ground first.** Use real logical names: check the table/column definitions (maker portal → Tables → Columns, the unpacked solution in the repo, or `GET /api/data/v9.2/EntityDefinitions(LogicalName='account')/Attributes?$select=LogicalName,AttributeType`). Never guess a schema name — custom columns carry the publisher prefix (`<prefix>_...`).

## FetchXML

```xml
<fetch top="50">
  <entity name="opportunity">
    <attribute name="name" />
    <attribute name="estimatedvalue" />
    <attribute name="estimatedclosedate" />
    <filter>
      <condition attribute="statecode" operator="eq" value="0" />
      <condition attribute="estimatedclosedate" operator="this-quarter" />
    </filter>
    <link-entity name="account" from="accountid" to="parentaccountid" alias="acc" link-type="inner">
      <attribute name="name" />
      <filter><condition attribute="address1_country" operator="eq" value="Kenya" /></filter>
    </link-entity>
    <order attribute="estimatedvalue" descending="true" />
  </entity>
</fetch>
```

Aggregate (counts / sums):

```xml
<fetch aggregate="true">
  <entity name="incident">
    <attribute name="incidentid" alias="cases" aggregate="count" />
    <attribute name="ownerid" alias="owner" groupby="true" />
    <filter><condition attribute="statecode" operator="eq" value="0" /></filter>
  </entity>
</fetch>
```

- Aggregates are capped (default 50,000 records); for bigger counts split the filter (e.g. by month) or use the TDS endpoint.
- Paging: 5,000 records per page; use the paging cookie (`page`, `count`, `paging-cookie`) or `@odata.nextLink` in Web API.
- Useful operators: `eq-userid`, `eq-businessid`, `last-x-days`, `this-month`, `under` (hierarchy), `not-null`, `in`.
- Build/test in **XrmToolBox → FetchXML Builder**, or the view designer then *Download FetchXML*.

## Web API (OData)

```
GET [org]/api/data/v9.2/contacts?$select=fullname,mobilephone,_parentcustomerid_value
    &$filter=statecode eq 0 and contains(emailaddress1,'@example.com')
    &$orderby=createdon desc&$top=50
Prefer: odata.include-annotations="OData.Community.Display.V1.FormattedValue"
```

- Lookups read as `_<lookup>_value`; write as `"<navproperty>@odata.bind": "/accounts(<guid>)"` (navigation property name is case-sensitive, often the schema name).
- Entity **set** names are plural (`accounts`, `contacts`, `<prefix>_loanapplications`).
- FetchXML via Web API: `GET [org]/api/data/v9.2/accounts?fetchXml=<url-encoded fetch>`.

## Power Automate "Filter rows"

Same OData `$filter` syntax: `statecode eq 0 and _ownerid_value eq '<guid>'`. Choice columns compare to the integer value.

## TDS (SQL) endpoint

Read-only T-SQL for analysis (must be enabled in the environment): connect with SSMS / Azure Data Studio to `<org>.crm4.dynamics.com,5558` with Entra ID auth. Respects the user's security. Good for ad-hoc counts and reconciliations; not for production integrations.

## Output

Return the query, what it returns in plain words, and any assumptions about schema names (flagged for verification).
