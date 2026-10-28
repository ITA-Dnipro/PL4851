import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ProductsList } from './index';
import { productsMock } from './mocks';

interface Product {
  id: number;
  label: string;
  description: string;
}

interface ProductsListProps {
  products: Product[];
}

function renderProductsList(props: ProductsListProps) {
  return render(
    <MemoryRouter>
      <ProductsList {...props} />
    </MemoryRouter>
  );
}

describe('ProductsList Component', () => {
  it('should render the list of products with correct titles and text', () => {
    renderProductsList(productsMock);

    const heading = screen.getByRole('heading', { name: /інформація про проекти/i });
    expect(heading).toBeInTheDocument();

    const items = screen.getAllByTestId('product-item');
    expect(items).toHaveLength(productsMock.products.length);

    expect(screen.getByText(new RegExp(productsMock.products[0].description, 'i'))).toBeInTheDocument();
  });

  it('should return null and render nothing if products list is empty', () => {
    const { container } = renderProductsList({ products: [] });

    expect(container.firstChild).toBeNull();

    const heading = screen.queryByRole('heading', { name: /інформація про проекти/i });
    expect(heading).not.toBeInTheDocument();
  });
});
