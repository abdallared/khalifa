📊 Khalifa Pharmacy WhatsApp Management System - Architecture Overview
System Overview
This is a WhatsApp Conversation Management System for Khalifa Pharmacies with 15 branches in Mansoura, Egypt.

Core Problem Solved:

Multiple employees (1 per branch) using the same WhatsApp number
WhatsApp blocking accounts due to suspicious activity
Solution: Centralized system to manage conversations with automatic distribution to agents


1. System Architecture Diagram

┌─────────────────────────────────────────────────────────────────┐
│                         KHALIFA PHARMACY SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────┐
                    │   WhatsApp Web Client    │
                    │   (wppconnect driver)    │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   WPPConnect Server       │
                    │   (Node.js + Express)    │
                    │   Port: 3000             │
                    │   - Message Handling     │
                    │   - QR Code Generation   │
                    │   - WebSocket Events     │
                    └────────────┬──────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Django Backend   │  │ Frontend (React) │  │ Admin Dashboard  │
│ (Python)         │  │ (Vite)           │  │ (Django Admin)   │
│ Port: 8000       │  │ Port: 5173       │  │ Port: 8000       │
│                  │  │                  │  │                  │
│ API Endpoints    │  │ Components:      │  │ Features:        │
│ - Tickets        │  │ - ChatList       │  │ - Tickets        │
│ - Messages       │  │ - ChatWindow     │  │ - Agents         │
│ - Customers      │  │ - MessageInput   │  │ - Analytics      │
│ - Agents         │  │ - QRDisplay      │  │ - Settings       │
│ - Analytics      │  │ - Real-time      │  │                  │
│ - KPI            │  │   Updates        │  │                  │
└──────┬───────────┘  └────────┬─────────┘  └──────────────────┘
       │                       │
       └───────────┬───────────┘
                   │
        ┌──────────▼──────────┐
        │  SQLite Database    │
        │ (db.sqlite3)        │
        │                     │
        │ Tables:             │
        │ - Users/Agents      │
        │ - Customers         │
        │ - Messages          │
        │ - Tickets           │
        │ - KPI Metrics       │
        │ - Activity Logs     │
        └─────────────────────┘




2. Data Model Diagram

┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE SCHEMA                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│    User      │          │   Agent      │          │   Admin      │
├──────────────┤          ├──────────────┤          ├──────────────┤
│ id (PK)      │          │ id (PK)      │          │ id (PK)      │
│ username     │          │ user_id (FK) │          │ user_id (FK) │
│ email        │          │ branch       │          │ department   │
│ password     │          │ is_online    │          │ permissions  │
│ is_staff     │          │ response_time│          │ created_at   │
│ is_superuser │          │ rating       │          └──────────────┘
│ created_at   │          └──────────────┘
└──────┬───────┘                 │
       │                         │
       │                         │ (1)
       │                    ┌────▼──────────┐
       │                    │   Ticket      │
       │                    ├───────────────┤
       │                    │ id (PK)       │
       │                    │ customer_id   │
       │                    │ agent_id (FK) │
       │                    │ status        │
       │                    │ priority      │
       │                    │ created_at    │
       │                    │ closed_at     │
       │                    └────┬──────────┘
       │                         │ (1)
       │                    ┌────▼──────────┐      ┌──────────────┐
       │                    │   Message     │◄─────┤ Customer     │
       │                    ├───────────────┤      ├──────────────┤
       │                    │ id (PK)       │      │ id (PK)      │
       │                    │ ticket_id(FK) │      │ phone        │
       │                    │ sender        │      │ name         │
       │                    │ content       │      │ email        │
       │                    │ message_type  │      │ tags         │
       │                    │ created_at    │      │ satisfaction │
       │                    │ status        │      │ source       │
       │                    └───────────────┘      └──────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   CustomerNote   │      │ CustomerTag      │      │  MessageSearchIdx │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│ id               │      │ id               │      │ id               │
│ customer_id(FK)  │      │ customer_id (FK) │      │ message_id (FK)  │
│ agent_id         │      │ tag_name         │      │ search_text      │
│ note_content     │      │ created_at       │      └──────────────────┘
│ created_at       │      └──────────────────┘

┌──────────────────┐      ┌──────────────────┐
│    AgentKPI      │      │  ActivityLog     │
├──────────────────┤      ├──────────────────┤
│ id               │      │ id               │
│ agent_id (FK)    │      │ user_id          │
│ messages_sent    │      │ action           │
│ response_time    │      │ timestamp        │
│ satisfaction     │      │ details          │
│ created_at       │      └──────────────────┘
└──────────────────┘





3. Complete Application Flow Sequence


┌─────────────────────────────────────────────────────────────────┐
│                    USER WORKFLOW SEQUENCE                        │
└─────────────────────────────────────────────────────────────────┘

STEP 1: SYSTEM INITIALIZATION
═══════════════════════════════════════════════════════════════════

1️⃣  User starts Django Backend
   └─► python manage.py runserver
   └─► Connects to SQLite Database
   └─► Loads all configurations from settings.py

2️⃣  WPPConnect Server (Node.js) starts
   └─► npm start in wppconnect-server/
   └─► Listens on Port 3000
   └─► Ready for WhatsApp Web connection

3️⃣  Frontend (React + Vite) starts
   └─► npm run dev in frontend/
   └─► Vite dev server on Port 5173
   └─► Ready to serve UI


STEP 2: QR CODE AUTHENTICATION
═══════════════════════════════════════════════════════════════════

1️⃣  User opens http://localhost:5173
   └─► Frontend requests QR Code from WPPConnect Server
   └─► Backend: GET /api/qr-code

2️⃣  WPPConnect Server generates QR Code
   └─► Uses Puppeteer to launch WhatsApp Web
   └─► Generates QR code image
   └─► Returns QR to Frontend

3️⃣  User scans QR Code with WhatsApp on Phone
   └─► WhatsApp Web authenticates
   └─► Session established with WhatsApp servers
   └─► WebSocket connection established


STEP 3: MESSAGE RECEPTION & PROCESSING
═══════════════════════════════════════════════════════════════════

        WhatsApp Phone              WhatsApp Web (Server)      Django Backend
               │                              │                        │
               │ (1) New Message              │                        │
               ├─────────────────────────────►│                        │
               │                              │ (2) Parse Message      │
               │                              │ (using wppconnect)     │
               │                              │                        │
               │                              │ (3) Send to Backend    │
               │                              ├───────────────────────►│
               │                              │  /api/messages/receive │
               │                              │                        │
               │                              │ (4) Create Ticket      │
               │                              │     (if new customer)  │
               │                              │  Create Message        │
               │                              │  Assign to Agent       │
               │                              │◄───────────────────────┤
               │                              │                        │
               │                              │ (5) Notify Agent       │
               │                              │     (WebSocket)        │
               │                              │ (6) Update UI          │
               │◄─────────────────────────────┤ (Real-time update)    │


STEP 4: AGENT HANDLING & MESSAGE SENDING
═══════════════════════════════════════════════════════════════════

        Frontend (React)           Django Backend          WPPConnect Server
               │                         │                         │
    Agent sees ticket         (1) Agent opens ticket         │
    and reads message              │                         │
               │                   │                         │
    (2) Agent types reply          │                         │
               │                   │                         │
    (3) Send button clicked        │                         │
    ├────────────────────────────►│                         │
    │   POST /api/messages/send   │                         │
    │                              │ (4) Create Message     │
    │                              │     record in DB       │
    │                              │                         │
    │                              │ (5) Extract WhatsApp   │
    │                              │     message details    │
    │                              │                         │
    │                              ├────────────────────────►│
    │                              │  Send message via API  │
    │                              │                         │
    │                              │ (6) WhatsApp sends     │
    │                              │     message to customer│
    │                              │◄────────────────────────┤
    │                              │ Message Status: SENT   │
    │                              │                         │
    │◄────────────────────────────┤                         │
    │  Message Confirmed           │                         │
    │  Update UI to show "Sent"    │                         │


STEP 5: TICKET LIFECYCLE
═══════════════════════════════════════════════════════════════════

NEW TICKET CREATED
   │
   ├─► Customer opens conversation
   ├─► System creates Ticket (Status: OPEN)
   ├─► System creates Customer record (if new)
   └─► Agent assigned automatically

AGENT RESPONDING
   │
   ├─► Agent reads customer message
   ├─► Ticket stays OPEN
   ├─► Agent sends response
   └─► Message logged in Message table

TICKET CLOSURE
   │
   ├─► Option 1: Agent closes ticket manually
   ├─► Option 2: Admin closes from admin panel
   ├─► Option 3: Auto-close after X days of inactivity
   └─► Ticket Status → CLOSED


STEP 6: ADMIN MONITORING & ANALYTICS
═══════════════════════════════════════════════════════════════════

Admin Dashboard (http://localhost:8000/admin/)
│
├─► View All Tickets
│   └─► See agents handling each ticket
│   └─► See customer satisfaction rating
│   └─► See response times
│
├─► View All Agents
│   └─► KPI metrics per agent
│   └─► Monthly performance tracking
│   └─► Average response time
│   └─► Customer satisfaction score
│
├─► Analytics & Reports
│   └─► Total messages sent/received
│   └─► Average response time
│   └─► Ticket resolution rate
│   └─► Customer satisfaction trends
│
└─► Activity Logs
    └─► Track all user actions
    └─► Login attempts
    └─► Ticket transfers
    └─► Status changes



4. Frontend Component Architecture


┌──────────────────────────────────────────────────────────────┐
│                        App.jsx (Main)                        │
│  - State management with React hooks                         │
│  - Socket.io connection setup                                │
│  - Real-time updates subscription                            │
└────────────────┬─────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ┌────────────┐   ┌──────────────┐
    │  Header    │   │   ChatList   │
    │            │   │              │
    │ - Logo     │   │ - Search bar  │
    │ - User     │   │ - Customers  │
    │   Info     │   │   list (Live) │
    │ - Logout   │   │ - Unread     │
    │            │   │   counter    │
    └────────────┘   │ - Sort by    │
                     │   recent     │
                     └────┬─────────┘
                          │
                          │ (Selected Customer)
                          ▼
                  ┌──────────────────┐
                  │  ChatWindow      │
                  │                  │
                  │ ┌──────────────┐ │
                  │ │ Messages List│ │
                  │ │              │ │
                  │ │ ┌──────────┐ │ │
                  │ │ │ Message  │ │ │
                  │ │ │ Bubble   │ │ │
                  │ │ │ - Text   │ │ │
                  │ │ │ - Images │ │ │
                  │ │ │ - Audio  │ │ │
                  │ │ │ - Status │ │ │
                  │ │ └──────────┘ │ │
                  │ └──────────────┘ │
                  │                  │
                  │ ┌──────────────┐ │
                  │ │MessageInput  │ │
                  │ │              │ │
                  │ │ - Text input │ │
                  │ │ - Emoji      │ │
                  │ │ - File upload│ │
                  │ │ - Send btn   │ │
                  │ └──────────────┘ │
                  └──────────────────┘

Real-time Updates (Socket.io):
├─► 'newMessage' → Update ChatWindow
├─► 'messageDelivered' → Update status
├─► 'messageRead' → Update status
├─► 'userOnline' → Update user status
├─► 'newCustomer' → Add to ChatList
└─► 'ticketAssigned' → Notify agent






5. API Endpoints Map

AUTHENTICATION
├─ POST   /auth/login
├─ POST   /auth/logout
├─ POST   /auth/register (Admin only)
└─ GET    /auth/profile

TICKETS
├─ GET    /api/tickets/
├─ GET    /api/tickets/<id>/
├─ POST   /api/tickets/
├─ PATCH  /api/tickets/<id>/
├─ DELETE /api/tickets/<id>/
├─ POST   /api/tickets/<id>/close/
├─ POST   /api/tickets/<id>/transfer/
└─ POST   /api/tickets/<id>/notes/

MESSAGES
├─ GET    /api/messages/
├─ GET    /api/messages/<id>/
├─ POST   /api/messages/send/
├─ POST   /api/messages/receive/
├─ DELETE /api/messages/<id>/
└─ GET    /api/messages/search/

CUSTOMERS
├─ GET    /api/customers/
├─ GET    /api/customers/<id>/
├─ POST   /api/customers/
├─ PATCH  /api/customers/<id>/
├─ POST   /api/customers/<id>/notes/
├─ POST   /api/customers/<id>/tags/
└─ GET    /api/customers/<id>/history/

AGENTS
├─ GET    /api/agents/
├─ GET    /api/agents/<id>/
├─ GET    /api/agents/<id>/kpi/
└─ POST   /api/agents/<id>/status/

ANALYTICS
├─ GET    /api/analytics/dashboard/
├─ GET    /api/analytics/kpi/
├─ GET    /api/analytics/agents/
├─ GET    /api/analytics/customers/
└─ GET    /api/analytics/reports/

WHATSAPP
├─ GET    /api/whatsapp/qr-code/
├─ GET    /api/whatsapp/status/
└─ POST   /api/whatsapp/disconnect/




6. Project Directory Structure

khalifa/
├── System/                          # Django Backend
│   ├── conversations/               # Main Django App
│   │   ├── migrations/              # Database migrations
│   │   ├── management/              # Custom commands
│   │   ├── models.py               # Data Models (18 models)
│   │   ├── serializers.py          # API Serializers
│   │   ├── views.py                # Main Views (37 KB)
│   │   ├── views_messages.py       # Message Endpoints
│   │   ├── views_whatsapp.py       # WhatsApp Integration
│   │   ├── views_analytics.py      # Analytics Endpoints
│   │   ├── views_frontend.py       # Frontend Support
│   │   ├── views_notifications.py  # Notifications
│   │   ├── admin.py                # Django Admin Config
│   │   ├── permissions.py          # Custom Permissions
│   │   ├── message_queue.py        # Message Queue Handler
│   │   ├── utils.py                # Utility Functions
│   │   ├── whatsapp_driver.py      # WhatsApp API Driver
│   │   ├── middleware.py           # Custom Middleware
│   │   ├── signals.py              # Django Signals
│   │   ├── urls.py                 # URL Routing
│   │   └── authentication.py       # Auth Logic
│   │
│   ├── khalifa_pharmacy/            # Django Project Settings
│   │   ├── settings.py              # Django Configuration
│   │   ├── urls.py                  # Main URL Router
│   │   ├── urls_frontend.py         # Frontend URLs
│   │   ├── wsgi.py                  # WSGI Config
│   │   └── asgi.py                  # ASGI Config
│   │
│   ├── templates/                   # HTML Templates
│   │   ├── base.html
│   │   ├── login.html
│   │   └── admin/
│   │
│   ├── static/                      # Static Files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── media/                       # Uploaded Media
│   │   └── messages/
│   │
│   ├── logs/                        # Application Logs
│   │   └── django.log
│   │
│   ├── db.sqlite3                   # SQLite Database
│   ├── manage.py                    # Django Management
│   ├── requirements.txt             # Python Dependencies
│   ├── README.md
│   └── QUICK_START.md
│
├── wppconnect-server/               # WhatsApp Web Server (Node.js)
│   ├── server.js                    # Main Express Server
│   ├── tokens/                      # WhatsApp Session Tokens
│   ├── uploads/                     # Received Media Files
│   ├── node_modules/                # Dependencies
│   ├── package.json
│   ├── .env
│   └── README.md
│
├── Khalifa_React_S03/
│   └── whatsapp_system/
│       ├── frontend/                # React Frontend
│       │   ├── src/
│       │   │   ├── components/
│       │   │   │   ├── App.jsx              # Main Component
│       │   │   │   ├── Header.jsx           # Top Navigation
│       │   │   │   ├── ChatList.jsx         # Conversations List
│       │   │   │   ├── ChatWindow.jsx       # Chat Display
│       │   │   │   ├── MessageBubble.jsx    # Message Component
│       │   │   │   ├── MessageInput.jsx     # Message Composer
│       │   │   │   └── QRCodeDisplay.jsx    # QR Code Scanner
│       │   │   ├── index.css                # Global Styles
│       │   │   └── main.jsx
│       │   ├── vite.config.js               # Vite Configuration
│       │   ├── tailwind.config.js           # Tailwind Config
│       │   ├── package.json
│       │   └── index.html
│       │
│       └── backend/                  # (Old Backend - Reference Only)
│
├── Documentation/                   # Comprehensive Docs
│   ├── MASTER_CONTEXT.md            # Complete Project Doc
│   ├── DRIVER_PATTERN.md            # Architecture Pattern
│   ├── KPI_CALCULATION_GUIDE.md
│   ├── COMPLETE_FLOW_TEST_REPORT.md
│   └── [25+ other documents]
│
├── run.bat                          # Start All Services (Windows)
├── stop.bat                         # Stop All Services (Windows)
├── dev.bat                          # Start Dev Mode (Windows)
├── Instructions.txt                 # Current Task Instructions
└── repo.md                          # Repository Documentation





7. Message Flow - Detailed Sequence

┌─────────────────────────────────────────────────────────────────┐
│            COMPLETE MESSAGE LIFECYCLE (End-to-End)              │
└─────────────────────────────────────────────────────────────────┘

[INCOMING MESSAGE FLOW]
═══════════════════════════════════════════════════════════════════

Customer sends message on WhatsApp
          │
          ▼
   WhatsApp Web (Puppeteer)
          │
          ▼
   WPPConnect Server (Node.js:3000)
          │ (parses message)
          ▼
   POST /api/messages/receive/
          │
          ▼
   Django Backend (Messages View)
          │
          ├─► Check if customer exists
          │   └─► If NO: Create new customer
          │
          ├─► Check if ticket exists
          │   └─► If NO: Create new ticket
          │
          ├─► Create Message record in DB
          │
          ├─► Get assigned agent
          │
          ├─► Update Message status to RECEIVED
          │
          ├─► Log activity in ActivityLog
          │
          ├─► Calculate KPI metrics
          │
          └─► Emit WebSocket event: 'newMessage'
                    │
                    ▼
              Frontend (React)
                    │
                    ├─► Update ChatList (show latest message)
                    ├─► Update ChatWindow (display message)
                    ├─► Play notification sound
                    ├─► Show unread badge
                    └─► Scroll to latest message


[OUTGOING MESSAGE FLOW]
═══════════════════════════════════════════════════════════════════

Agent types message in UI
          │
          ▼
   User clicks "Send"
          │
          ▼
   Frontend sends: POST /api/messages/send/
   {
     "ticket_id": 123,
     "content": "Hello customer!",
     "message_type": "text"
   }
          │
          ▼
   Django Backend (Send Message View)
          │
          ├─► Validate request
          ├─► Verify agent has access to ticket
          │
          ├─► Create Message record in DB
          │   └─► Status: PENDING
          │   └─► Sender: Agent
          │   └─► Timestamp: now()
          │
          ├─► Extract customer phone from Ticket
          │
          ├─► Call WPPConnect API
          │   POST http://localhost:3000/message/send
          │   {
          │     "phone": "+20xxxxxxxxxx",
          │     "message": "Hello customer!",
          │     "type": "text"
          │   }
          │
          ▼
   WPPConnect Server (Node.js)
          │
          ├─► Validate phone format
          ├─► Get WhatsApp Web session
          ├─► Send message via WhatsApp Web
          │
          ▼
   WhatsApp Servers (Send)
          │
          ├─► Message status → SENT ✓
          └─► Emit webhook callback
                    │
                    ▼
          WPPConnect receives callback
                    │
                    ▼
          POST http://Django/api/messages/<id>/status/
          {"status": "sent"}
                    │
                    ▼
          Update Message.status = SENT
          Emit WebSocket: 'messageSent'
                    │
                    ▼
          Frontend receives event
          Update UI: Show ✓ (sent icon)


[MESSAGE DELIVERY FLOW]
═══════════════════════════════════════════════════════════════════

WhatsApp Server → Customer phone
          │
          ├─► Message delivered to phone
          │
          ├─► Send delivery callback to WPPConnect
          │
          ▼
WPPConnect receives callback
          │
          ▼
POST http://Django/api/messages/<id>/status/
{"status": "delivered"}
          │
          ▼
Update Message.status = DELIVERED
Update MessageDeliveryLog
Emit WebSocket: 'messageDelivered'
          │
          ▼
Frontend updates: Show ✓✓ (double check)


[MESSAGE READ FLOW]
═══════════════════════════════════════════════════════════════════

Customer reads message on phone
          │
          ▼
WhatsApp detects read receipt
          │
          ▼
Send read callback to WPPConnect
          │
          ▼
POST http://Django/api/messages/<id>/status/
{"status": "read"}
          │
          ▼
Update Message.status = READ
Update MessageDeliveryLog
Update ResponseTimeTracking (calculate response time)
Emit WebSocket: 'messageRead'
          │
          ▼
Frontend updates: Show ✓✓ (blue double check)
Update Agent KPI: 'response_time'




8. Key Technologies Stack
| Layer | Technology | Purpose | |-------|-----------|---------| | Frontend | React 18 | UI Framework | | | Vite | Build Tool | | | Tailwind CSS | Styling | | | Socket.io Client | Real-time | | | Axios | HTTP Requests | | | Lucide React | Icons | | Backend | Django 4.2 | Web Framework | | | Django REST Framework | API | | | SQLite | Database | | | Python 3.11+ | Runtime | | WhatsApp | WPPConnect | WhatsApp Web API | | | Puppeteer | Browser Automation | | | Node.js 14+ | Runtime | | | Express | Web Server | | Real-time | Socket.io | WebSocket Server | | | WebSocket Protocol | Communication |






9. Data Models Overview (18 Total)

1. User              - Base user for auth
2. Agent            - Employees handling tickets
3. Admin            - Administrative users
4. Customer         - Customer contact info
5. CustomerTag      - Customer categorization
6. CustomerNote     - Internal notes
7. Ticket           - Support tickets
8. TicketTransferLog - Track ticket transfers
9. TicketStateLog   - Track ticket status
10. Message         - All messages (sent/received)
11. MessageDeliveryLog - Delivery tracking
12. MessageSearchIndex - Search optimization
13. GlobalTemplate  - System templates
14. AgentTemplate   - Agent-specific templates
15. AutoReplyTrigger - Auto-reply rules
16. ResponseTimeTracking - Response metrics
17. AgentDelayEvent - Track delays
18. AgentKPI        - Performance metrics
19. AgentKPIMonthly - Monthly reports
20. CustomerSatisfaction - Ratings
21. ActivityLog     - Audit trail
22. LoginAttempt    - Login tracking
