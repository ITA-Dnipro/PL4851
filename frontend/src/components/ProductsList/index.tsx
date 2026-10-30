import React from 'react';
import viewStyles from '../../pages/StartupView.module.css';

interface Product {
  id: number;
  label: string;
  description: string;
}

export interface ProductsListProps {
  products: Product[];
}

export const ProductsList: React.FC<ProductsListProps> = ({ products }) => {
  if (!products || products.length === 0) return null;

  return (
    <section id="products" className={viewStyles.productsSection}>
      <h2 className={viewStyles.title}>Інформація про проєкти</h2>
      <div className={viewStyles.productsList}>
        {products.map((item) => (
          <p key={item.id} className={viewStyles.productItem} data-testid="product-item">
            <strong>{item.label}:</strong>{' '}
            <span>{item.description}</span>
          </p>
        ))}
      </div>
    </section>
  );
};
