const { test, expect } = require('@playwright/test');

test('HUD Frontpage Visual Check', async ({ page }) => {
  await page.goto('http://localhost:8080');
  await page.waitForTimeout(5000); // Wait for GSAP/Three.js
  await page.screenshot({ path: 'verification/hud_final.png', fullPage: true });
});

test('Streamlit Dashboard Visual Check', async ({ page }) => {
  await page.goto('http://localhost:8501');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'verification/streamlit_final.png', fullPage: true });
});
