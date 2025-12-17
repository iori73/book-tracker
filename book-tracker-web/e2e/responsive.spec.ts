import { test, expect } from '@playwright/test';

test.describe('Responsive Design Check', () => {
  test('Dashboard loads correctly on all devices', async ({ page }) => {
    await page.goto('/');
    
    // タイトルの確認
    await expect(page.getByRole('heading', { name: 'Book Tracker' })).toBeVisible();
    
    // 統計カードが表示されているか
    await expect(page.getByText('総冊数')).toBeVisible();
    
    // スクリーンショット撮影
    await page.screenshot({ path: `e2e/screenshots/dashboard-${test.info().project.name}.png` });
  });

  test('Books list page is responsive', async ({ page }) => {
    await page.goto('/books');
    
    // タイトルの確認
    await expect(page.getByRole('heading', { name: '本の一覧' })).toBeVisible();
    
    // 検索入力が表示されているか
    await expect(page.getByPlaceholder('タイトルを入力...')).toBeVisible();
    
    // スクリーンショット撮影
    await page.screenshot({ path: `e2e/screenshots/books-${test.info().project.name}.png` });
  });
  
  test('Categories page is responsive', async ({ page }) => {
    await page.goto('/categories');
    
    // タイトルの確認
    await expect(page.getByRole('heading', { name: 'カテゴリ' })).toBeVisible();
    
    // スクリーンショット撮影
    await page.screenshot({ path: `e2e/screenshots/categories-${test.info().project.name}.png` });
  });
});

