import type { AboutProps } from './types';

export const aboutMock: AboutProps = {
  aboutHtml: '<p data-testid="test-p">Інноваційні технології для бізнесу</p>'
};

export const aboutMaliciousMock: AboutProps = {
  aboutHtml: '<p>Безпечний текст</p><script data-testid="xss">alert("xss")</script>'
};
