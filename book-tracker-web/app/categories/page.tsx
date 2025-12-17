'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Folder, CheckCircle2, BookOpen, Clock, ShoppingCart } from 'lucide-react';
import { Book } from '@/lib/db';

interface CategorySummary {
  category: string;
  total_books: number;
  completed: number;
  in_progress: number;
  not_started: number;
  purchased: number;
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<CategorySummary[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      fetchBooks(selectedCategory);
    }
  }, [selectedCategory]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setCategories(data.categories);
      if (data.categories.length > 0 && !selectedCategory) {
        setSelectedCategory(data.categories[0].category);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBooks = async (category: string) => {
    try {
      const response = await fetch(`/api/books?category=${encodeURIComponent(category)}`);
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error('Error fetching books:', error);
    }
  };

  const selectedCat = categories.find(c => c.category === selectedCategory);

  const completedBooks = books.filter(b => b.status === 'completed');
  const inProgressBooks = books.filter(b => b.status === 'in_progress');
  const notStartedBooks = books.filter(b => b.status === 'not_started');
  const purchasedBooks = books.filter(b => b.status === 'purchased');

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => window.location.href = '/'}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <div className="flex items-center gap-2">
            <Folder className="h-7 w-7" />
            <h1 className="text-3xl font-bold">カテゴリ</h1>
          </div>
          <p className="text-muted-foreground">カテゴリ別に本を閲覧</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-[300px_1fr] gap-6">
        {/* カテゴリリスト */}
        <Card>
          <CardHeader>
            <CardTitle>カテゴリ一覧</CardTitle>
            <CardDescription>{categories.length}カテゴリ</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {categories.map((category) => (
                <Button
                  key={category.category}
                  variant={selectedCategory === category.category ? "default" : "ghost"}
                  className="w-full justify-between"
                  onClick={() => setSelectedCategory(category.category)}
                >
                  <span className="truncate">{category.category}</span>
                  <Badge variant="secondary">{category.total_books}</Badge>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* カテゴリ詳細 */}
        {selectedCat && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>{selectedCat.category}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{selectedCat.total_books}</div>
                    <div className="text-sm text-muted-foreground">総数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{selectedCat.completed}</div>
                    <div className="text-sm text-muted-foreground">完了</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{selectedCat.in_progress}</div>
                    <div className="text-sm text-muted-foreground">進行中</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">{selectedCat.not_started}</div>
                    <div className="text-sm text-muted-foreground">未読</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-amber-600">{selectedCat.purchased}</div>
                    <div className="text-sm text-muted-foreground">購入済み</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="all" className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="all">すべて ({books.length})</TabsTrigger>
                <TabsTrigger value="completed" className="flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4" />
                  完了 ({completedBooks.length})
                </TabsTrigger>
                <TabsTrigger value="in_progress" className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  進行中 ({inProgressBooks.length})
                </TabsTrigger>
                <TabsTrigger value="not_started" className="flex items-center gap-1">
                  <BookOpen className="h-4 w-4" />
                  未読 ({notStartedBooks.length})
                </TabsTrigger>
                <TabsTrigger value="purchased" className="flex items-center gap-1">
                  <ShoppingCart className="h-4 w-4" />
                  購入 ({purchasedBooks.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4 mt-4">
                {books.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </TabsContent>

              <TabsContent value="completed" className="space-y-4 mt-4">
                {completedBooks.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </TabsContent>

              <TabsContent value="in_progress" className="space-y-4 mt-4">
                {inProgressBooks.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </TabsContent>

              <TabsContent value="not_started" className="space-y-4 mt-4">
                {notStartedBooks.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </TabsContent>

              <TabsContent value="purchased" className="space-y-4 mt-4">
                {purchasedBooks.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}

function BookCard({ book }: { book: Book }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">{book.title}</h3>
            <Badge variant="secondary">{book.source}</Badge>
          </div>
          <p className="text-sm text-muted-foreground">著者: {book.author || 'N/A'}</p>
          {book.remaining_time && (
            <p className="text-sm text-blue-600 flex items-center gap-1">
              <Clock className="h-4 w-4" />
              残り時間: {book.remaining_time}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

