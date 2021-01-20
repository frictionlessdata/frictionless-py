/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const users = [
  // Please add in alphabetical order of title.
  {
    title: 'Datahub.io',
    description: 'A platform for finding, sharing and publishing high quality data online.',
    preview: require('./showcase/datahub.png'),
    website: 'https://datahub.io',
    source: 'https://github.com/datopian',
    fbOpenSource: false,
    pinned: false,
  },
  {
    title: 'goodtables.io',
    description: 'Continuous data validation, as a service.',
    preview: require('./showcase/goodtables2.png'),
    website: 'https://goodtables.io',
    source: 'https://github.com/frictionlessdata/goodtables.io',
    fbOpenSource: true,
    pinned: true,
  },
  {
    title: 'OpenSpending',
    description: 'The Fiscal Data Package is the native format for datasets published on OpenSpending.',
    preview: require('./showcase/openspending.png'),
    website: 'https://openspending.io',
    source: 'https://github.com/openspending',
    fbOpenSource: true,
    pinned: true,
  },
];

export default users;
