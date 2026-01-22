import { render, screen } from '@testing-library/react';
import Home from '@/app/page';

describe('Home Page', () => {
  it('renders welcome message', () => {
    render(<Home />);
    
    const heading = screen.getByRole('heading', { name: /welcome to meghan/i });
    expect(heading).toBeInTheDocument();
  });

  it('displays all chat modes', () => {
    render(<Home />);
    
    expect(screen.getByText('Talk Mode')).toBeInTheDocument();
    expect(screen.getByText('Plan Mode')).toBeInTheDocument();
    expect(screen.getByText('Calm Mode')).toBeInTheDocument();
    expect(screen.getByText('Reflect Mode')).toBeInTheDocument();
  });

  it('shows mode descriptions', () => {
    render(<Home />);
    
    expect(screen.getByText('Empathetic listening and emotional validation')).toBeInTheDocument();
    expect(screen.getByText('Micro-planning and manageable next steps')).toBeInTheDocument();
    expect(screen.getByText('Grounding techniques and breathing exercises')).toBeInTheDocument();
    expect(screen.getByText('Structured journaling and self-reflection')).toBeInTheDocument();
  });
});