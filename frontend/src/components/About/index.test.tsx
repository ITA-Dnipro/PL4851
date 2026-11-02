import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { About } from './index';
import { aboutMock, aboutMaliciousMock } from './mocks';

function renderAbout(props: { aboutHtml: string }) {
  return render(
    <MemoryRouter>
      <About {...props} />
    </MemoryRouter>
  );
}

describe('About Component', () => {
  it('should render HTML content successfully', () => {
    renderAbout(aboutMock);

    const heading = screen.getByRole('heading', { name: /про компанію/i });
    expect(heading).toBeInTheDocument();

    const contentText = screen.getByText(/інноваційні технології для бізнесу/i);
    expect(contentText).toBeInTheDocument();
  });

  it('should sanitize and strip malicious script tags', () => {
    renderAbout(aboutMaliciousMock);

    expect(screen.getByText('Безпечний текст')).toBeInTheDocument();

    const scriptTag = screen.queryByText(/alert/i) || screen.queryByTestId('xss');
    expect(scriptTag).not.toBeInTheDocument();
  });

  it('should return null and render nothing if aboutHtml is empty', () => {
    const { container } = renderAbout({ aboutHtml: '' });

    expect(container.firstChild).toBeNull();

    const heading = screen.queryByRole('heading', { name: /про компанію/i });
    expect(heading).not.toBeInTheDocument();
  });
});
