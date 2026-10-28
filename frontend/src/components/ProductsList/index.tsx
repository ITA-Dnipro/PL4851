import React from 'react';
import viewStyles from '../../pages/StartupView.module.css';

interface Product {
  id: number;
  label: string;
  description: string;
}

interface ProductsListProps {
  products: Product[];
}

export const ProductsList: React.FC<ProductsListProps> = ({ products }) => {
  if (!products || products.length === 0) return null;

  return (
    <section id="products" style={{ marginTop: '40px' }}>
      <h2 className={viewStyles.title}>Інформація про проекти</h2>
      <div className={viewStyles.group}>
        {products.map((item) => (
          <div key={item.id} className={viewStyles.row} data-testid="product-item">
            <strong className={viewStyles.value}>{item.label}:</strong>
            <span>{item.description}</span>
          </div>
        ))}
      </div>
    </section>
  );
};
