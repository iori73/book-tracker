import React from 'react'
import { render, screen } from '@testing-library/react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

describe('UI Components', () => {
  it('Badge renders correctly', () => {
    render(<Badge>Test Badge</Badge>)
    const badge = screen.getByText('Test Badge')
    expect(badge).toBeInTheDocument()
  })

  it('Button renders correctly', () => {
    render(<Button>Test Button</Button>)
    const button = screen.getByRole('button', { name: 'Test Button' })
    expect(button).toBeInTheDocument()
  })
})

