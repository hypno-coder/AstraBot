# TECHNICAL SPECIFICATION AND AI AGENT GUIDELINES (TECH_SPEC)

**CRITICAL FOR AI AGENTS:** This document is the absolute and inviolable standard for this project. Any deviation from the tech stack, abstraction layers, or code style rules is STRICTLY PROHIBITED without explicit direct instruction from the user. 

## 0. CORE PROJECT & BUSINESS LOGIC
CORE PROJECT & BUSINESS LOGIC

### 0.1. Elevator Pitch
The bot provides personalized esoteric calculations (money calendars, horoscopes, compatibility) based on user-provided data.

### 0.2. DATABASE ENTITIES & RELATIONSHIPS
The AI Agent must implement the following schema using SQLAlchemy 2.0 with strict typing.
#### 0.2.1. User Entity
Stores profile data, split into automated and manual collection phases.
* **Primary (Automated):**
    * `id`: BigInteger (Telegram ID), Primary Key.
    * `username`: String, Nullable.
    * `is_admin`: Boolean (default: False).
    * `is_active`: Boolean (default: True, tracks bot block status).
    * `is_tele_prem`: Boolean (Telegram Premium status).
    * `status`: Enum ("free", "premium").
    * `reg_date`: DateTime.
    * `last_visit_date`: DateTime.
    * `referred_by`: BigInteger (Foreign Key to User.id).
    * `language_code`: String (default: "ru")
* **Secondary (Manual Input):**
    * `fio`: String (Full Name).
    * `gender`: Enum (MALE, FEMALE, UNKNOWN).
    * `birth_city`: String.
    * `birthday`: Date.    
    * `birth_time`: Time    
    * `birth_lat`: Float    
    * `birth_lon`: Float
    * `timezone`: String (e.g., "Europe/Moscow").
####  0.2.2. Product Entity (The Catalog)
Represents esoteric services available for purchase.
* `id`: Integer, Primary Key.
* `title`: String (Service name).
* `description`: Text.
* `content_type`: Enum (TEXT, FILE).
* `content_data`: Text (Stores the actual text or Telegram `file_id` for caching).
####  0.2.3. Purchase Entity (Transaction Log)
Links Users and Products (One-to-Many relationship).
* `id`: Integer, Primary Key.
* `user_id`: BigInteger (Foreign Key to User.id).
* `product_id`: Integer (Foreign Key to Product.id).
* `purchase_date`: DateTime (default: now).
####  0.2.4. PromoCode Entity
* `code`: String, Unique Index.
* `discount_percent`: Integer (1-100, with CheckConstraint).
* `expires_at`: DateTime, Nullable (NULL = unlimited).
* `max_uses`: Integer, Nullable (NULL = unlimited).
* `current_uses`: Integer (default: 0).
* `allowed_user_id`: BigInteger (Foreign Key to User.id, NULL = for everyone).
* `target_product_id`: Integer (Foreign Key to Product.id, NULL = for all products).
####  0.2.5. Mailing System
* **MailingCampaign:**
    * `id`: Integer, Primary Key.
    * `name`: String (Internal name).
    * `text_content`: Text.
    * `status`: Enum (DRAFT, SCHEDULED, PROCESSING, COMPLETED, CANCELED).
    * `scheduled_at`: DateTime, Nullable.
    * `media_type`: Enum (PHOTO, VIDEO, ANIMATION, DOCUMENT, NONE).
    * `media_file_id`: String, Nullable.
    * `reply_markup`: JSONB (Serialized InlineButtons).
* **MailingLog:**
    * `id`: BigInteger, Primary Key.
    * `campaign_id`: Integer (Foreign Key).
    * `user_id`: BigInteger (Foreign Key).
    * `status`: Enum (PENDING, SUCCESS, FAILED).
    * `error_message`: Text, Nullable.
### 0.3. Integrations & External Services
* **Payment Gateways:** Integration with Robokassa and Prodamus via secure webhooks for processing Premium service purchases.
* **LLM Integration (Esoteric AI):** Connection to a specialized neural network API for esoteric consultations. The LLM context must be strictly isolated to esoteric topics via prompt engineering (bypassing tech support or billing queries).
### 0.4. Background & CPU-Bound Tasks (Strictly for NATS/FastStream Workers)
To prevent blocking the main aiogram event loop, the following tasks MUST be offloaded to isolated microservices:
* **Artifact Generation:** Creating graphical/PDF reports (e.g., Natal charts, Yantras) and uploading to NATS Object Store.
* **Heavy Processing & Scraping:** Complex astrological calculations and parsing external esoteric resources (using tools like Selenium where API is unavailable).
* **Mass Mailing:** Daily broadcast campaigns (e.g., morning horoscopes) for thousands of users using the MailingSystem entities.
### 0.5. Core User Flow Strategy
* **Progressive Profiling:** Users start with auto-collected data (Primary). Accessing deeper features requires manual profile completion (Secondary data: birth info, coords).
* **Tiered Access:** Clear separation between Free features (e.g., daily horoscopes) and Premium gated content (e.g., Yantras, deep calculations).

## 1. TECHNOLOGY STACK (STRICT)
* **Bot Framework:** `aiogram v3.4.x` (strictly asynchronous).
* **Complex UI/Dialogs:** `aiogram-dialog v2.2.0a3`.
* **Database & Driver:** PostgreSQL 17, `asyncpg` (relational storage).
* **ORM:** `SQLAlchemy v2.0.x` (modern async pattern, typing-first).
* **Migrations:** `alembic` (located in `/database/`).
* **Message Broker & Queues (Event-driven layer):** `NATS` v2.10+ (JetStream is used).
* **State Machine (FSM Storage):** NATS KeyValue (`nats-py`), custom implementation.
* **Object Storage (File Storage):** NATS Object Store.
* **Microservice Framework (Component interaction):** `FastStream` (for processing CPU-bound tasks outside the bot).
* **Internationalization (I18N):** `fluentogram` (Project Fluent format, `.ftl`).
* **Configuration Management:** `dynaconf` (settings in `settings.toml`, `secrets.toml`).
* **Logging:** `structlog` (structured logs).
* **Package Manager:** `Poetry`.
* **PROHIBITED:** The use of Redis, RabbitMQ, Celery, synchronous libraries (requests, psycopg2, etc.), standard logging, and direct print statements.

## 2. ABSTRACTION LAYERS (LOCATION & ISOLATION)
* **`/database/models/`** — Database layer. Declarative SQLAlchemy models are located here. Query logic MUST NOT leak into the bot configuration. The base abstract class (`Base`) is in `base.py`, entities in `models.py`.
* **`/database/migration/`** — Alembic scripts and environment for DB structure management.
* **`/I18N/locales/`** — Localization layer and user texts in `.ftl` format. Hardcoding English/Russian text in handlers is STRICTLY PROHIBITED.
* **`/bot/handling/handlers/`** — Handlers for single bot events (e.g., `start.py`, `get_user.py`). 
* **`/bot/handling/dialogs/`** — Complex UI states based on `aiogram-dialog` (screens, widgets, pagination).
* **`/bot/handling/states/`** — State graph (FSM) descriptions for the bot.
* **`/bot/handling/middlewares/`** — Interceptor layer. Responsible for dependency injection, DB session management, and retrieving language profiles.
* **`/bot/nats_storage/`** — FSM state storage layer (persistent storage based on NATS KV).
* **`/img-converter/`** (or similar services) — Autonomous background workers. Isolated FastStream microservices independent of aiogram. They handle binary and CPU-bound tasks.

## 3. DESIGN PATTERNS
* **Dependency Injection (DI):** Dependencies are injected globally via Middlewares. Handlers DO NOT create DB connections and DO NOT read config files directly — everything is passed via function arguments (`**kwargs` in `aiogram`, e.g., `i18n: TranslatorRunner`, `dialog_manager`).
* **State Machine Pattern (FSM):** User context is stored in `NATSFSMStorage` strictly outside the bot's RAM.
* **Event-Driven / Publisher-Subscriber Pattern:** All blocking (CPU / I/O intensive) business logic is moved out of the bot's event loop. The bot serializes the task (`Task`), pushes it to NATS -> Worker picks it up, processes it, and returns the response.
* **Claim Check Pattern:** Instead of passing binary data (images/documents) through the broker bus, the object is uploaded to NATS Object Store, and only the identifier (`img_uuid`) is passed to the broker.
* **Active Record / Repository Model:** Use of `relationship(lazy="selectin")` in SQLAlchemy 2.0 to preload dependent entities to avoid N+1 query problems.

## 4. CODE STYLE AND ROUTING RULES
* **Routing:** Adding handlers directly to the `Dispatcher` (dp) is STRICTLY PROHIBITED. Each domain (module) MUST have its own `Router()`. Registration of all routers is strictly consolidated in `/bot/handling/schema.py` (`dp.include_router(...)`).
* **Typing (PEP 484):** 100% Type Hints coverage (Python 3.10+). Exclusively explicit syntax (e.g., `Mapped[int]`).
* **DB Sessions:** Session management is inverted. `DatabaseMiddleware` initializes the transaction, passes the abstraction to the handler, and executes commit/rollback after the handler finishes. Explicit `session.commit()` calls inside handlers are PROHIBITED (except for complex, long-running transactions).
* **Dialogs vs Handlers:** Simple text commands (`/start`) are intercepted by classic Routers in `/handlers`. All navigation, pagination, and data collection (steps) are intercepted in `/dialogs` using `DialogManager`. Mixing these logic types is PROHIBITED.
* **Logging:** Total abandonment of standard `print()` and `logging`. ONLY `import structlog` is allowed. Any events must be accompanied by a JSON/text log: `logger.info()`.