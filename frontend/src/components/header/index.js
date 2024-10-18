import styles from './style.module.css'
import { Nav, AccountMenu, LinkComponent } from '../index.js'
import Container from '../container'
import LogoHeader from '../../images/logo-header.png'
import { NavLink } from 'react-router-dom'

const Header = ({ loggedIn, onSignOut, orders }) => {
  return <header className={styles.header}>
    <Container>
      <div className={styles.headerContent}>
        <LinkComponent
          className={styles.headerLink}
          title={<img className={styles.headerLogo} src={LogoHeader} alt='Foodgram' />}
          href='/'
        />
        <Nav
          loggedIn={loggedIn}
          onSignOut={onSignOut}
          orders={orders}
        />
        <NavLink
          exact
          to="/about"
          className={styles.navLink}
          activeClassName={styles.navLinkActive}
        >
          About
        </NavLink>
        <NavLink
          exact
          to="/technologies"
          className={styles.navLink}
          activeClassName={styles.navLinkActive}
        >
          Technologies
        </NavLink>
      </div>
    </Container>
  </header>
}

export default Header
