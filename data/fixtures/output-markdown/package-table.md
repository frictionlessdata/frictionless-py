# `package`
## `main`
  - `schema`
      - `primaryKey` ['id']
  | name           | type    | description                 | constraints                   |
|:---------------|:--------|:----------------------------|:------------------------------|
| id             | integer | Any positive integer        | {'minimum': 1}                |
| integer_minmax | integer | An integer between 1 and 10 | {'minimum': 1, 'maximum': 10} |
| boolean        | boolean | Any boolean                 |                               |
## `secondary`
  - `schema`
      - `foreignKeys`
      - [1]
        - `fields` ['main_id']
        - `reference`
          - `resource` main
          - `fields` ['id']
  | name    | type    | description                      | constraints      |
|:--------|:--------|:---------------------------------|:-----------------|
| main_id | integer | Any value in main.id             |                  |
| string  | string  | Any string of up to 3 characters | {'maxLength': 3} |