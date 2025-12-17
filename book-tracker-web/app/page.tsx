'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BookOpen, CheckCircle2, Clock, ShoppingCart, Folder, Check, MessageSquare } from 'lucide-react';

interface Statistics {
  source: string;
  status: string;
  count: number;
}

interface CategorySummary {
  category: string;
  total_books: number;
  completed: number;
  in_progress: number;
  not_started: number;
  purchased: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Statistics[]>([]);
  const [categories, setCategories] = useState<CategorySummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data.stats);
      setCategories(data.categories);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalBooks = stats.reduce((sum, s) => sum + s.count, 0);
  const completed = stats.find(s => s.status === 'completed')?.count || 0;
  const inProgress = stats.find(s => s.status === 'in_progress')?.count || 0;
  const notStarted = stats.find(s => s.status === 'not_started')?.count || 0;
  const purchased = stats.find(s => s.status === 'purchased')?.count || 0;
  
  const audibleBooks = stats.filter(s => s.source === 'Audible').reduce((sum, s) => sum + s.count, 0);
  const kindleBooks = stats.filter(s => s.source === 'Kindle').reduce((sum, s) => sum + s.count, 0);
  
  const completionRate = totalBooks > 0 ? ((completed / totalBooks) * 100).toFixed(1) : '0.0';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* ヘッダー */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <BookOpen className="h-8 w-8" />
          <h1 className="text-4xl font-bold tracking-tight">Book Tracker</h1>
        </div>
        <p className="text-muted-foreground">あなたの読書を管理するダッシュボード</p>
      </div>

      {/* メトリクス */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">総冊数</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalBooks}冊</div>
            <p className="text-xs text-muted-foreground">
              Audible {audibleBooks}冊 / Kindle {kindleBooks}冊
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">完了</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completed}冊</div>
            <p className="text-xs text-muted-foreground">
              完了率 {completionRate}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">進行中</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{inProgress}冊</div>
            <p className="text-xs text-muted-foreground">
              今読んでいる本
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">未読・購入済み</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{notStarted + purchased}冊</div>
            <p className="text-xs text-muted-foreground">
              未読 {notStarted}冊 / 購入済み {purchased}冊
            </p>
          </CardContent>
        </Card>
      </div>

      {/* カテゴリTop 10 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Folder className="h-5 w-5" />
            カテゴリTop 10
          </CardTitle>
          <CardDescription>カテゴリ別の読書状況</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {categories.slice(0, 10).map((category) => (
              <div key={category.category} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{category.category}</span>
                    <Badge variant="secondary">{category.total_books}冊</Badge>
                  </div>
                  <div className="flex gap-2 text-sm text-muted-foreground">
                    {category.completed > 0 && (
                      <span className="flex items-center gap-1 text-green-600">
                        <Check className="h-3 w-3" />
                        {category.completed}
                      </span>
                    )}
                    {category.in_progress > 0 && (
                      <span className="flex items-center gap-1 text-blue-600">
                        <BookOpen className="h-3 w-3" />
                        {category.in_progress}
                      </span>
                    )}
                    {category.not_started > 0 && (
                      <span className="flex items-center gap-1 text-gray-600">
                        <BookOpen className="h-3 w-3" />
                        {category.not_started}
                      </span>
                    )}
                    {category.purchased > 0 && (
                      <span className="flex items-center gap-1 text-amber-600">
                        <ShoppingCart className="h-3 w-3" />
                        {category.purchased}
                      </span>
                    )}
                  </div>
        </div>
                <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
                  <div className="flex h-full">
                    <div
                      className="bg-green-500"
                      style={{
                        width: `${(category.completed / category.total_books) * 100}%`,
                      }}
                    />
                    <div
                      className="bg-blue-500"
                      style={{
                        width: `${(category.in_progress / category.total_books) * 100}%`,
                      }}
                    />
                    <div
                      className="bg-gray-400"
                      style={{
                        width: `${(category.not_started / category.total_books) * 100}%`,
                      }}
                    />
                    <div
                      className="bg-amber-500"
                      style={{
                        width: `${(category.purchased / category.total_books) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* クイックリンク */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => window.location.href = '/books'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              本を探す
            </CardTitle>
            <CardDescription>タイトル、著者、カテゴリで検索</CardDescription>
          </CardHeader>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors" onClick={() => window.location.href = '/categories'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Folder className="h-5 w-5" />
              カテゴリで探す
            </CardTitle>
            <CardDescription>カテゴリ別に本を閲覧</CardDescription>
          </CardHeader>
        </Card>
        </div>
    </div>
  );
}
