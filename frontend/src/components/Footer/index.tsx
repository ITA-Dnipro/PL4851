import { faEnvelope, faPhone } from '@fortawesome/free-solid-svg-icons'
import { Link } from 'react-router-dom'

import logo from '../../assets/logo.svg'
import Icon from '../Icon'
import type { FooterContactsData, FooterData, FooterLinkData, FooterLinkGroupData } from './types'
import styles from './styles.module.css'

interface FooterProps {
  data: FooterData | null
}

export default function Footer({ data }: FooterProps) {
  // Without data the footer still closes the page with the copyright
  if (!data) {
    return (
      <footer className={styles.footer}>
        <div className="container">
          <p className={`${styles.copyright} ${styles.centered}`}>
            Copyright {new Date().getFullYear()} Forum. All rights reserved.
          </p>
        </div>
      </footer>
    )
  }

  const { contacts, link_groups, legal_links, copyright } = data

  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.about}>
          <Link to="/" className={styles.logo}>
            <img src={logo} alt="" />
            <span>Forum</span>
          </Link>
          <Contacts contacts={contacts} />
        </div>

        <div className={styles.groups}>
          {link_groups.map((group) => (
            <LinkGroup key={group.title} group={group} />
          ))}
        </div>

        <div className={styles.legal}>
          <LegalLinks links={legal_links} />
          <p className={styles.copyright}>{copyright}</p>
        </div>
      </div>
    </footer>
  )
}

function Contacts({ contacts }: { contacts: FooterContactsData }) {
  const { address, email, phone } = contacts

  return (
    <address className={styles.contacts}>
      <p className={styles.address}>
        {address.map((line) => (
          <span key={line}>{line}</span>
        ))}
      </p>
      <a href={`mailto:${email}`} className={styles.contact}>
        <Icon icon={faEnvelope} className={styles.contactIcon} />
        {email}
      </a>
      <a href={`tel:${phone.replace(/\s/g, '')}`} className={styles.contact}>
        <Icon icon={faPhone} className={styles.contactIcon} />
        {phone}
      </a>
    </address>
  )
}

function LinkGroup({ group }: { group: FooterLinkGroupData }) {
  return (
    <nav aria-label={group.title} className={styles.group}>
      <h3 className={styles.groupTitle}>{group.title}</h3>
      <ul className={styles.groupLinks}>
        {group.links.map((link) => (
          <li key={link.label}>
            <Link to={link.url} className={styles.link}>
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}

function LegalLinks({ links }: { links: FooterLinkData[] }) {
  return (
    <ul className={styles.legalLinks}>
      {links.map((link) => (
        <li key={link.label}>
          <Link to={link.url} className={styles.secondaryLink}>
            {link.label}
          </Link>
        </li>
      ))}
    </ul>
  )
}
