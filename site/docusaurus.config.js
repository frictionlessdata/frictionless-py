module.exports = {
  title: "Frictionless Framework",
  tagline: "Describe, extract, validate, and fransform data in Python",
  organizationName: "Frictionless Data",
  projectName: "frictionless",
  baseUrl: "/",
  url: "https://framework.frictionlessdata.io",
  favicon: "img/logo.png",
  customFields: {
    description:
      "Data management framework for Python that provides functionality to describe, extract, validate, and transform tabular data",
  },
  themes: ["@docusaurus/theme-live-codeblock"],
  // stylesheets: ["https://fonts.googleapis.com/css?family=Roboto&display=swap"],
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
    [
      "docusaurus-plugin-plausible",
      {
        domain: "framework.frictionlessdata.io",
      },
    ],
  ],
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          path: "docs",
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl:
            "https://github.com/frictionlessdata/frictionless-py/edit/main/docs/",
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          remarkPlugins: [require("./src/plugins/remark-npm2yarn")],
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
  themeConfig: {
    announcementBar: {
      id: "support_us",
      content:
        'The latest version is <a href="https://framework.frictionlessdata.io/">Frictionless Framework (v5)</a>',
      backgroundColor: "#fafbfc",
      textColor: "#091E42",
      isCloseable: false,
    },
    sidebarCollapsible: true,
    image: "img/logo-bright2.png",
    prism: {
      theme: require("prism-react-renderer/themes/github"),
      darkTheme: require("prism-react-renderer/themes/dracula"),
    },
    algolia: {
      apiKey: "0632881f114cfc50b94e4bc7b970cbce",
      indexName: "frictionless-py",
      algoliaOptions: {
        // facetFilters: [`version:${versions[0]}`],
      },
    },
    navbar: {
      hideOnScroll: true,
      logo: {
        alt: "Frictionless Framework",
        src: "img/logo-bright.png",
        srcDark: "img/logo-dark.png",
      },
      items: [
        {
          to: "docs/guides/guides-overview",
          label: "Guides",
          position: "left",
        },
        {
          to: "docs/tutorials/tutorials-overview",
          label: "Tutorials",
          position: "left",
        },
        {
          label: "Notebooks",
          position: "left",
          items: [
            {
              label: "Frictionless Cars",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/frictionless-cars.ipynb",
            },
            {
              label: "Frictionless Biology",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/reshaping-data-frictionless.ipynb",
            },
            {
              label: "Frictionless Describe and Extract",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/frictionless-tutorial-describe-extract.ipynb",
            },
            {
              label: "Frictionless Excel",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/frictionless-excel.ipynb",
            },
            {
              label: "Frictionless Research Data Management Workflows",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/frictionless-RDM-workflows.ipynb",
            },
            {
              label: "Frictionless Export, Markdown and Other",
              href: "https://colab.research.google.com/github/frictionlessdata/frictionless-py/blob/main/docs/tutorials/notebooks/tutorial-markdown-export-feature.ipynb",
            },
          ],
        },
        {
          to: "docs/references/references-overview",
          label: "References",
          position: "left",
        },
        {
          to: "docs/development/development",
          label: "Development",
          position: "left",
        },
        {
          to: "docs/faq",
          label: "FAQ",
          position: "left",
        },
        {
          href: "https://frictionlessdata.io/",
          label: "Back to the main site",
          position: "right",
          className: "header-mainsite-link",
        },
        {
          to: "docs/development/changelog",
          label: "v4",
          position: "right",
          className: "header-version-link",
        },
        {
          href: "https://github.com/frictionlessdata/frictionless-py",
          position: "right",
          className: "header-github-link",
          "aria-label": "GitHub repository",
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
              label: "Guides",
              to: "docs/guides/guides-overview",
            },
            {
              label: "Tutorials",
              to: "docs/tutorials/tutorials-overview",
            },
            {
              label: "References",
              to: "docs/references/references-overview",
            },
            {
              label: "Development",
              to: "docs/development/development",
            },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "Blog",
              href: "https://frictionlessdata.io/blog/",
            },
            {
              label: "Forum",
              to: "https://github.com/frictionlessdata/project/discussions",
            },
            {
              label: "Chat",
              href: "https://discordapp.com/invite/Sewv6av",
            },
          ],
        },
        {
          title: "Social",
          items: [
            {
              label: "GitHub",
              to: "https://github.com/frictionlessdata/frictionless-py",
            },
            {
              label: "Twitter",
              href: "https://twitter.com/frictionlessd8a",
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
