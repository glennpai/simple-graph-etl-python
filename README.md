# simple-graph-etl

Minimal wrapper lib for Python ETLs using Microsoft's Graph API

Designed with intent for use in Ohio University Python scripts interacting with the Graph API

## Example
Example document library structure: 
```
remote
└──dir
   └──path
      └──ExampleFile.txt
```

Example ETL:
```Python
import simple_graph_etl as sge

documentLibrary = sge.documentlibrary(
  client_id = 'some client ID',
  site_id = 'some site ID',
  res_id = 'some res ID',
  authority = 'some authority',
  scope = 'some scope'
 )
 
connection = sge.simpleetl(
  library = documentLibrary,
  thumbprint = 'some thumbprint',
  private_key = 'some private key'
)

connection.fetch('/remote/dir/path') # Create local copies of child files at specified remote path

transform_file('ExampleFile.txt') # Transform local file 

connection.delete('/remote/dir/path', 'ExampleFile.txt') # Delete remote copy of file as it will be replaced

connection.upload('/remote/dir/path', 'ExampleFile.txt') # Upload local copy of file to same location as original

```

## TODO

Add tests
Peer review
Publish
