import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { Story } from './index';
import { storyMock } from './mocks';

interface StorySection {
  id: string;
  title: string;
  text: string;
}

interface StoryProps {
  sections: StorySection[];
}

function renderStory(props: StoryProps) {
  return render(
    <MemoryRouter>
      <Story {...props} />
    </MemoryRouter>
  );
}

describe('Story Component', () => {
  it('should render all story blocks with anchors successfully', () => {
    renderStory(storyMock);

    const heading = screen.getByRole('heading', { name: /стартап/i });
    expect(heading).toBeInTheDocument();

    const blocks = screen.getAllByTestId('story-block');
    expect(blocks).toHaveLength(storyMock.sections.length);

    const firstSection = storyMock.sections[0];
    const firstBlock = screen.getByText(firstSection.title).closest('div');
    expect(firstBlock).toHaveAttribute('id', firstSection.id);

    expect(screen.getByText(new RegExp(firstSection.text, 'i'))).toBeInTheDocument();
  });

  it('should return null and render nothing if sections list is empty', () => {
    const { container } = renderStory({ sections: [] });

    expect(container.firstChild).toBeNull();

    const heading = screen.queryByRole('heading', { name: /стартап/i });
    expect(heading).not.toBeInTheDocument();
  });
});
