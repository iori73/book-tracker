import { NextResponse } from 'next/server';
import { getStatistics, getCategorySummary } from '@/lib/db';

export async function GET() {
  try {
    const stats = getStatistics();
    const categories = getCategorySummary();
    
    return NextResponse.json({
      stats,
      categories
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    return NextResponse.json({ error: 'Failed to fetch statistics' }, { status: 500 });
  }
}

