import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Header.module.css';
import logo from '../assets/logo.svg';
import searchIcon from '../assets/search.svg';
import { useAuth } from '../hooks/useAuth';

export default function Header() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const onSearch = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

    return (
        <header className={styles.header}>
          <div className={`container ${styles.inner}`}>
            <Link to="/" className={styles.logo}>
              <img src={logo} alt="Forum" />
              <p>Forum</p>
            </Link>

           <div className={styles.menu}>
              <nav className={styles.nav} aria-label="Головне меню">
                <Link to="#">Про нас</Link>
                <Link to="#">Підприємства та сектори</Link>
              </nav>

              <form className={styles.search} role="search" onSubmit={onSearch}>
                <input
                  type="search"
                  placeholder="Пошук"
                  className={styles.searchInput}
                  aria-label="Пошук"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                <button type="submit" className={styles.searchButton} aria-label="Шукати">
                  <img src={searchIcon} alt="" />
                </button>
              </form>
            </div>

            <div className={styles.actions}>
              {isAuthenticated ? (
                <Link to="/dashboard" className="button">Кабінет</Link>
              ) : (
                <>
                  <Link to="/login" className={styles.login}>Увійти</Link>
                  <Link to="/register" className="button">Зареєструватися</Link>
                </>
              )}
            </div>
          </div>
        </header>
    );
}