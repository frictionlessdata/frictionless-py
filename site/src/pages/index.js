/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import useBaseUrl from "@docusaurus/useBaseUrl";
import Image from "@theme/IdealImage";
import Layout from "@theme/Layout";
import classnames from "classnames";
import styles from "./styles.module.css";

function Home() {
  const context = useDocusaurusContext();
  const { siteConfig: { customFields = {}, tagline } = {} } = context;

  return (
    <Layout
      title={tagline}
      permalink="/"
      description={customFields.description}
    >
      <div className={styles.hero}>
        <div className={styles.heroInner}>
          <h1 className={styles.heroProjectTagline}>
            <img
              alt="Docusaurus with Keytar"
              className={styles.heroLogo}
              src={useBaseUrl("img/example.png")}
            />
            Data <span className={styles.heroProjectKeywords}>framework</span>{" "}
            for Python
          </h1>
          <div className={styles.indexCtas}>
            <Link
              className={styles.indexCtasGetStartedButton}
              to={useBaseUrl("docs/guides/introduction")}
            >
              Get Started
            </Link>
            <span className={styles.indexCtasGitHubButtonWrapper}>
              <iframe
                className={styles.indexCtasGitHubButton}
                src="https://ghbtns.com/github-btn.html?user=frictionlessdata&amp;repo=frictionless-py&amp;type=star&amp;count=true&amp;size=large"
                width={160}
                height={30}
                title="GitHub Stars"
              />
            </span>
          </div>
        </div>
      </div>
      <div className={classnames(styles.announcement, styles.announcementDark)}>
        <div className={styles.announcementInner}>
          Data management framework for Python to describe, extract, validate,
          and transform tabular data.
        </div>
      </div>
      <div className={styles.section}>
        <div className="container text--center">
          <div className="row">
            <div className="col">
              <a href="docs/guides/describing-data">
                <img
                  className={styles.featureImage}
                  alt="Specifications"
                  src={useBaseUrl("img/describe.png")}
                />
                <h3 className="padding-top--md">Describe Data</h3>
              </a>
              <p className="padding-horiz--md">
                You can infer, edit and save metadata of your data tables. It's
                a first step for ensuring data quality and usability.
              </p>
            </div>
            <div className="col">
              <a href="docs/guides/extracting-data">
                <img
                  className={styles.featureImage}
                  alt="Specifications"
                  src={useBaseUrl("img/extract.png")}
                />
                <h3 className="padding-top--md">Extract Data</h3>
              </a>
              <p className="padding-horiz--md">
                You can read your data using a unified tabular interface. Data
                quality and consistency are guaranteed by a schema.
              </p>
            </div>
            <div className="col">
              <a href="docs/guides/validation-guide">
                <img
                  alt="Software"
                  className={styles.featureImage}
                  src={useBaseUrl("img/validate.png")}
                />
                <h3 className="padding-top--md">Validate Data</h3>
              </a>
              <p className="padding-horiz--md">
                You can validate data tables, resources, and datasets.
                Frictionless generates a unified validation report.
              </p>
            </div>
            <div className="col">
              <a href="docs/guides/transform-guide">
                <img
                  alt="Community"
                  className={styles.featureImage}
                  src={useBaseUrl("img/transform.png")}
                />
                <h3 className="padding-top--md">Transform Data</h3>
              </a>
              <p className="padding-horiz--md">
                You can clean, reshape, and transfer your data tables and
                datasets. Frictionless provides a pipeline capability.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Home;
