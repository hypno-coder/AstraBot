enter_image = "Загрузите фото"
enter_watermark = "Напишите текст вотермарки"
in_progress = "Ща вотермарка наложится"
db_get_user = Юзер {$user}

main_menu_prompt = Выберите опцию:
#Buttons
horoscope_btt = Гороскоп
compatibility_btt = Совместимость
sonnik_btt = Сонник
premium_features_btt = Премиум функции

# Profile UI
profile_btt = 👤 Мой профиль
profile_title = <b>👤 Ваш профиль:</b>

profile_fio = 👤 ФИО: { $fio }
profile_gender = 🚻 Пол: { $gender }
profile_city = 🏙 Место рождения: { $birth_city }
profile_birthday = 📅 Дата рождения: { $birthday }
profile_time = 🕒 Время рождения: { $birth_time }
profile_timezone = 🌍 Ваше время (UTC): { $timezone }

profile_not_set = Не указано ❌

btn_edit_fio = ✏️ ФИО
btn_edit_gender = ✏️ Пол
btn_edit_city = ✏️ Место рожд.
btn_edit_birthday = ✏️ Дату рожд.
btn_edit_time = ✏️ Время рожд.
btn_edit_timezone = ✏️ Часовой пояс
btn_back = 🔙 Назад

# Profile Prompts
prompt_fio = ✍️ Введите ваше ФИО полностью:
prompt_city = ✍️ Введите город рождения:
prompt_birthday = 📅 Выберите вашу дату рождения:
prompt_time = 🕒 Введите время рождения (в формате ЧЧ:ММ, например 14:30):
prompt_timezone = 🌍 Выберите ваш часовой пояс относительно UTC:
prompt_gender = 🚻 Выберите ваш пол:
gender_male = Мужской
gender_female = Женский
gender_unknown = Не указан
error_time_format = ❌ Неверный формат времени! Используйте формат ЧЧ:ММ (например 14:30).

# Geocoding Confirmation
confirm_city_prompt = 📍 Это ваш город?
    <b>{ $address }</b>
btn_yes_city = ✅ Да, верно
btn_no_city = ❌ Нет, ввести заново
error_city_not_found = ❌ Мы не смогли найти такой город. Попробуйте еще раз или введите более крупный соседний город.

# Admin Panel

admin_btt = 🔐 Админ Панель
admin_header = 📊 Юзеров: { $users } | 💰 Касса сегодня: { $cash } | 🧠 ИИ: { $ai_status }
lang_toggle = 🇺🇸 Переключить на английский
admin_back = ⬅️ Назад

btn_admin_analytics = 📊 Аналитика и Статистика
btn_admin_users = 👥 Управление пользователями
btn_admin_finance = 💳 Финансы и Тарифы
btn_admin_broadcast = 📢 Рассылка и Вещание
btn_admin_tech = 🛠 Техзона

# Analytics
stub_analytics_stats = Статистика
stub_analytics_tokens = Расход токенов
stub_analytics_payments = Список оплат

# Users
stub_users_search = Поиск пользователя
stub_users_block = Блокировка/Разблокировка
stub_users_reply = Ответ от имени бота
stub_users_dialogs = Диалоги

# Finance
stub_finance_search = Поиск по чеку/ID
stub_finance_gift = Подарить Premium
stub_finance_prices = Изменение цен
stub_finance_promos = Промокоды

# Broadcasting
stub_broadcast_create = Создать рассылку
stub_broadcast_stats = Статистика рассылки

# Tech Zone
stub_tech_maintenance = Режим техобслуживания
stub_tech_admin = Создание админа
stub_tech_restart_bot = Перезагрузка бота
stub_tech_restart_server = Перезагрузка сервера
stub_tech_block_bot = Блокировка бота

confirm_action_prompt = ⚠️ Вы уверены? Это повлияет на всю систему.
btn_confirm_yes = ✅ Да, я уверен
btn_confirm_no = ❌ Нет, отмена

# Horoscope
horo_ask_dob = 📅 Для гороскопа нам нужна ваша дата рождения. Выберите её:
horo_select_period = Выберите период:
horo_compat_btt = 🔮 Совместимость
horo_ask_own_gender = 🚻 Укажите ваш пол для расчёта совместимости:
horo_compat_male = 👨 Мужчина
horo_compat_female = 👩 Женщина
horo_compat_zodiac = ♈ Выберите знак зодиака партнёра:
horo_finance = Финансы
horo_health = Здоровье
horo_love = Любовь
horo_error = ⚠️ Гороскоп временно недоступен. Попробуйте позже.

# Referral
ref_btt = 💎 Реферальная программа
ref_title = <b>💎 Реферальная программа</b>
ref_progress = 👥 Приглашено: { $current } из { $goal }
ref_premium_active = ✅ Premium активен до: { $date }
ref_premium_inactive = ❌ Premium: не активен
ref_body =
    Приглашайте друзей и получайте <b>30 дней Premium</b> за каждые 5 успешных приглашений.
    
    Друг должен запустить бота по вашей ссылке, чтобы приглашение засчиталось! 🚀
ref_invite_btt = 🔗 Пригласить друга
ref_invite_share_text = Привет! Попробуй этот Астро-бот 🌟 https://t.me/{ $bot_username }?start={ $user_id }
