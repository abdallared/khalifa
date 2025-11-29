/**
 * WPPConnect Server for Khalifa Pharmacy
 * خادم WPPConnect لصيدليات خليفة
 * 
 * المهام:
 * 1. الاتصال بـ WhatsApp عبر QR Code
 * 2. استقبال الرسائل من WhatsApp
 * 3. إرسال الرسائل إلى WhatsApp
 * 4. إرسال الرسائل الواردة إلى Django عبر Webhook
 */

// Load environment variables from parent directory first, then local
require('dotenv').config({ path: '../.env' });
require('dotenv').config(); // This will override with local .env if exists

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios');
const https = require('https');
const wppconnect = require('@wppconnect-team/wppconnect');
const redis = require('redis');
const fs = require('fs');
const path = require('path');

// ✅ تجاهل أخطاء SSL للـ localhost (Development only)
const httpsAgent = new https.Agent({
    rejectUnauthorized: false
});

// ============================================
// Configuration
// ============================================
const app = express();
const PORT = process.env.WPPCONNECT_PORT || process.env.PORT || 3000;
const HOST = process.env.WPPCONNECT_HOST || process.env.HOST || '0.0.0.0';
const SESSION_NAME = process.env.WPPCONNECT_SESSION_NAME || process.env.SESSION_NAME || 'khalifa-pharmacy';
const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://127.0.0.1:8000';
const DJANGO_WEBHOOK_ENDPOINT = process.env.DJANGO_WEBHOOK_ENDPOINT || '/api/whatsapp/webhook/';
const API_KEY = process.env.WHATSAPP_API_KEY || process.env.API_KEY || 'khalifa-pharmacy-secret-key-2025';

// ============================================
// Middleware
// ============================================
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// خدمة الملفات المرفوعة
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// API Key Authentication Middleware
const authenticateAPIKey = (req, res, next) => {
    const apiKey = req.headers['x-api-key'];
    if (apiKey && apiKey === API_KEY) {
        next();
    } else {
        res.status(401).json({ error: 'Unauthorized: Invalid API Key' });
    }
};

// ============================================
// Global Variables
// ============================================
let client = null;
let isClientReady = false;
let redisClient = null;

// إنشاء مجلد للملفات المرفوعة
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// ============================================
// Redis Setup (Optional)
// ============================================
async function setupRedis() {
    // Redis is optional - skip if not available
    console.log('⚠️  Redis is optional - skipping for now');
    redisClient = null;
}

// ============================================
// WPPConnect Client Setup
// ============================================

let clientStartAttempts = 0;
const MAX_CLIENT_START_ATTEMPTS = 3;

async function startWhatsAppClient() {
    try {
        clientStartAttempts++;
        console.log(`🚀 Starting WhatsApp Client... (Attempt ${clientStartAttempts}/${MAX_CLIENT_START_ATTEMPTS})`);

        let chromeExecutablePath = process.env.CHROME_PATH;
        if (!chromeExecutablePath) {
            const candidates = [
                'C\\\:\\Program Files\\\Google\\\Chrome\\\Application\\\chrome.exe',
                'C\\\:\\Program Files (x86)\\\Google\\\Chrome\\\Application\\\chrome.exe'
            ];
            for (const p of candidates) {
                const normalized = p.replace(/\\\\/g, '\\');
                if (fs.existsSync(normalized)) {
                    chromeExecutablePath = normalized;
                    break;
                }
            }
        }

        const userDataDir = path.join(__dirname, 'tokens', SESSION_NAME);

        if (clientStartAttempts > 1 && process.env.CLEAR_TOKENS_ON_RETRY === '1') {
            console.log('🔄 Clearing old session for fresh start...');
            const tokenPath = path.join(__dirname, 'tokens', SESSION_NAME);
            if (fs.existsSync(tokenPath)) {
                try {
                    fs.rmSync(tokenPath, { recursive: true, force: true });
                    console.log('✅ Old session cleared');
                } catch (clearError) {
                    console.warn('⚠️  Could not clear old session:', clearError.message);
                }
            }
        }

        client = await wppconnect.create({
            session: SESSION_NAME,
            catchQR: (base64Qr, asciiQR, attempts, urlCode) => {
                console.log('📱 QR Code Generated (Attempt:', attempts, ')');
                console.log(asciiQR); // QR Code في الـ Terminal

                // حفظ QR Code في Redis للعرض في الواجهة
                if (redisClient) {
                    redisClient.set('whatsapp:qr_code', base64Qr, { EX: 60 });
                    redisClient.set('whatsapp:qr_url', urlCode, { EX: 60 });
                }
            },
            statusFind: (statusSession, session) => {
                console.log('📊 Status:', statusSession);

                if (statusSession === 'qrReadSuccess') {
                    console.log('✅ QR Code Scanned Successfully!');
                }

                if (statusSession === 'isLogged') {
                    console.log('✅ WhatsApp Connected!');
                    isClientReady = true;
                }

                if (statusSession === 'notLogged') {
                    console.log('⚠️  Not Logged In - Please Scan QR Code');
                    isClientReady = false;
                }

                if (statusSession === 'autocloseCalled') {
                    console.log('⚠️  Auto-close called - Session timeout');
                }

                if (statusSession === 'desconnectedMobile') {
                    console.log('⚠️  Mobile disconnected');
                }
            },
            headless: true,
            devtools: false,
            useChrome: true,
            debug: false,
            logQR: true,
            // إعدادات حفظ الجلسة
            autoClose: 0,
            disableWelcome: true, // تعطيل رسالة الترحيب
            updatesLog: false, // تعطيل سجل التحديثات
            disableSpins: true, // منع إعادة تحميل الصفحة
            disableGoogleAnalytics: true, // تعطيل Google Analytics
            waitForLogin: true, // انتظار تسجيل الدخول
            logLevel: 'error', // تقليل السجلات
            // حفظ بيانات الجلسة
            folderNameToken: './tokens', // مجلد حفظ الجلسات
            mkdirFolderToken: '', // مجلد فرعي (فارغ = المجلد الرئيسي)
            // إعدادات المتصفح محدثة لحل مشكلة ProtocolError
            browserArgs: [
                `--user-data-dir=${userDataDir}`,
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-web-security',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor,TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--mute-audio',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--disable-background-networking',
                '--disable-domain-reliability',
                '--disable-component-update',
                '--disable-background-downloads',
                '--disable-plugins-discovery',
                '--disable-prompt-on-repost',
                '--disable-hang-monitor',
                '--disable-logging',
                '--disable-notifications',
                '--disable-permissions-api'
            ],
            // إعدادات Puppeteer محدثة لحل مشكلة DOM.resolveNode
            puppeteerOptions: {
                headless: true,
                channel: 'chrome',
                executablePath: chromeExecutablePath,
                args: [
                    `--user-data-dir=${userDataDir}`,
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor,TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-default-apps',
                    '--mute-audio',
                    '--disable-client-side-phishing-detection',
                    '--disable-sync',
                    '--disable-background-networking',
                    '--disable-domain-reliability',
                    '--disable-component-update',
                    '--disable-background-downloads',
                    '--disable-plugins-discovery',
                    '--disable-prompt-on-repost',
                    '--disable-hang-monitor',
                    '--disable-logging',
                    '--disable-notifications',
                    '--disable-permissions-api'
                ],
                ignoreDefaultArgs: ['--disable-extensions'],
                defaultViewport: null,
                devtools: false,
                // إضافة إعدادات مهلة زمنية
                timeout: 30000,
                slowMo: 100 // إبطاء العمليات لتجنب مشاكل التوقيت
            },
            // إعدادات إضافية لحل مشاكل wapi.js injection
            waitForInjectToken: 10000, // انتظار 10 ثواني قبل حقن wapi.js
            waitForLogin: true,
            createPathFileToken: true
        });

        // ============================================
        // Event Listeners
        // ============================================
        
        // عند استقبال رسالة
        client.onMessage(async (message) => {
            try {
                console.log('📩 New Message Received:', message.from);
                
                // تجاهل الرسائل من المجموعات
                if (message.isGroupMsg) {
                    console.log('⏭️  Skipping group message');
                    return;
                }
                
                // تجاهل الرسائل القديمة (أكثر من 5 دقائق)
                const messageAge = Date.now() - (message.timestamp * 1000);
                if (messageAge > 5 * 60 * 1000) {
                    console.log('⏭️  Skipping old message');
                    return;
                }
                
                // تحضير البيانات للإرسال إلى Django
                // ✅ الحل الجذري: استخراج الرقم الحقيقي من أي صيغة!
                let chatIdForReply = message.from; // الافتراضي
                let displayPhone = message.from.replace('@c.us', '').replace('@lid', '');
                let realPhone = null;

                // ✅ دائماً نحاول الحصول على الرقم الحقيقي من WPP.contact
                console.log('🔍 Looking up contact info for:', message.from);
                try {
                    const contactInfo = await client.page.evaluate(
                        async ({ chatId }) => {
                            try {
                                const contact = await WPP.contact.get(chatId);
                                const fullData = {
                                    id: contact?.id?._serialized,
                                    user: contact?.id?.user,
                                    name: contact?.name,
                                    pushname: contact?.pushname,
                                    formattedNumber: contact?.formattedNumber,
                                    number: contact?.number,
                                    phoneNumber: contact?.phoneNumber
                                };
                                
                                // محاولة الحصول على الرقم الحقيقي من البيانات المتاحة
                                let actualPhone = null;
                                if (contact?.phoneNumber) {
                                    actualPhone = contact.phoneNumber.replace('@c.us', '').replace('@lid', '');
                                } else if (contact?.number) {
                                    actualPhone = contact.number;
                                } else if (contact?.formattedNumber) {
                                    actualPhone = contact.formattedNumber.replace(/\D/g, '');
                                }
                                
                                fullData.actualPhone = actualPhone;
                                return fullData;
                            } catch (e) {
                                return { error: e.message };
                            }
                        },
                        { chatId: message.from }
                    );

                    console.log('📞 Contact info:', JSON.stringify(contactInfo));

                    // USE THE NEW EXTRACTION FUNCTION
                    realPhone = extractRealPhoneNumber(message, contactInfo);
                    
                    // Check if this is a LID (Local ID)
                    if (message.from && message.from.includes('@lid')) {
                        // This is a WhatsApp Business Local ID
                        console.log('🔒 Detected WhatsApp Local ID (LID)');
                        
                        // For LIDs, we must use the original format for replies
                        chatIdForReply = message.from;  // Keep the @lid format
                        
                        // Extract the LID number for storage
                        const lidNumber = message.from.split('@')[0];
                        displayPhone = lidNumber;  // Store the LID as the "phone"
                        
                        console.log(`📱 LID Number: ${lidNumber}`);
                        console.log(`📱 Reply to: ${chatIdForReply}`);
                        
                        // Note: We can't get the real phone for LID users
                        realPhone = lidNumber;
                    } else {
                        // Regular phone number
                        chatIdForReply = realPhone + '@c.us';
                        displayPhone = realPhone;
                    }
                    
                    console.log('✅ Final phone number:', realPhone);
                    console.log('✅ Will reply to:', chatIdForReply);

                } catch (contactError) {
                    console.log('❌ Contact lookup failed:', contactError.message);
                    
                    // Fallback - still use the extraction function
                    realPhone = extractRealPhoneNumber(message, null);
                    chatIdForReply = realPhone + '@c.us';
                    displayPhone = realPhone;
                    console.log('✅ Fallback extraction result:', realPhone);
                }

                // ✅ Map message types (normalize PTT to audio)
                let normalizedType = message.type || 'chat';
                if (message.type === 'ptt') {
                    normalizedType = 'audio';
                }

                const messageData = {
                    id_ext: message.id,
                    phone: realPhone,                 // ✅ ALWAYS use real phone
                    chat_id: chatIdForReply,          // ✅ Real phone @c.us
                    real_phone: realPhone,            // ✅ Real phone
                    message_id: message.id,           // ✅ لحفظ ID الرسالة للرد عليها
                    message_text: message.body || '',
                    message_type: normalizedType,     // ✅ استخدام النوع المعياري
                    sender_name: message.sender.pushname || message.sender.name || '-',
                    timestamp: message.timestamp,
                    is_from_me: message.fromMe,
                    media_url: null,
                    mime_type: message.mimetype || null,
                    raw_data: message
                };

                // ✅ معالجة الملفات المرفقة بالطريقة الصحيحة (بما في ذلك PTT)
                if (message.type === 'image' || message.type === 'audio' || message.type === 'document' || message.type === 'video' || message.type === 'ptt') {
                    try {
                        console.log(`📎 Processing ${message.type} file...`);

                        // فك تشفير الملف من WhatsApp
                        const buffer = await client.decryptFile(message);

                        // إنشاء اسم ملف فريد
                        const fileExtension = getFileExtension(message.mimetype);
                        const fileName = `${Date.now()}_${message.fromMe}_${message.from}_${message.id}.${fileExtension}`;
                        const filePath = path.join(uploadsDir, fileName);

                        // حفظ الملف على القرص
                        fs.writeFileSync(filePath, buffer);

                        // تحديث بيانات الرسالة
                        messageData.media_url = `/uploads/${fileName}`;
                        messageData.message_text = message.caption || message.filename || '';

                        console.log(`✅ File saved: ${fileName} (${buffer.length} bytes)`);

                    } catch (fileError) {
                        console.error('❌ Error processing media file:', fileError);
                        // في حالة فشل معالجة الملف، نحتفظ بالرسالة بدون ميديا
                        if (message.type === 'ptt' || normalizedType === 'audio') {
                            messageData.message_text = 'Voice message - file processing failed';
                        } else {
                            messageData.message_text = `${normalizedType.toUpperCase()} file - processing failed`;
                        }
                    }
                }
                
                // إرسال إلى Django Webhook
                await sendToDjangoWebhook(messageData);
                
                // حفظ في Redis Queue (اختياري)
                if (redisClient) {
                    await redisClient.lPush('whatsapp:incoming_messages', JSON.stringify(messageData));
                }
                
            } catch (error) {
                console.error('❌ Error processing message:', error);
            }
        });

        // عند تغيير حالة الاتصال
        client.onStateChange((state) => {
            console.log('🔄 State Changed:', state);
            if (state === 'CONNECTED') {
                isClientReady = true;
                console.log('✅ WhatsApp Connected - Session Active');
            } else if (state === 'UNPAIRED') {
                isClientReady = false;
                console.log('⚠️  WhatsApp Unpaired - Session will be restored on next connection');
            } else if (state === 'DISCONNECTED' || state === 'TIMEOUT') {
                isClientReady = false;
                console.log('⚠️  WhatsApp Disconnected - Session saved, will reconnect automatically');
            }
        });

        console.log('✅ WhatsApp Client Started Successfully!');
        
    } catch (error) {
        console.error('❌ Failed to start WhatsApp Client:', error);
        console.error('Error details:', error.message);
        
        // إذا كانت المحاولة تحتوي على ProtocolError، نحاول مرة أخرى
        if (error.message.includes('Protocol error') && clientStartAttempts < MAX_CLIENT_START_ATTEMPTS) {
            console.log(`🔄 Protocol error detected, retrying in 10 seconds... (${clientStartAttempts}/${MAX_CLIENT_START_ATTEMPTS})`);
            setTimeout(() => {
                startWhatsAppClient();
            }, 10000);
            return;
        }
        
        // إذا فشلت كل المحاولات
        if (clientStartAttempts >= MAX_CLIENT_START_ATTEMPTS) {
            console.error('💀 All retry attempts failed. Please check your setup.');
            console.error('🔧 Troubleshooting suggestions:');
            console.error('   1. Clear tokens folder: rm -rf ./tokens');
            console.error('   2. Restart the server');
            console.error('   3. Check if Chrome/Chromium is properly installed');
            console.error('   4. Try updating wppconnect: npm update @wppconnect-team/wppconnect');
        }
        
        isClientReady = false;
    }
}

// ============================================
// Helper Functions
// ============================================

// Validate phone number or LID
function isValidPhoneNumber(phone) {
    // Remove any non-digits
    phone = phone.replace(/\D/g, '');
    
    // Egyptian numbers: 11-12 digits starting with 20
    if (phone.startsWith('20') && phone.length >= 11 && phone.length <= 12) {
        return true;
    }
    
    // Check if this might be a WhatsApp LID (Local ID)
    // LIDs are typically 14-15 digits and don't follow phone number patterns
    if (phone.length >= 14 && phone.length <= 15) {
        // These are actually LIDs, not phone numbers
        // We should accept them but mark them differently
        console.log(`🔒 Detected WhatsApp LID: ${phone}`);
        return 'LID';  // Return special marker for LID
    }
    
    // International numbers: 10-13 digits
    if (phone.length >= 10 && phone.length <= 13) {
        return true;
    }
    
    return false;
}

// Extract real phone number from message and contact info
function extractRealPhoneNumber(message, contactInfo) {
    console.log('🔍 Extracting phone number or LID...');
    
    // Check if this is a LID first
    if (message.from && message.from.includes('@lid')) {
        const lidNumber = message.from.split('@')[0];
        console.log(`🔒 This is a WhatsApp LID: ${lidNumber}`);
        return lidNumber;  // Return the LID as-is
    }
    
    // Priority 1: Try to get from contact info
    if (contactInfo && !contactInfo.error) {
        // Check actualPhone first
        if (contactInfo.actualPhone) {
            const phone = String(contactInfo.actualPhone).replace(/\D/g, '');
            const validation = isValidPhoneNumber(phone);
            if (validation === true || validation === 'LID') {
                console.log(`✅ Using actualPhone: ${phone}`);
                return phone;
            }
        }
        
        // Check number field
        if (contactInfo.number) {
            const phone = String(contactInfo.number).replace(/\D/g, '');
            const validation = isValidPhoneNumber(phone);
            if (validation === true || validation === 'LID') {
                console.log(`✅ Using number: ${phone}`);
                return phone;
            }
        }
        
        // Check formattedNumber
        if (contactInfo.formattedNumber) {
            const phone = String(contactInfo.formattedNumber).replace(/\D/g, '');
            const validation = isValidPhoneNumber(phone);
            if (validation === true || validation === 'LID') {
                console.log(`✅ Using formattedNumber: ${phone}`);
                return phone;
            }
        }
        
        // Check user field
        if (contactInfo.user) {
            const phone = String(contactInfo.user).replace(/\D/g, '');
            const validation = isValidPhoneNumber(phone);
            if (validation === true || validation === 'LID') {
                console.log(`✅ Using user: ${phone}`);
                return phone;
            }
        }
    }
    
    // Priority 2: Try message.sender
    if (message.sender && message.sender.id) {
        if (message.sender.id.user) {
            const phone = String(message.sender.id.user).replace(/\D/g, '');
            const validation = isValidPhoneNumber(phone);
            if (validation === true || validation === 'LID') {
                console.log(`✅ Using sender.id.user: ${phone}`);
                return phone;
            }
        }
    }
    
    // Priority 3: Try message.from
    if (message.from) {
        const phone = String(message.from).split('@')[0].replace(/\D/g, '');
        const validation = isValidPhoneNumber(phone);
        if (validation === true || validation === 'LID') {
            console.log(`✅ Using message.from: ${phone}`);
            return phone;
        }
    }
    
    // If we get here, return the raw ID
    const rawId = message.from.split('@')[0];
    console.log(`⚠️ Using raw ID: ${rawId}`);
    return rawId;
}

// إرسال الرسالة إلى Django Webhook
async function sendToDjangoWebhook(messageData) {
    try {
        const webhookUrl = `${DJANGO_BACKEND_URL}${DJANGO_WEBHOOK_ENDPOINT}`;
        console.log('📤 Sending to Django:', webhookUrl);
        
        const response = await axios.post(webhookUrl, messageData, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            timeout: 10000,
            httpsAgent: httpsAgent  // ✅ تجاهل أخطاء SSL للـ localhost
        });
        
        console.log('✅ Sent to Django successfully:', response.status);
        return response.data;
        
    } catch (error) {
        console.error('❌ Failed to send to Django:', error.message);
        if (error.response) {
            console.error('Response:', error.response.status, error.response.data);
        }
        throw error;
    }
}

// تطبيع رقم الهاتف
function normalizePhone(phone) {
    let normalized = phone.replace(/\D/g, ''); // إزالة كل شيء ما عدا الأرقام

    if (normalized.startsWith('0')) {
        normalized = '20' + normalized.substring(1);
    }

    if (!normalized.startsWith('20')) {
        normalized = '20' + normalized;
    }

    return normalized;
}

// الحصول على امتداد الملف من MIME type
function getFileExtension(mimetype) {
    const mimeMap = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'audio/ogg': 'ogg',
        'audio/mpeg': 'mp3',
        'audio/mp4': 'm4a',
        'audio/aac': 'aac',
        'video/mp4': 'mp4',
        'video/3gpp': '3gp',
        'application/pdf': 'pdf',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'txt'
    };
    return mimeMap[mimetype] || 'bin';
}

// ============================================
// API Routes
// ============================================

// Health Check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: isClientReady,
        timestamp: new Date().toISOString()
    });
});

// Get QR Code
app.get('/api/qr-code', authenticateAPIKey, async (req, res) => {
    try {
        if (isClientReady) {
            return res.json({
                success: false,
                message: 'Already connected to WhatsApp'
            });
        }
        
        if (redisClient) {
            const qrCode = await redisClient.get('whatsapp:qr_code');
            const qrUrl = await redisClient.get('whatsapp:qr_url');
            
            if (qrCode) {
                return res.json({
                    success: true,
                    qr_code: qrCode,
                    qr_url: qrUrl
                });
            }
        }
        
        res.json({
            success: false,
            message: 'QR Code not available. Please restart the server.'
        });
        
    } catch (error) {
        console.error('❌ Error getting QR Code:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get Connection Status
app.get('/api/status', authenticateAPIKey, async (req, res) => {
    try {
        const status = {
            connected: isClientReady,
            session: SESSION_NAME,
            timestamp: new Date().toISOString()
        };

        if (isClientReady && client) {
            try {
                const hostDevice = await client.getHostDevice();
                if (hostDevice && hostDevice.id) {
                    status.phone = hostDevice.id.user;
                }
                if (hostDevice && hostDevice.phone && hostDevice.phone.device_manufacturer) {
                    status.device = hostDevice.phone.device_manufacturer;
                }
            } catch (deviceError) {
                console.log('⚠️  Could not get device info:', deviceError.message);
                // Continue without device info
            }
        }

        res.json(status);

    } catch (error) {
        console.error('❌ Error getting status:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Send Text Message
app.post('/api/send-message', authenticateAPIKey, async (req, res) => {
    try {
        if (!isClientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp not connected'
            });
        }
        
        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({
                success: false,
                error: 'Phone and message are required'
            });
        }

        // ✅ إذا كان الرقم يحتوي على @ (chatId كامل)، نستخدمه مباشرة
        let chatId;
        let phoneForCheck;

        if (phone.includes('@')) {
            // الرقم يحتوي على chatId كامل (مثل 201003648984@c.us أو 25516987932689@lid)
            chatId = phone;
            phoneForCheck = phone.split('@')[0]; // استخراج الرقم للتحقق
            console.log('✅ Using provided chatId:', chatId);
        } else {
            // رقم عادي، نطبعه ونضيف @c.us
            phoneForCheck = normalizePhone(phone);
            chatId = phoneForCheck + '@c.us';
            console.log('📤 Normalized phone to chatId:', chatId);
        }

        console.log('📤 Sending message to:', chatId);

        try {
            // ✅ محاولة الحصول على الرقم الحقيقي للمستخدم من معلومات الاتصال
            // ⚠️ فقط للأرقام التي لا تحتوي على @ (أي ليست chatId كامل)
            if (!phone.includes('@')) {
                try {
                    console.log('🔍 Looking up contact for sending to:', chatId);
                    const contactInfo = await client.page.evaluate(
                        async ({ chatId }) => {
                            try {
                                const contact = await WPP.contact.get(chatId);
                                const fullData = {
                                    id: contact?.id?._serialized,
                                    user: contact?.id?.user,
                                    number: contact?.number,
                                    formattedNumber: contact?.formattedNumber,
                                    phoneNumber: contact?.phoneNumber,
                                    name: contact?.name,
                                    pushname: contact?.pushname
                                };

                                // محاولة الحصول على الرقم الحقيقي من البيانات المتاحة
                                let actualPhone = null;
                                if (contact?.phoneNumber) {
                                    actualPhone = contact.phoneNumber.replace('@c.us', '').replace('@lid', '');
                                } else if (contact?.number) {
                                    actualPhone = contact.number;
                                } else if (contact?.formattedNumber) {
                                    actualPhone = contact.formattedNumber.replace(/\D/g, '');
                                }

                                fullData.actualPhone = actualPhone;
                                return fullData;
                            } catch (e) {
                                return { error: e.message };
                            }
                        },
                        { chatId: chatId }
                    );

                    console.log('📞 Send contact info:', JSON.stringify(contactInfo));

                    // استخدام الرقم الحقيقي من actualPhone
                    if (contactInfo && contactInfo.actualPhone && contactInfo.actualPhone !== phoneForCheck) {
                        console.log(`✅ Found actual phone: ${contactInfo.actualPhone} (was ${phoneForCheck})`);
                        phoneForCheck = contactInfo.actualPhone;
                        chatId = phoneForCheck + '@c.us';
                        console.log('✅ Updated chatId to:', chatId);
                    } else if (contactInfo && contactInfo.number && contactInfo.number !== phoneForCheck) {
                        console.log(`✅ Found real phone from contact.number: ${contactInfo.number} (was ${phoneForCheck})`);
                        phoneForCheck = contactInfo.number;
                        chatId = phoneForCheck + '@c.us';
                        console.log('✅ Updated chatId to:', chatId);
                    } else if (contactInfo && contactInfo.user && contactInfo.user !== phoneForCheck) {
                        console.log(`✅ Found real phone from contact.user: ${contactInfo.user} (was ${phoneForCheck})`);
                        phoneForCheck = contactInfo.user;
                        chatId = phoneForCheck + '@c.us';
                        console.log('✅ Updated chatId to:', chatId);
                    } else {
                        console.log('ℹ️ No phone number change needed');
                    }
                } catch (contactError) {
                    console.log('⚠️ Could not get contact info:', contactError.message);
                }
            } else {
                // ✅ إذا كان chatId كامل (@lid أو @c.us)، نستخدمه كما هو بدون تعديل
                console.log('✅ Using provided chatId as-is (preserving @lid or @c.us):', chatId);
            }

            // ✅ للأرقام العادية (@c.us)
            if (!phone.includes('@')) {
                const numberExists = await client.checkNumberStatus(phoneForCheck);

                if (!numberExists || !numberExists.numberExists) {
                    console.log('❌ Number does not exist on WhatsApp:', phoneForCheck);
                    return res.status(400).json({
                        success: false,
                        error: 'Number does not exist on WhatsApp'
                    });
                }
                console.log('✅ Number exists, sending message...');
            } else {
                console.log('✅ Using existing chatId, skipping number check...');
            }

            // محاولة إرسال الرسالة
            try {
                console.log('🔄 Trying WPP.chat.sendTextMessage...');
                const result = await client.page.evaluate(
                    async ({ chatId, message }) => {
                        return await WPP.chat.sendTextMessage(chatId, message, {
                            createChat: true,
                            waitForAck: true
                        });
                    },
                    { chatId, message }
                );

                console.log('✅ Message sent successfully:', result.id);

                res.json({
                    success: true,
                    message_id: result.id || 'sent',
                    phone: phoneForCheck,
                    chat_id: chatId
                });
            } catch (wppError) {
                console.error('❌ WPP method failed:', wppError.message);

                // محاولة الطريقة القديمة كـ fallback
                console.log('🔄 Trying fallback method with client.sendText...');
                const result = await client.sendText(chatId, message);

                console.log('✅ Message sent successfully with fallback:', result.id);

                res.json({
                    success: true,
                    message_id: result.id,
                    phone: phoneForCheck,
                    chat_id: chatId
                });
            }
        } catch (sendError) {
            console.error('❌ All send methods failed:', sendError.message);
            throw sendError;
        }
        
    } catch (error) {
        console.error('❌ Error sending message:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Send Media Message (Image, Video, Document)
app.post('/api/send-media', authenticateAPIKey, async (req, res) => {
    try {
        if (!isClientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp not connected'
            });
        }
        
        const { phone, media_url, media_type, caption } = req.body;

        if (!phone || !media_url) {
            return res.status(400).json({
                success: false,
                error: 'Phone and media_url are required'
            });
        }

        // ✅ إذا كان الرقم يحتوي على @ (chatId كامل)، نستخدمه مباشرة
        let chatId;
        let phoneForCheck;

        if (phone.includes('@')) {
            // الرقم يحتوي على chatId كامل
            chatId = phone;
            phoneForCheck = phone.split('@')[0];
            console.log('✅ Using provided chatId for media:', chatId);
        } else {
            // رقم عادي، نطبعه ونضيف @c.us
            phoneForCheck = normalizePhone(phone);
            chatId = phoneForCheck + '@c.us';
            console.log('📤 Normalized phone to chatId for media:', chatId);
        }

        console.log(`📤 Sending ${media_type || 'image'} to:`, chatId);
        console.log('📸 Media URL:', media_url);
        console.log('📝 Caption:', caption || 'none');

        try {
            // ✅ لا نتحقق من وجود الرقم إذا كان chatId كامل
            if (!phone.includes('@')) {
                const numberExists = await client.checkNumberStatus(phoneForCheck);

                if (!numberExists || !numberExists.numberExists) {
                    console.log('❌ Number does not exist on WhatsApp:', phoneForCheck);
                    return res.status(400).json({
                        success: false,
                        error: 'Number does not exist on WhatsApp'
                    });
                }
                console.log('✅ Number exists, sending media...');
            } else {
                console.log('✅ Using existing chatId, skipping number check...');
            }

            // إرسال الميديا حسب النوع
            let result;
            
            if (media_type === 'image' || !media_type) {
                // إرسال صورة
                console.log('🖼️  Sending as image...');
                result = await client.sendImage(
                    chatId,
                    media_url,
                    'image',
                    caption || ''
                );
            } else if (media_type === 'video') {
                // إرسال فيديو
                console.log('🎥 Sending as video...');
                result = await client.sendFile(
                    chatId,
                    media_url,
                    'video',
                    caption || ''
                );
            } else if (media_type === 'document') {
                // إرسال مستند
                console.log('📄 Sending as document...');
                result = await client.sendFile(
                    chatId,
                    media_url,
                    'document',
                    caption || ''
                );
            } else {
                // نوع غير معروف، نرسله كملف
                console.log('📎 Sending as file...');
                result = await client.sendFile(
                    chatId,
                    media_url,
                    media_type,
                    caption || ''
                );
            }

            console.log('✅ Media sent successfully:', result.id || result);

            res.json({
                success: true,
                message_id: result.id || 'sent',
                phone: phoneForCheck,
                chat_id: chatId
            });

        } catch (sendError) {
            console.error('❌ Failed to send media:', sendError.message);
            console.error('Error details:', sendError);
            throw sendError;
        }
        
    } catch (error) {
        console.error('❌ Error sending media:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Logout/Disconnect
app.post('/api/logout', authenticateAPIKey, async (req, res) => {
    try {
        if (client) {
            await client.logout();
            isClientReady = false;
            
            res.json({
                success: true,
                message: 'Logged out successfully'
            });
        } else {
            res.json({
                success: false,
                message: 'No active session'
            });
        }
    } catch (error) {
        console.error('❌ Error logging out:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ============================================
// Start Server
// ============================================
async function startServer() {
    try {
        // Setup Redis
        await setupRedis();

        // Start Express Server FIRST
        app.listen(PORT, HOST, () => {
            console.log('');
            console.log('='.repeat(50));
            console.log('🚀 WPPConnect Server Started!');
            console.log('='.repeat(50));
            console.log(`📍 Server: http://${HOST}:${PORT}`);
            console.log(`📱 Session: ${SESSION_NAME}`);
            console.log(`🔗 Django Backend: ${DJANGO_BACKEND_URL}`);
            console.log('='.repeat(50));
            console.log('');
        });

        // Start WhatsApp Client (non-blocking)
        startWhatsAppClient().catch(err => {
            console.error('❌ WhatsApp Client Error:', err);
        });

    } catch (error) {
        console.error('❌ Failed to start server:', error);
        process.exit(1);
    }
}

// Start the server
startServer();
