## `main`
  - `schema`
      - `primaryKey` ['id']
  | name           | description                 | type    | constraints                   |
|:---------------|:----------------------------|:--------|:------------------------------|
| id             | Any positive integer        | integer | {'minimum': 1}                |
| integer_minmax | An integer between 1 and 10 | integer | {'minimum': 1, 'maximum': 10} |