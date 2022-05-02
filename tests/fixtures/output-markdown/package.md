# `package`
## `main`
  - `schema`
      - `primaryKey` ['id']
### `id`
  - `description` Any positive integer
  - `type` integer
  - `constraints`:
    - `minimum` 1
### `integer_minmax`
  - `description` An integer between 1 and 10
  - `type` integer
  - `constraints`:
    - `minimum` 1
    - `maximum` 10
### `boolean`
  - `description` Any boolean
  - `type` boolean
## `secondary`
  - `schema`
      - `foreignKeys`
      - [1]
        - `fields` ['main_id']
        - `reference`
          - `resource` main
          - `fields` ['id']
### `main_id`
  - `description` Any value in main.id
  - `type` integer
### `string`
  - `description` Any string of up to 3 characters
  - `type` string
  - `constraints`:
    - `maxLength` 3