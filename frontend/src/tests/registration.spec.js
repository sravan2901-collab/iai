import { test, expect } from '@playwright/test';

test.describe('AksharAI Registration & Auth Modal E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Open frontend app
    await page.goto('http://127.0.0.1:5173');
  });

  test('TC-01: Successful Registration with Strong Password', async ({ page }) => {
    // Click Login/Register button
    await page.click('button:has-text("Login / Create Account")');
    
    // Switch to Register mode
    await page.click('button:has-text("Need an account? Register")');

    // Fill form
    await page.fill('input[name="fullName"]', 'Test Learner');
    await page.fill('input[name="username"]', `user_${Date.now()}`);
    await page.fill('input[name="email"]', `learner_${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'StrongP@ss123');

    // Submit registration
    await page.click('button:has-text("Register & Verify Email")');

    // Expect success message or email verification banner
    await expect(page.locator('text=Registration successful!')).toBeVisible();
    await expect(page.locator('text=Verify Your Email Address')).toBeVisible();
  });

  test('TC-02: Weak Password Enforcement Disables Submit Button', async ({ page }) => {
    await page.click('button:has-text("Login / Create Account")');
    await page.click('button:has-text("Need an account? Register")');

    await page.fill('input[name="fullName"]', 'Weak User');
    await page.fill('input[name="username"]', 'weakuser123');
    await page.fill('input[name="email"]', 'weak@example.com');
    
    // Type weak password
    await page.fill('input[name="password"]', 'weak123');

    // Submit button should be disabled
    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeDisabled();

    // Check checklist indicators
    await expect(page.locator('text=8+ Characters')).toBeVisible();
  });

  test('TC-03: Duplicate Username Rejection', async ({ page }) => {
    await page.click('button:has-text("Login / Create Account")');
    await page.click('button:has-text("Need an account? Register")');

    const duplicateUsername = 'existing_alex';

    // First Registration
    await page.fill('input[name="fullName"]', 'Alex One');
    await page.fill('input[name="username"]', duplicateUsername);
    await page.fill('input[name="email"]', `alex1_${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'StrongP@ss123');
    await page.click('button:has-text("Register & Verify Email")');

    // Close and open modal again
    await page.click('button:has-text("Login / Create Account")');
    await page.click('button:has-text("Need an account? Register")');

    // Attempt registration with duplicate username
    await page.fill('input[name="fullName"]', 'Alex Two');
    await page.fill('input[name="username"]', duplicateUsername);
    await page.fill('input[name="email"]', `alex2_${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'StrongP@ss123');
    await page.click('button:has-text("Register & Verify Email")');

    // Expect red alert banner
    await expect(page.locator('text=Username already exists')).toBeVisible();
  });

  test('TC-04: Duplicate Email Rejection', async ({ page }) => {
    await page.click('button:has-text("Login / Create Account")');
    await page.click('button:has-text("Need an account? Register")');

    const duplicateEmail = `same_email_${Date.now()}@example.com`;

    // First Registration
    await page.fill('input[name="fullName"]', 'User A');
    await page.fill('input[name="username"]', `user_a_${Date.now()}`);
    await page.fill('input[name="email"]', duplicateEmail);
    await page.fill('input[name="password"]', 'StrongP@ss123');
    await page.click('button:has-text("Register & Verify Email")');

    // Close and try registering another user with same email
    await page.click('button:has-text("Login / Create Account")');
    await page.click('button:has-text("Need an account? Register")');

    await page.fill('input[name="fullName"]', 'User B');
    await page.fill('input[name="username"]', `user_b_${Date.now()}`);
    await page.fill('input[name="email"]', duplicateEmail);
    await page.fill('input[name="password"]', 'StrongP@ss123');
    await page.click('button:has-text("Register & Verify Email")');

    // Expect red alert banner
    await expect(page.locator('text=Email already exists')).toBeVisible();
  });

});
