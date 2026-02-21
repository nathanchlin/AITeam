import { render, screen } from '@testing-library/react';
import Game from '../components/Game';

test('renders game title', () => {
  render(<Game />);
  const titleElement = screen.getByText(/2046 Game/i);
  expect(titleElement).toBeInTheDocument();
});