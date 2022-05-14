# `package`
## `main`
  - `schema`
      - `primaryKey` ['id']
  | name           | description                 | type    | constraints                   |
|:---------------|:----------------------------|:--------|:------------------------------|
| id             | Any positive integer        | integer | {'minimum': 1}                |
| integer_minmax | An integer between 1 and 10 | integer | {'minimum': 1, 'maximum': 10} |
| boolean        | Any boolean                 | boolean |                               |
## `secondary`
  - `schema`
      - `foreignKeys`
      - [1]
        - `fields` ['main_id']
        - `reference`
          - `resource` main
          - `fields` ['id']
  | name    | description                      | type    | constraints      |
|:--------|:---------------------------------|:--------|:-----------------|
| main_id | Any value in main.id             | integer |                  |
| string  | Any string of up to 3 characters | string  | {'maxLength': 3} |