/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
  title: "Frictionless Data",
  tagline: "The future of data is frictionless",
  organizationName: "facebook",
  projectName: "docusaurus",
  baseUrl: "/",
  url: "https://v2.frictionlessdata.io",
  favicon: "img/fd-blue.png",
  customFields: {
    description:
      "An optimized site generator in React. Docusaurus helps you to move fast and write content. Build documentation websites, blogs, marketing pages, and more.",
  },
  themes: ["@docusaurus/theme-live-codeblock"],
  stylesheets: ["https://fonts.googleapis.com/css?family=Roboto&display=swap"],
  plugins: [
    [
      "@docusaurus/plugin-ideal-image",
      {
        quality: 70,
        max: 1030, // max resized image's size.
        min: 640, // min resized image's size. if original is lower, use that size.
        steps: 2, // the max number of images generated between min and max (inclusive)
      },
    ],
  ],
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          path: "../docs",
          sidebarPath: require.resolve("./sidebars.js"),
          // editUrl: 'https://github.com/frictionlessdata/frictionlessdata.io/edit/master/',
          // showLastUpdateAuthor: true,
          // showLastUpdateTime: true,
          remarkPlugins: [require("./src/plugins/remark-npm2yarn")],
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
  themeConfig: {
    sidebarCollapsible: false,
    image: "img/docusaurus.png",
    gtag: {
      trackingID: "UA-141789564-1",
    },
    // googleAnalytics: {
    //   trackingID: 'UA-141789564-1',
    // },
    algolia: {
      apiKey: "47ecd3b21be71c5822571b9f59e52544",
      indexName: "docusaurus-2",
      algoliaOptions: {
        // facetFilters: [`version:${versions[0]}`],
      },
    },
    navbar: {
      hideOnScroll: true,
      title: "Frictionless Data",
      logo: {
        alt: "Frictionless Data Logo",
        src: "img/fd-blue.png",
      },
      items: [
        {
          to: "docs/guides/introduction-guide",
          label: "Guides",
          position: "left",
        },
        {
          to: "docs/tutorials/filelike-tutorial",
          label: "Tutorials",
          position: "left",
        },
        {
          to: "docs/references/schemes-reference",
          label: "References",
          position: "left",
        },
        {
          to: "docs/development/contributing",
          label: "Development",
          position: "left",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            {
              label: "Intro",
              to: "docs/intro/home",
            },
            {
              label: "Specs",
              to: "docs/specs/home",
            },
            {
              label: "Software",
              to: "docs/software/home",
            },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "Blog",
              href: "https://stackoverflow.com/questions/tagged/docusaurus",
            },
            {
              label: "Forum",
              to: "feedback",
            },
            {
              label: "Chat",
              href: "https://gitter.im/frictionlessdata/chat",
            },
          ],
        },
        {
          title: "Social",
          items: [
            {
              label: "GitHub",
              to: "https://github.com/frictionlessdata/frictionlessdata.io",
            },
            {
              label: "Facebook",
              href: "https://github.com/facebook/docusaurus",
            },
            {
              label: "Twitter",
              href: "https://twitter.com/docusaurus",
            },
          ],
        },
      ],
      logo: {
        alt: "Open Knowledge Foundation",
        src: "https://a.okfn.org/img/oki/landscape-white-468x122.png",
        href: "https://okfn.org",
      },
      copyright: `Copyright © ${new Date().getFullYear()} Frictionless Data`,
    },
  },
};
