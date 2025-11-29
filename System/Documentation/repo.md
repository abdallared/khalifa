# 🏥 Khalifa Pharmacy WhatsApp Management System

## 📋 Project Overview

**Project Name:** WhatsApp Conversation Management System  
**Company:** Khalifa Pharmacies - Mansoura, Egypt  
**Branches:** 15 locations  
**Status:** 90% Complete  
**Last Updated:** November 2025

### Problem Statement
- 15 employees from different branches using the same WhatsApp number
- WhatsApp blocking accounts due to suspicious activity patterns
- Loss of customer communication channels

### Solution
A unified system for managing all WhatsApp conversations with:
- ✅ Centralized conversation management
- ✅ Automatic distribution to agents
- ✅ Performance monitoring and KPIs
- ✅ Complete activity tracking

---

## 🏗️ Repository Structure

```
khalifa/
├── New folder/                    # Main Django Project
│   ├── khalifa_pharmacy/          # Django settings & configuration
│   ├── conversations/             # Core application
│   │   ├── models.py             # 22 Database models
│   │   ├── serializers.py        # 22 DRF serializers
│   │   ├── views.py              # API views
│   │   ├── views_frontend.py    # Frontend views
│   │   ├── views_whatsapp.py    # WhatsApp integration views
│   │   ├── views_analytics.py   # Analytics views
│   │   ├── views_messages.py    # Message handling views
│   │   ├── views_notifications.py # Notification views
│   │   ├── whatsapp_driver.py   # WhatsApp driver pattern
│   │   ├── message_queue.py     # Message queue handling
│   │   ├── authentication.py    # Custom authentication
│   │   ├── permissions.py        # Permission classes
│   │   ├── middleware.py         # Custom middleware
│   │   ├── signals.py           # Django signals
│   │   └── utils.py             # Utility functions
│   ├── templates/                # HTML templates
│   │   ├── admin/               # Admin interface (7 pages)
│   │   └── agent/               # Agent interface (3 pages)
│   ├── static/                   # Static files (CSS/JS/Images)
│   ├── Documentation/            # Project documentation
│   │   ├── EXECUTIVE_SUMMARY.md
│   │   ├── WPPCONNECT_SETUP_GUIDE.md
│   │   ├── USER_GUIDE.md
│   │   └── PROJECT_COMPLETE_SUMMARY.md
│   ├── manage.py                # Django management script
│   ├── requirements.txt         # Python dependencies
│   ├── README.md               # Project readme
│   └── db.sqlite3              # SQLite database
│
├── wppconnect-server/           # WhatsApp Integration Server
│   ├── server.js               # Main server file
│   ├── package.json            # Node.js dependencies
│   ├── .env                    # Environment variables
│   └── README.md              # Server documentation
│
├── Khalifa_React_S03/          # React frontend (future)
│   └── whatsapp_system/
│
├── .env                        # Root environment variables
├── dev.bat                     # Development startup script
├── run.bat                     # Production startup script
└── stop.bat                    # Stop all services script
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Database:** SQLite (Production-ready for PostgreSQL)
- **Language:** Python 3.11+
- **Authentication:** Custom token-based auth

### WhatsApp Integration
- **Server:** Node.js with WPPConnect
- **Protocol:** WebSocket & REST API
- **Pattern:** Driver Pattern for abstraction
- **Dependencies:**
  - @wppconnect-team/wppconnect: ^1.30.0
  - express: ^4.18.2
  - axios: ^1.6.0

### Frontend (Current)
- **Framework:** Server-side rendered Django templates
- **UI:** Bootstrap 5 RTL
- **JavaScript:** Vanilla JS with AJAX
- **Icons:** Font Awesome 6
- **Font:** Cairo (Arabic support)

---

## 📊 Database Schema

### Models Overview (22 Tables)

#### User Management (3 models)
- **User**: System users (Admin/Agent)
- **Agent**: Agent-specific data and capacity
- **Admin**: Admin-specific permissions

#### Customer & Contact (3 models)
- **Customer**: Customer profiles
- **CustomerTag**: Customer categorization
- **CustomerNote**: Customer interaction notes

#### Ticket Management (3 models)
- **Ticket**: Conversation tickets
- **TicketTransferLog**: Transfer history
- **TicketStateLog**: State change tracking

#### Messages (3 models)
- **Message**: WhatsApp messages
- **MessageDeliveryLog**: Delivery status tracking
- **MessageSearchIndex**: Full-text search index

#### Templates (3 models)
- **GlobalTemplate**: Company-wide templates
- **AgentTemplate**: Personal agent templates
- **AutoReplyTrigger**: Automated responses

#### Performance Tracking (5 models)
- **ResponseTimeTracking**: Response time metrics
- **AgentDelayEvent**: Delay tracking
- **AgentKPI**: Daily KPI metrics
- **AgentKPIMonthly**: Monthly aggregates
- **CustomerSatisfaction**: Satisfaction scores

#### System (2 models)
- **ActivityLog**: Audit trail
- **LoginAttempt**: Security tracking

---

## 🔌 API Endpoints

### Overview
- **Total Endpoints:** 50+
- **Authentication:** Token-based
- **Format:** RESTful JSON API
- **Rate Limiting:** Implemented

### Main Endpoint Categories

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Current user info

#### Tickets
- `GET /api/tickets/` - List tickets
- `POST /api/tickets/` - Create ticket
- `GET /api/tickets/{id}/` - Ticket details
- `PUT /api/tickets/{id}/` - Update ticket
- `POST /api/tickets/{id}/transfer/` - Transfer ticket

#### Messages
- `GET /api/messages/` - List messages
- `POST /api/messages/` - Send message
- `GET /api/messages/unread/` - Unread messages
- `POST /api/messages/mark-read/` - Mark as read

#### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/` - Customer details
- `GET /api/customers/{id}/history/` - Customer history

#### Analytics
- `GET /api/analytics/dashboard/` - Dashboard stats
- `GET /api/analytics/agent-kpis/` - Agent KPIs
- `GET /api/analytics/reports/` - Generate reports

#### WhatsApp
- `POST /api/whatsapp/webhook/` - Incoming messages
- `POST /api/whatsapp/send/` - Send message
- `GET /api/whatsapp/status/` - Connection status
- `GET /api/whatsapp/qr-code/` - Get QR code

---

## ✨ Key Features

### 1. Conversation Management
- 📱 Automatic WhatsApp message reception
- 🔄 Least Loaded distribution algorithm
- 💬 WhatsApp Web-like interface
- 📝 Quick reply templates
- ⏱️ Real-time updates (5-second intervals)
- ✓✓ Delivery status tracking

### 2. Agent Management
- 👥 CRUD operations for agents
- 📊 Capacity management
- 🔄 Online/offline status
- 📈 Performance tracking
- 🎯 Automatic KPI calculation

### 3. Customer Management
- ➕ Automatic customer creation
- 📜 Complete conversation history
- 🏷️ Tagging system
- 🔍 Advanced search
- 📝 Notes and annotations

### 4. Analytics & Reporting
- 📊 Comprehensive dashboard
- 📈 Agent KPIs and metrics
- 📅 Daily/weekly/monthly reports
- 📥 Excel export functionality
- 📊 Real-time statistics

### 5. Security & Permissions
- 👨‍💼 Role-based access (Admin/Agent)
- 🔒 Rate limiting protection
- 📝 Complete audit logging
- 🔐 Brute force protection
- 🛡️ Token-based authentication

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 14+
- Redis (optional, for caching)

### Quick Start

#### 1. Backend Setup
```bash
cd "New folder"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 2. WhatsApp Server Setup
```bash
cd wppconnect-server
npm install
cp .env.example .env
# Edit .env file with your settings
npm start
```

#### 3. Access the System
- URL: `http://localhost:8000/login/`
- Admin: `admin` / `admin123`
- Agent: `agent1` / `agent123`

### Using Batch Scripts (Windows)
```bash
# Development mode
dev.bat

# Production mode
run.bat

# Stop all services
stop.bat
```

---

## 📈 Project Status

### Completed (90%)
- ✅ **Backend:** 100% complete
- ✅ **Database:** 22 models implemented
- ✅ **API:** 50+ endpoints ready
- ✅ **Tests:** 25/25 passing
- ✅ **Frontend:** 10 pages (Django templates)
- ✅ **WhatsApp:** WPPConnect integration
- ✅ **Documentation:** Comprehensive guides

### Pending (10%)
- ⏳ Cloud API integration
- ⏳ WebSocket real-time updates
- ⏳ React frontend migration
- ⏳ Advanced analytics dashboard

---

## 📊 Statistics

```
📝 Lines of Code: 4000+
📁 Files: 40+ Python files
🗄️ Database Models: 22
🔗 Foreign Keys: 34
🔌 API Endpoints: 50+
🧪 Test Cases: 25
📄 HTML Pages: 10
📚 Documentation: 4 comprehensive guides
```

---

## 🔒 Security Features

- Token-based authentication
- Rate limiting on all endpoints
- Brute force protection
- Complete audit logging
- Input validation and sanitization
- CORS configuration
- Environment variable management

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [EXECUTIVE_SUMMARY.md](New%20folder/Documentation/EXECUTIVE_SUMMARY.md) | Executive overview for stakeholders |
| [WPPCONNECT_SETUP_GUIDE.md](New%20folder/Documentation/WPPCONNECT_SETUP_GUIDE.md) | WhatsApp server setup guide |
| [USER_GUIDE.md](New%20folder/Documentation/USER_GUIDE.md) | End-user manual |
| [PROJECT_COMPLETE_SUMMARY.md](New%20folder/Documentation/PROJECT_COMPLETE_SUMMARY.md) | Technical project summary |

---

## 🎯 Use Cases

1. **Multi-branch Customer Service**
   - Centralized WhatsApp number for all branches
   - Automatic distribution to available agents
   - Consistent customer experience

2. **Performance Management**
   - Real-time KPI tracking
   - Response time monitoring
   - Customer satisfaction metrics

3. **Compliance & Audit**
   - Complete message history
   - Activity logging
   - Transfer tracking

---

## 🚦 Roadmap

### Phase 1: Core System ✅
- Basic conversation management
- Agent assignment
- Message handling

### Phase 2: Advanced Features ✅
- Templates system
- KPI tracking
- Analytics dashboard

### Phase 3: Integration ✅
- WPPConnect integration
- Webhook handling
- Real-time updates

### Phase 4: UI/UX ✅
- Admin interface
- Agent interface
- Mobile responsive

### Phase 5: Cloud & Scale ⏳
- Cloud API migration
- Horizontal scaling
- Advanced analytics

---

## 👥 Team & Support

**Development:** Augment AI Agent  
**Date:** October-November 2025  
**Version:** 1.0.0  
**License:** Proprietary - Khalifa Pharmacies

---

## 🔧 Maintenance

### Daily Tasks
- Monitor WhatsApp connection status
- Check error logs
- Review agent performance

### Weekly Tasks
- Generate performance reports
- Review customer satisfaction
- Update templates

### Monthly Tasks
- Database optimization
- Security audit
- Backup verification

---

## 📞 Contact & Support

For technical support or questions about this system, please refer to the documentation or contact the development team.

---

**© 2025 Khalifa Pharmacies - Mansoura, Egypt**