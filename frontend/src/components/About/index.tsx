import React from 'react';
import DOMPurify from 'dompurify';
import viewStyles from '../../pages/StartupView.module.css';

export interface AboutProps {
  aboutHtml: string;
}

export const About: React.FC<AboutProps> = ({ aboutHtml }) => {
  if (!aboutHtml) return null;

  const sanitizedHtml = DOMPurify.sanitize(aboutHtml);

  return (
    <section id="about" style={{ marginTop: '40px' }}>
      <h2 className={viewStyles.title}>Про Компанію</h2>
      <div
        className={viewStyles.lead}
        dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
      />
    </section>
  );
};
