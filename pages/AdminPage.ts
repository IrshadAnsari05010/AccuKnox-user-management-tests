import { Page, expect } from '@playwright/test';

export class AdminPage {
    private page: Page;

    // Direct, highly accurate selectors matching the system DOM layout tree
    private adminMenu = 'role=link[name="Admin"]';
    private addButton = 'role=button[name=" Add"]';
    private selectArrows = '.oxd-icon.bi-caret-down-fill.oxd-select-text--arrow';
    private saveButton = 'role=button[name="Save"]';
    private searchButton = 'role=button[name="Search"]';
    private deleteConfirmButton = 'role=button[name=" Yes, Delete"]';
    private successToast = '.oxd-toast-container';

    constructor(page: Page) {
        this.page = page;
    }

    async navigateToAdmin() {
        await this.page.locator(this.adminMenu).click();
        await this.page.waitForLoadState('networkidle');
    }

    async addUser(username: string, pass: string) {
        await this.page.locator(this.addButton).click();
        await this.page.waitForLoadState('domcontentloaded');

        // 1. Select User Role: ESS
        await this.page.locator(this.selectArrows).first().click();
        await this.page.getByRole('option', { name: 'ESS' }).click();

        // 2. Handle Employee Name (The Blunt-Force Fix)
        const employeeInput = this.page.getByPlaceholder('Type for hints...');
        await employeeInput.click();
        await employeeInput.fill('a');
        
        // CRITICAL FIX: Stop the script entirely for 3 seconds. 
        // This guarantees the "Searching..." text disappears and the real employee names load from the server.
        await this.page.waitForTimeout(3000);
        
        // Now that the real names are definitely there, click the first one.
        await this.page.locator('.oxd-autocomplete-option').first().click();

        // 3. Select Status: Enabled
        await this.page.locator(this.selectArrows).last().click();
        await this.page.getByRole('option', { name: 'Enabled' }).click();

        // 4. Input unique user profile values
        await this.page.getByRole('textbox').nth(2).fill(username);
        await this.page.locator('input[type="password"]').nth(0).fill(pass);
        await this.page.locator('input[type="password"]').nth(1).fill(pass);

        // Click save and observe application confirmation toast
        await this.page.locator(this.saveButton).click();
        await this.page.waitForSelector(this.successToast, { timeout: 15000 });
    }

    async searchUser(username: string) {
        const inputField = this.page.getByRole('textbox').nth(1);
        await inputField.click();
        await inputField.fill(username);
        await this.page.locator(this.searchButton).click();
        await this.page.waitForTimeout(2000);
    }

    async verifyUserInResults(username: string) {
        const row = this.page.locator('.oxd-table-card', { hasText: username });
        await expect(row).toBeVisible({ timeout: 6000 });
    }

    async editUserToAdmin(username: string) {
        await this.page.locator('.oxd-table-card', { hasText: username }).locator('.bi-pencil-fill').click();
        await this.page.waitForLoadState('domcontentloaded');

        await this.page.locator(this.selectArrows).first().click();
        await this.page.getByRole('option', { name: 'Admin' }).click();

        await this.page.locator(this.saveButton).click();
        await this.page.waitForSelector(this.successToast, { timeout: 10000 });
    }

    async verifyUpdatedRole(username: string) {
        const row = this.page.locator('.oxd-table-card', { hasText: username });
        await expect(row).toContainText('Admin');
    }

    async deleteUser(username: string) {
        await this.page.locator('.oxd-table-card', { hasText: username }).locator('.bi-trash').click();
        await this.page.locator(this.deleteConfirmButton).click();
        await this.page.waitForSelector(this.successToast, { timeout: 10000 });
    }

    async verifyUserDeleted(username: string) {
        await this.searchUser(username);
        const emptyState = this.page.locator('text=No Records Found').first();
        await expect(emptyState).toBeVisible();
    }
}