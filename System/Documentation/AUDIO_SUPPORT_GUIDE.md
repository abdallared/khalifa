# 🎤 Audio Message Support Guide

## Overview
The Khalifa Pharmacy WhatsApp system now fully supports audio messages (voice notes) from WhatsApp. Agents can receive and play audio messages directly in the conversation interface.

## ✅ Supported Features

### Audio File Types
- **OGG** (WhatsApp default for voice notes)
- **MP3** 
- **M4A**
- **AAC**

### Message Types Supported
1. **Audio** - Voice notes with inline player
2. **Image** - Pictures with preview
3. **Document** - PDF, DOC, etc. with download link
4. **Video** - Video files with download link
5. **Text** - Regular text messages

## 🔧 Technical Implementation

### Backend (Django)
The `Message` model already supports audio files:
```python
MESSAGE_TYPE_CHOICES = [
    ('text', 'Text'),
    ('image', 'Image'),
    ('audio', 'Audio'),  # ✅ Audio support
    ('video', 'Video'),
    ('document', 'Document'),
    # ...
]
```

### WhatsApp Server (WPPConnect)
The server automatically:
1. Receives audio files from WhatsApp
2. Decrypts the audio data
3. Saves to `/uploads/` directory
4. Sends metadata to Django webhook

### Frontend Display
Audio messages appear with:
- 🎤 Microphone icon
- HTML5 audio player with controls
- Play/pause functionality
- Seek bar
- Volume control

## 📱 User Interface

### Agent Conversation View (`/agent/conversations/`)
```html
<!-- Audio Message Display -->
<div class="message-audio">
    <div class="audio-icon">
        <i class="fas fa-microphone"></i>
    </div>
    <div class="audio-player">
        <audio controls>
            <source src="/uploads/audio_file.ogg" type="audio/ogg">
        </audio>
    </div>
</div>
```

### Admin Monitor View (`/admin/monitor-agent/`)
Same audio player interface for monitoring agent conversations.

## 🚀 How It Works

### Receiving Audio Messages

1. **Customer sends voice note** on WhatsApp
2. **WPPConnect receives** the message
3. **Server processes**:
   ```javascript
   if (message.type === 'audio') {
       const buffer = await client.decryptFile(message);
       const fileName = `${timestamp}_audio.ogg`;
       fs.writeFileSync(`uploads/${fileName}`, buffer);
   }
   ```
4. **Webhook sends** to Django:
   ```json
   {
       "message_type": "audio",
       "media_url": "/uploads/1234567890_audio.ogg",
       "mime_type": "audio/ogg"
   }
   ```
5. **Django saves** message to database
6. **Frontend displays** audio player

## 🧪 Testing

### Test Script
Run the test script to create sample audio messages:
```bash
cd "New folder"
python test_audio_whatsapp.py
```

### Manual Testing
1. Send a voice note to the WhatsApp number
2. Open agent conversation interface
3. Select the customer
4. Verify audio player appears
5. Test playback

## 🎨 Styling

### CSS Classes
- `.message-audio` - Container for audio message
- `.audio-icon` - Microphone icon
- `.audio-player` - Audio controls wrapper

### Customization
Audio player uses native HTML5 controls which adapt to:
- Browser theme
- RTL/LTR direction
- Mobile/desktop view

## 🔍 Troubleshooting

### Audio Not Playing
1. **Check file exists**: Verify file in `/wppconnect-server/uploads/`
2. **Check MIME type**: Ensure correct `mime_type` in database
3. **Check proxy**: Verify Django proxy serves `/uploads/` files
4. **Browser support**: Test in Chrome/Firefox/Safari

### Audio Not Receiving
1. **Check WPPConnect**: Ensure connected to WhatsApp
2. **Check webhook**: Verify Django webhook receives data
3. **Check logs**: Review server.js console output
4. **File permissions**: Ensure uploads folder is writable

## 📊 Database Query Examples

### Find All Audio Messages
```python
from conversations.models import Message

audio_messages = Message.objects.filter(message_type='audio')
print(f"Total audio messages: {audio_messages.count()}")
```

### Get Audio Messages for Customer
```python
customer = Customer.objects.get(phone_number='201234567890')
tickets = Ticket.objects.filter(customer=customer)
audio_msgs = Message.objects.filter(
    ticket__in=tickets,
    message_type='audio'
)
```

## 🔐 Security Considerations

1. **File Validation**: Only accept audio MIME types
2. **Size Limits**: Implement max file size (e.g., 16MB)
3. **Access Control**: Proxy ensures authenticated access
4. **Storage**: Consider cloud storage for production

## 📈 Future Enhancements

- [ ] Audio transcription (speech-to-text)
- [ ] Waveform visualization
- [ ] Audio message recording from agent side
- [ ] Compressed storage format
- [ ] CDN integration for faster delivery

## 📝 Notes

- WhatsApp voice notes are typically in OGG format with Opus codec
- Maximum WhatsApp audio duration: 15 minutes
- Files are stored locally in development, consider S3/cloud for production
- Audio players are responsive and work on mobile devices

---

**Last Updated:** November 2025  
**Version:** 1.0.0  
**Author:** Khalifa Pharmacy Development Team