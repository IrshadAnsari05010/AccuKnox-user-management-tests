import { Page } from '@playwright/test';

export class LoginPage {
    private page: Page;
    private usernameInput = 'input[name="username"]';
    private passwordInput = 'input[name="password"]';
    private loginButton = 'button[type="submit"]';

    constructor(page: Page) {
        this.page = page;
    }

    async navigate() {
        await this.page.goto('https://opensource-demo.orangehrmlive.com/web/index.php/auth/login', {
            waitUntil: 'domcontentloaded'
        });
    }

    async login(username: string, password: string) {
        await this.page.locator(this.usernameInput).fill(username);
        await this.page.locator(this.passwordInput).fill(password);
        await this.page.locator(this.loginButton).click();
    }
}