/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';

import Image from '@theme/IdealImage';
import Layout from '@theme/Layout';

import classnames from 'classnames';

import styles from './styles.module.css';

const QUOTES = [
  {
    thumbnail: require('../data/quotes/christopher-chedeau.jpg'),
    name: 'Christopher "vjeux" Chedeau',
    title: 'Lead Prettier Developer',
    text: (
      <>
        I&apos;ve helped open source many projects at Facebook and every one
        needed a website. They all had very similar constraints: the
        documentation should be written in markdown and be deployed via GitHub
        pages. I’m so glad that Docusaurus now exists so that I don’t have to
        spend a week each time spinning up a new one.
      </>
    ),
  },
  {
    thumbnail: require('../data/quotes/hector-ramos.jpg'),
    name: 'Hector Ramos',
    title: 'Lead React Native Advocate',
    text: (
      <>
        Open source contributions to the React Native docs have skyrocketed
        after our move to Docusaurus. The docs are now hosted on a small repo in
        plain markdown, with none of the clutter that a typical static site
        generator would require. Thanks Slash!
      </>
    ),
  },
  {
    thumbnail: require('../data/quotes/ricky-vetter.jpg'),
    name: 'Ricky Vetter',
    title: 'ReasonReact Developer',
    text: (
      <>
        Docusaurus has been a great choice for the ReasonML family of projects.
        It makes our documentation consistent, i18n-friendly, easy to maintain,
        and friendly for new contributors.
      </>
    ),
  },
];

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig: {customFields = {}} = {}} = context;

  return (
    <Layout permalink="/" description={customFields.description}>
      <div className={styles.hero}>
        <div className={styles.heroInner}>
          <h1 className={styles.heroProjectTagline}>
            <img
              alt="Docusaurus with Keytar"
              className={styles.heroLogo}
              src={useBaseUrl('img/rufus.png')}
            />
            The <span className={styles.heroProjectKeywords}>future</span> of <span className={styles.heroProjectKeywords}>data</span>{' '}
            <div>is <span className={styles.heroProjectKeywords}>frictionless</span></div>
          </h1>
          <div className={styles.indexCtas}>
            <Link
              className={styles.indexCtasGetStartedButton}
              to={useBaseUrl('docs/intro/home')}>
              Get Started
            </Link>
            <span className={styles.indexCtasGitHubButtonWrapper}>
              <iframe
                className={styles.indexCtasGitHubButton}
                src="https://ghbtns.com/github-btn.html?user=frictionlessdata&amp;repo=specs&amp;type=star&amp;count=true&amp;size=large"
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
          Specifications and software for the publication, transport, and consumption of data.
        </div>
      </div>
      <div className={styles.section}>
        <div className="container text--center">
          <div className="row">
            <div className="col">
              <img
                className={styles.featureImage}
                alt="Specifications"
                src={useBaseUrl('img/standard.png')}
              />
              <h3 className="padding-top--md">Specifications</h3>
              <p className="padding-horiz--md">
                Lightweight containerisation formats for data that provide a
                minimal yet powerful foundation for data publication, transport,
                and consumption.
              </p>
            </div>
            <div className="col">
              <img
                alt="Software"
                className={styles.featureImage}
                src={useBaseUrl('img/software.png')}
              />
              <h3 className="padding-top--md">Software</h3>
              <p className="padding-horiz--md">
                Apps and integrations that make it easy to integrate Frictionless Data
                specifications into your data publication, access, and analysis workflows.
              </p>
            </div>
            <div className="col">
              <img
                alt="Community"
                className={styles.featureImage}
                src={useBaseUrl('img/community3.png')}
              />
              <h3 className="padding-top--md">Community</h3>
              <p className="padding-horiz--md">
                Labs, libraries, governments, and companies are using Frictionless Data
                in their data workflows to reduce grunt work and move faster to insight.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className={classnames(styles.section, 'section-users')}>
        <div className="container text--center">
          <h2>Who is using Frictionless Data</h2>
          <img src="/img/users2.png" alt="" />
        </div>
      </div>

      <div
        className={classnames(
          styles.section,
          styles.sectionAlt,
          styles.quotes,
        )}>
        <div className="container">
          <div className="row">
            {QUOTES.map(quote => (
              <div className="col" key={quote.name}>
                <div className="avatar avatar--vertical margin-bottom--sm">
                  <Image
                    alt={quote.name}
                    className="avatar__photo avatar__photo--xl"
                    img={quote.thumbnail}
                    style={{overflow: 'hidden'}}
                  />
                  <div className="avatar__intro padding-top--sm">
                    <h4 className="avatar__name">{quote.name}</h4>
                    <small className="avatar__subtitle">{quote.title}</small>
                  </div>
                </div>
                <p className="text--center text--italic padding-horiz--md">
                  {quote.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Home;
