## `main`
  - `path` data/primary-file-types.csv
  - `schema`
      - `primaryKey` ['id']
  | name           | type    | description                 | constraints                   |
|:---------------|:--------|:----------------------------|:------------------------------|
| id             | integer | Any positive integer        | {'minimum': 1}                |
| integer_minmax | integer | An integer between 1 and 10 | {'minimum': 1, 'maximum': 10} |
| boolean        | boolean | Any boolean                 |                               |