# TECHNICAL SPECIFICATION AND AI AGENT GUIDELINES (TECH_SPEC)

**CRITICAL FOR AI AGENTS:** This document is the absolute and inviolable standard for this project. Any deviation from the tech stack, abstraction layers, or code style rules is STRICTLY PROHIBITED without explicit direct instruction from the user. 

## 0. CORE PROJECT & BUSINESS LOGIC
* [TO BE FILLED LATER: Detailed description of the problem being solved, main user flow, and the list of resource-intensive tasks to be offloaded to microservices] *

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