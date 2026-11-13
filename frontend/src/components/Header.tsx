import Link from 'next/link'
import styles from '@/styles/Header.module.css'

export default function Header() {
  return (
    <header className={styles.header}>
      <Link href="/" className={styles.logo}>
        SubTrack
      </Link>
      <nav className={styles.nav}>
        <a href="/#dashboard">Dashboard</a>
        <a href="https://app.swaggerhub.com" target="_blank" rel="noopener noreferrer">API Docs</a>
      </nav>
    </header>
  )
}
