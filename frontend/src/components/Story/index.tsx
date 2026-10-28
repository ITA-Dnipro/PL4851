import React from 'react';
import viewStyles from '../../pages/StartupView.module.css';

interface StorySection {
  id: string;
  title: string;
  text: string;
}

interface StoryProps {
  sections: StorySection[];
}

export const Story: React.FC<StoryProps> = ({ sections }) => {
  if (!sections || sections.length === 0) return null;

  return (
    <section id="story" style={{ marginTop: '40px' }}>
      <h2 className={viewStyles.title}>Стартап</h2>
      <div className={viewStyles.group}>
        {sections.map((item) => (
          <div key={item.id} id={item.id} data-testid="story-block" style={{ marginBottom: '12px' }}>
            <h3 className={viewStyles.value} style={{ fontSize: '18px', marginBottom: '8px' }}>
              {item.title}
            </h3>
            <p style={{ fontSize: '16px', color: 'var(--color-black-90)', lineHeight: '1.5' }}>
              {item.text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};
