import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Header from './Header';
import { useAuth } from '../hooks/useAuth';

const navigate = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useNavigate: () => navigate };
});

vi.mock('../hooks/useAuth');

function renderHeader() {
  return render(
    <MemoryRouter>
      <Header />
    </MemoryRouter>,
  );
}

describe('Header', () => {
  beforeEach(() => {
    navigate.mockClear();
    useAuth.mockReturnValue({ user: null, isAuthenticated: false });
  });

  it('веде логотип на головну сторінку', () => {
    renderHeader();
    expect(screen.getByRole('link', { name: /forum/i })).toHaveAttribute('href', '/');
  });

  it('показує поле пошуку', () => {
    renderHeader();
    expect(screen.getByRole('searchbox', { name: 'Пошук' })).toBeInTheDocument();
  });

  it('показує Увійти та Зареєструватися для гостя', () => {
    renderHeader();
    expect(screen.getByRole('link', { name: 'Увійти' })).toHaveAttribute('href', '/login');
    expect(screen.getByRole('link', { name: 'Зареєструватися' })).toHaveAttribute('href', '/register');
  });

  it('перекидає на /search?q=... при відправці пошуку', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.type(screen.getByRole('searchbox', { name: 'Пошук' }), 'сир{enter}');

    expect(navigate).toHaveBeenCalledWith('/search?q=%D1%81%D0%B8%D1%80');
  });

  it('не навігує, якщо запит порожній', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.type(screen.getByRole('searchbox', { name: 'Пошук' }), '{enter}');

    expect(navigate).not.toHaveBeenCalled();
  });

  it('ховає кнопки входу, коли користувач авторизований', () => {
    useAuth.mockReturnValue({ user: { id: 1 }, isAuthenticated: true });
    renderHeader();

    expect(screen.queryByRole('link', { name: 'Увійти' })).not.toBeInTheDocument();
  });
});