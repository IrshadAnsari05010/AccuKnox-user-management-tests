import { test } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { AdminPage } from '../pages/AdminPage';

test.describe('OrangeHRM - User Management E2E Flow', () => {
    let loginPage: LoginPage;
    let adminPage: AdminPage;
    
    // Generates a unique string identifier dynamically for every test run
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const uniqueUsername = `KnoxQA_${randomSuffix}`;

    test.beforeEach(async ({ page }) => {
        test.setTimeout(60000);
        loginPage = new LoginPage(page);
        adminPage = new AdminPage(page);
        
        await loginPage.navigate();
        await loginPage.login('Admin', 'admin123');
    });

    test('Execute E2E User Management Lifecycle', async () => {
        test.setTimeout(90000);

        // 1. Navigate to Admin
        await adminPage.navigateToAdmin();

        // 2. Add New User
        await adminPage.addUser(uniqueUsername, 'SecureKnox@2026!');

        // 3. Search Newly Created User
        await adminPage.navigateToAdmin();
        await adminPage.searchUser(uniqueUsername);
        await adminPage.verifyUserInResults(uniqueUsername);

        // 4 & 5. Edit Details and Validate Update
        await adminPage.editUserToAdmin(uniqueUsername);
        await adminPage.navigateToAdmin();
        await adminPage.searchUser(uniqueUsername);
        await adminPage.verifyUpdatedRole(uniqueUsername);

        // 6. Delete User and Verify Complete Removal
        await adminPage.deleteUser(uniqueUsername);
        await adminPage.verifyUserDeleted(uniqueUsername);
    });
});