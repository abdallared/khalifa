
// ✅ إعدادات محسنة لـ WPPConnect
const wppconnectConfig = {
    session: 'khalifa-pharmacy',
    headless: true,
    devtools: false,
    useChrome: false,
    debug: false,
    logQR: true,
    autoClose: 180000, // 3 دقائق
    disableWelcome: true,
    updatesLog: false,
    disableSpins: true,
    disableGoogleAnalytics: true,
    waitForLogin: true,
    logLevel: 'error',
    folderNameToken: './tokens',
    mkdirFolderToken: '',
    waitForInjectToken: 15000, // زيادة المهلة لـ wapi.js
    puppeteerOptions: {
        headless: true,
        timeout: 60000, // زيادة المهلة العامة
        slowMo: 200, // إبطاء أكثر
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-sync'
        ],
        ignoreDefaultArgs: ['--disable-extensions'],
        defaultViewport: null,
        devtools: false
    },
    createPathFileToken: true,
    waitForLogin: true
};

module.exports = wppconnectConfig;
