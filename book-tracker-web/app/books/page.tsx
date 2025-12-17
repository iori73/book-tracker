'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Search, Filter, Edit2, CheckCircle2, BookOpen, Clock, ShoppingCart, Save, MessageSquare } from 'lucide-react';
import { Book } from '@/lib/db';

const STATUS_MAP = {
  completed: { label: '完了', color: 'bg-green-500', icon: CheckCircle2 },
  in_progress: { label: '進行中', color: 'bg-blue-500', icon: Clock },
  not_started: { label: '未読', color: 'bg-gray-500', icon: BookOpen },
  purchased: { label: '購入済み', color: 'bg-amber-500', icon: ShoppingCart },
};

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  // フィルター
  const [titleSearch, setTitleSearch] = useState('');
  const [authorSearch, setAuthorSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  
  // 編集
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [editStatus, setEditStatus] = useState('');
  const [editRemainingTime, setEditRemainingTime] = useState('');
  const [editNotes, setEditNotes] = useState('');

  useEffect(() => {
    fetchCategories();
    fetchBooks();
  }, [titleSearch, authorSearch, sourceFilter, statusFilter, categoryFilter]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/categories');
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (titleSearch) params.append('title', titleSearch);
      if (authorSearch) params.append('author', authorSearch);
      if (sourceFilter) params.append('source', sourceFilter);
      if (statusFilter) params.append('status', statusFilter);
      if (categoryFilter) params.append('category', categoryFilter);
      
      const response = await fetch(`/api/books?${params}`);
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error('Error fetching books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (book: Book) => {
    setEditingBook(book);
    setEditStatus(book.status);
    setEditRemainingTime(book.remaining_time || '');
    setEditNotes(book.notes || '');
  };

  const handleSave = async () => {
    if (!editingBook) return;
    
    try {
      const response = await fetch(`/api/books/${editingBook.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: editStatus,
          remaining_time: editRemainingTime || null,
          notes: editNotes || null,
        }),
      });
      
      if (response.ok) {
        await fetchBooks();
        setEditingBook(null);
      }
    } catch (error) {
      console.error('Error updating book:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => window.location.href = '/'}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-7 w-7" />
            <h1 className="text-3xl font-bold">本の一覧</h1>
          </div>
          <p className="text-muted-foreground">検索・フィルタリング・編集</p>
        </div>
      </div>

      {/* 検索・フィルター */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            検索・フィルター
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-2">
              <Label>タイトル検索</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="タイトルを入力..."
                  className="pl-8"
                  value={titleSearch}
                  onChange={(e) => setTitleSearch(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>著者検索</Label>
              <Input
                placeholder="著者を入力..."
                value={authorSearch}
                onChange={(e) => setAuthorSearch(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>ソース</Label>
              <Select value={sourceFilter} onValueChange={setSourceFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="すべて" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべて</SelectItem>
                  <SelectItem value="Audible">Audible</SelectItem>
                  <SelectItem value="Kindle">Kindle</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>ステータス</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="すべて" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべて</SelectItem>
                  <SelectItem value="completed" className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    完了
                  </SelectItem>
                  <SelectItem value="in_progress" className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    進行中
                  </SelectItem>
                  <SelectItem value="not_started" className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    未読
                  </SelectItem>
                  <SelectItem value="purchased" className="flex items-center gap-2">
                    <ShoppingCart className="h-4 w-4" />
                    購入済み
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>カテゴリ</Label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="すべて" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべて</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setTitleSearch('');
                  setAuthorSearch('');
                  setSourceFilter('');
                  setStatusFilter('');
                  setCategoryFilter('');
                }}
              >
                クリア
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 結果 */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          検索結果: <span className="font-semibold text-foreground">{books.length}冊</span>
        </p>
      </div>

      {/* 本のリスト */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : books.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            該当する本が見つかりませんでした
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {books.map((book) => (
            <Card key={book.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">{book.title}</h3>
                      <Badge variant="secondary">{book.source}</Badge>
                      <Badge className={`${STATUS_MAP[book.status].color} flex items-center gap-1`}>
                        {(() => {
                          const Icon = STATUS_MAP[book.status].icon;
                          return <Icon className="h-3 w-3" />;
                        })()}
                        {STATUS_MAP[book.status].label}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">著者: {book.author || 'N/A'}</p>
                    
                    {book.category && (
                      <p className="text-sm">
                        <span className="text-muted-foreground">カテゴリ:</span> {book.category}
                      </p>
                    )}
                    
                    {book.remaining_time && (
                      <p className="text-sm text-blue-600 flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        残り時間: {book.remaining_time}
                      </p>
                    )}
                    
                    {book.notes && (
                      <p className="text-sm text-muted-foreground italic flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        {book.notes}
                      </p>
                    )}
                  </div>
                  
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleEdit(book)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>本を編集</DialogTitle>
                        <DialogDescription>
                          {book.title}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>ステータス</Label>
                          <Select value={editStatus} onValueChange={setEditStatus}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="completed" className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4" />
                                完了
                              </SelectItem>
                              <SelectItem value="in_progress" className="flex items-center gap-2">
                                <Clock className="h-4 w-4" />
                                進行中
                              </SelectItem>
                              <SelectItem value="not_started" className="flex items-center gap-2">
                                <BookOpen className="h-4 w-4" />
                                未読
                              </SelectItem>
                              <SelectItem value="purchased" className="flex items-center gap-2">
                                <ShoppingCart className="h-4 w-4" />
                                購入済み
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div className="space-y-2">
                          <Label>残り時間</Label>
                          <Input
                            placeholder="例: 5時間 30分"
                            value={editRemainingTime}
                            onChange={(e) => setEditRemainingTime(e.target.value)}
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label>メモ</Label>
                          <Textarea
                            placeholder="メモを入力..."
                            value={editNotes}
                            onChange={(e) => setEditNotes(e.target.value)}
                            rows={3}
                          />
                        </div>
                        
                        <Button className="w-full" onClick={handleSave}>
                          <Save className="h-4 w-4 mr-2" />
                          保存
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

