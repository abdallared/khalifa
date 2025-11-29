#!/usr/bin/env node

/**
 * إصلاح مشاكل WPPConnect
 * WhatsApp Connection Troubleshooter
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 WhatsApp Connection Troubleshooter');
console.log('=====================================');

// 1. حذف ملفات الجلسة القديمة
function clearOldSessions() {
    console.log('\n1. Clearing old sessions...');
    
    const tokensPath = path.join(__dirname, 'tokens');
    if (fs.existsSync(tokensPath)) {
        try {
            fs.rmSync(tokensPath, { recursive: true, force: true });
            console.log('✅ Old sessions cleared');
        } catch (error) {
            console.log('❌ Error clearing sessions:', error.message);
        }
    } else {
        console.log('ℹ️  No old sessions found');
    }
}

// 2. حذف ملفات الرفع القديمة
function clearOldUploads() {
    console.log('\n2. Clearing old uploads...');
    
    const uploadsPath = path.join(__dirname, 'uploads');
    if (fs.existsSync(uploadsPath)) {
        try {
            const files = fs.readdirSync(uploadsPath);
            let deletedCount = 0;
            
            files.forEach(file => {
                const filePath = path.join(uploadsPath, file);
                const stats = fs.statSync(filePath);
                
                // حذف الملفات الأقدم من 24 ساعة
                const ageHours = (Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60);
                if (ageHours > 24) {
                    fs.unlinkSync(filePath);
                    deletedCount++;
                }
            });
            
            console.log(`✅ Deleted ${deletedCount} old upload files`);
            
        } catch (error) {
            console.log('❌ Error clearing uploads:', error.message);
        }
    } else {
        console.log('ℹ️  No uploads folder found');
    }
}

// 3. فحص متطلبات النظام
function checkSystemRequirements() {
    console.log('\n3. Checking system requirements...');
    
    // فحص Node.js
    const nodeVersion = process.version;
    console.log(`📦 Node.js version: ${nodeVersion}`);
    
    if (parseInt(nodeVersion.split('.')[0].replace('v', '')) < 16) {
        console.log('⚠️  Warning: Node.js 16+ recommended');
    } else {
        console.log('✅ Node.js version OK');
    }
    
    // فحص package.json
    const packagePath = path.join(__dirname, 'package.json');
    if (fs.existsSync(packagePath)) {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        console.log(`📦 WPPConnect version: ${pkg.dependencies['@wppconnect-team/wppconnect']}`);
        console.log('✅ Package.json found');
    } else {
        console.log('❌ Package.json not found');
    }
}

// 4. فحص المنافذ
function checkPorts() {
    console.log('\n4. Checking ports...');
    
    const net = require('net');
    const port = process.env.WPPCONNECT_PORT || process.env.PORT || 3000;
    
    const server = net.createServer();
    
    server.listen(port, (err) => {
        if (err) {
            console.log(`❌ Port ${port} is busy`);
        } else {
            console.log(`✅ Port ${port} is available`);
            server.close();
        }
    });
    
    server.on('error', (err) => {
        console.log(`❌ Port ${port} is busy: ${err.message}`);
    });
}

// 5. إعدادات مُحسَّنة
function generateOptimizedConfig() {
    console.log('\n5. Generating optimized configuration...');
    
    const optimizedConfig = `
// ✅ إعدادات محسنة لـ WPPConnect
const wppconnectConfig = {
    session: '${process.env.WPPCONNECT_SESSION_NAME || 'khalifa-pharmacy'}',
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
`;
    
    const configPath = path.join(__dirname, 'wppconnect-optimized-config.js');
    fs.writeFileSync(configPath, optimizedConfig);
    
    console.log(`✅ Optimized config saved to: ${configPath}`);
}

// تشغيل جميع الإصلاحات
async function runAll() {
    console.log('🚀 Running all fixes...\n');
    
    clearOldSessions();
    clearOldUploads();
    checkSystemRequirements();
    checkPorts();
    generateOptimizedConfig();
    
    console.log('\n✅ Troubleshooting complete!');
    console.log('\n📋 Next steps:');
    console.log('1. npm install (if needed)');
    console.log('2. npm start');
    console.log('3. Scan QR code when it appears');
    console.log('\n💡 If issues persist:');
    console.log('- Try: npm update @wppconnect-team/wppconnect');
    console.log('- Check Chrome installation');
    console.log('- Run this script again');
}

// تشغيل النص البرمجي
if (require.main === module) {
    runAll();
}

module.exports = {
    clearOldSessions,
    clearOldUploads,
    checkSystemRequirements,
    checkPorts,
    generateOptimizedConfig
};