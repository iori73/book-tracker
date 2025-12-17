import { NextResponse } from 'next/server';
import { searchBooks } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  
  const params = {
    source: searchParams.get('source') || undefined,
    status: searchParams.get('status') || undefined,
    title: searchParams.get('title') || undefined,
    author: searchParams.get('author') || undefined,
    category: searchParams.get('category') || undefined,
  };
  
  try {
    const books = searchBooks(params);
    return NextResponse.json(books);
  } catch (error) {
    console.error('Error fetching books:', error);
    return NextResponse.json({ error: 'Failed to fetch books' }, { status: 500 });
  }
}

