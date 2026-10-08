import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Header from './Header';
import { useAuth } from '../hooks/useAuth';
import type { AuthUser } from '../hooks/useAuth'

const navigate = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return { ...actual, useNavigate: () => navigate };
});

vi.mock('../hooks/useAuth');

const mockUser: AuthUser = {
  id: 1,
  email: 'test@example.com',
}

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
    vi.mocked(useAuth).mockReturnValue({ user: null, isAuthenticated: false })
  });

  it('The logo links to the homepage', () => {
    renderHeader();
    expect(screen.getByRole('link', { name: /forum/i })).toHaveAttribute('href', '/');
  });

  it('shows the search field', () => {
    renderHeader();
    expect(screen.getByRole('searchbox', { name: 'Пошук' })).toBeInTheDocument();
  });

  it('displays "Log In" and "Sign Up" for guests', () => {
    renderHeader();
    expect(screen.getByRole('link', { name: 'Увійти' })).toHaveAttribute('href', '/login');
    expect(screen.getByRole('link', { name: 'Зареєструватися' })).toHaveAttribute('href', '/register');
  });

  it('redirects to /search?q=... when submitting a search', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.type(screen.getByRole('searchbox', { name: 'Пошук' }), 'сир{enter}');

    expect(navigate).toHaveBeenCalledWith('/search?q=%D1%81%D0%B8%D1%80');
  });

  it('does not navigate if the query is empty', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.type(screen.getByRole('searchbox', { name: 'Пошук' }), '{enter}');

    expect(navigate).not.toHaveBeenCalled();
  });

  it('hides the login buttons when the user is logged in', () => {
    vi.mocked(useAuth).mockReturnValue({ user: mockUser, isAuthenticated: true })
    renderHeader();

    expect(screen.queryByRole('link', { name: 'Увійти' })).not.toBeInTheDocument();
  });
});
