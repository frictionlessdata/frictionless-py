/*
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
  introduction: ["introduction/introduction", "introduction/whats-next"],
  guides: [
    "guides/guides-overview",
    "guides/getting-started",
    "guides/introduction-guide",
    "guides/describing-data",
    "guides/extracting-data",
    "guides/validating-data",
    "guides/transforming-data",
    {
      "Mastring the Framework": [
        "guides/package-guide",
        "guides/resource-guide",
        "guides/schema-guide",
        "guides/field-guide",
        "guides/layout-guide",
        "guides/detector-guide",
        "guides/inquiry-guide",
        "guides/report-guide",
        "guides/pipeline-guide",
        "guides/status-guide",
      ],
      "Writing an Extension": [
        "guides/system-guide",
        "guides/plugin-guide",
        "guides/scheme-guide",
        "guides/format-guide",
        "guides/storage-guide",
        "guides/server-guide",
        "guides/error-guide",
        "guides/check-guide",
        "guides/step-guide",
        "guides/type-guide",
      ],
    },
  ],
  tutorials: [
    "tutorials/tutorials-overview",
    "tutorials/working-in-python",
    "tutorials/working-with-cli",
    "tutorials/working-with-api",
    {
      "Schemes Tutorials": [
        "tutorials/buffer-tutorial",
        "tutorials/local-tutorial",
        "tutorials/multipart-tutorial",
        "tutorials/remote-tutorial",
        "tutorials/s3-tutorial",
        "tutorials/stream-tutorial",
      ],
      "Formats Tutorials": [
        "tutorials/bigquery-tutorial",
        "tutorials/ckan-tutorial",
        "tutorials/csv-tutorial",
        "tutorials/excel-tutorial",
        "tutorials/gsheets-tutorial",
        "tutorials/html-tutorial",
        "tutorials/inline-tutorial",
        "tutorials/json-tutorial",
        "tutorials/ods-tutorial",
        "tutorials/pandas-tutorial",
        "tutorials/spss-tutorial",
        "tutorials/sql-tutorial",
      ],
    },
  ],
  references: [
    "references/references-overview",
    "references/plugins-reference",
    "references/schemes-reference",
    "references/formats-reference",
    "references/errors-reference",
    "references/checks-reference",
    "references/steps-reference",
    "references/types-reference",
    "references/api-reference",
  ],
  development: [
    "development/development",
    "development/contributing",
    "development/changelog",
    "development/migration",
    "development/authors",
  ],
};
