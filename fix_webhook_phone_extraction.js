// Fix for WPPConnect webhook to properly extract phone numbers
// Problem: The webhook sometimes uses WhatsApp internal IDs (15+ digits) instead of real phone numbers

// Add this function to server.js to validate and fix phone numbers
function extractRealPhoneNumber(message, contactInfo) {
    console.log('🔍 Extracting real phone number...');
    
    // Priority 1: Try to get from contact info
    if (contactInfo) {
        // Check actualPhone first
        if (contactInfo.actualPhone) {
            const phone = contactInfo.actualPhone.replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using actualPhone: ${phone}`);
                return phone;
            }
        }
        
        // Check number field
        if (contactInfo.number) {
            const phone = contactInfo.number.replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using number: ${phone}`);
                return phone;
            }
        }
        
        // Check formattedNumber
        if (contactInfo.formattedNumber) {
            const phone = contactInfo.formattedNumber.replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using formattedNumber: ${phone}`);
                return phone;
            }
        }
        
        // Check user field
        if (contactInfo.user) {
            const phone = contactInfo.user.replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using user: ${phone}`);
                return phone;
            }
        }
    }
    
    // Priority 2: Try message.sender
    if (message.sender && message.sender.id) {
        if (message.sender.id.user) {
            const phone = message.sender.id.user.replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using sender.id.user: ${phone}`);
                return phone;
            }
        }
        
        if (message.sender.id._serialized) {
            const phone = message.sender.id._serialized.split('@')[0].replace(/\D/g, '');
            if (isValidPhoneNumber(phone)) {
                console.log(`✅ Using sender.id._serialized: ${phone}`);
                return phone;
            }
        }
    }
    
    // Priority 3: Try message.from (but validate it!)
    if (message.from) {
        const phone = message.from.split('@')[0].replace(/\D/g, '');
        if (isValidPhoneNumber(phone)) {
            console.log(`✅ Using message.from: ${phone}`);
            return phone;
        } else {
            console.log(`⚠️ message.from has invalid number: ${phone} (${phone.length} digits)`);
        }
    }
    
    // If we get here, we couldn't find a valid phone number
    console.error('❌ Could not extract valid phone number!');
    console.error('Message data:', {
        from: message.from,
        sender: message.sender,
        contactInfo: contactInfo
    });
    
    // Return the raw ID as last resort (but it will likely fail)
    return message.from.split('@')[0];
}

// Validate phone number
function isValidPhoneNumber(phone) {
    // Remove any non-digits
    phone = phone.replace(/\D/g, '');
    
    // Egyptian numbers: 11-12 digits starting with 20
    if (phone.startsWith('20') && phone.length >= 11 && phone.length <= 12) {
        return true;
    }
    
    // International numbers: 10-15 digits (but not weird IDs)
    if (phone.length >= 10 && phone.length <= 15) {
        // Reject if it looks like a WhatsApp internal ID
        // These usually have patterns like 131748608372742 (15 digits with weird prefixes)
        if (phone.length === 15 && !phone.startsWith('20')) {
            console.warn(`⚠️ Suspicious 15-digit number: ${phone}`);
            return false;
        }
        return true;
    }
    
    return false;
}

// REPLACE THE EXISTING CODE IN server.js (around line 255-320) with:
/*
// تحضير البيانات للإرسال إلى Django
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
                return {
                    id: contact?.id?._serialized,
                    user: contact?.id?.user,
                    name: contact?.name,
                    pushname: contact?.pushname,
                    formattedNumber: contact?.formattedNumber,
                    number: contact?.number,
                    phoneNumber: contact?.phoneNumber,
                    actualPhone: contact?.phoneNumber?.replace('@c.us', '').replace('@lid', '') || 
                                 contact?.number || 
                                 contact?.formattedNumber?.replace(/\D/g, '')
                };
            } catch (e) {
                return { error: e.message };
            }
        },
        { chatId: message.from }
    );

    console.log('📞 Contact info:', JSON.stringify(contactInfo));
    
    // USE THE NEW FUNCTION HERE
    realPhone = extractRealPhoneNumber(message, contactInfo);
    
    // Always use the real phone for everything
    chatIdForReply = realPhone + '@c.us';
    displayPhone = realPhone;
    
    console.log('✅ Final phone number:', realPhone);
    console.log('✅ Will reply to:', chatIdForReply);

} catch (contactError) {
    console.log('❌ Contact lookup failed:', contactError.message);
    
    // Fallback
    realPhone = extractRealPhoneNumber(message, null);
    chatIdForReply = realPhone + '@c.us';
    displayPhone = realPhone;
}

const messageData = {
    id_ext: message.id,
    phone: realPhone,                    // ✅ ALWAYS use real phone
    chat_id: chatIdForReply,            // ✅ Real phone @c.us
    real_phone: realPhone,               // ✅ Real phone
    message_id: message.id,
    message_text: message.body || '',
    message_type: normalizedType,
    sender_name: message.sender.pushname || message.sender.name || '-',
    timestamp: message.timestamp,
    is_from_me: message.fromMe,
    media_url: null,
    mime_type: message.mimetype || null,
    raw_data: message
};
*/