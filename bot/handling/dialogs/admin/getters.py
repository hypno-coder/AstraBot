from aiogram_dialog import DialogManager

async def get_admin_data(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data["i18n"]
    
    return {
        "admin_btt": i18n.admin_btt(),
        "admin_header": i18n.admin_header(users=1500, cash=5000, ai_status="OK"),
        "lang_toggle": i18n.lang_toggle(),
        "admin_back": i18n.admin_back(),
        
        "btn_admin_analytics": i18n.btn_admin_analytics(),
        "btn_admin_users": i18n.btn_admin_users(),
        "btn_admin_finance": i18n.btn_admin_finance(),
        "btn_admin_broadcast": i18n.btn_admin_broadcast(),
        "btn_admin_tech": i18n.btn_admin_tech(),
        
        "stub_analytics_stats": i18n.stub_analytics_stats(),
        "stub_analytics_tokens": i18n.stub_analytics_tokens(),
        "stub_analytics_payments": i18n.stub_analytics_payments(),
        
        "stub_users_search": i18n.stub_users_search(),
        "stub_users_block": i18n.stub_users_block(),
        "stub_users_reply": i18n.stub_users_reply(),
        "stub_users_dialogs": i18n.stub_users_dialogs(),
        
        "stub_finance_search": i18n.stub_finance_search(),
        "stub_finance_gift": i18n.stub_finance_gift(),
        "stub_finance_prices": i18n.stub_finance_prices(),
        "stub_finance_promos": i18n.stub_finance_promos(),
        
        "stub_broadcast_create": i18n.stub_broadcast_create(),
        "stub_broadcast_stats": i18n.stub_broadcast_stats(),
        
        "stub_tech_maintenance": i18n.stub_tech_maintenance(),
        "stub_tech_admin": i18n.stub_tech_admin(),
        "stub_tech_restart_bot": i18n.stub_tech_restart_bot(),
        "stub_tech_restart_server": i18n.stub_tech_restart_server(),
        "stub_tech_block_bot": i18n.stub_tech_block_bot(),
        
        "confirm_action_prompt": i18n.confirm_action_prompt(),
        "btn_confirm_yes": i18n.btn_confirm_yes(),
        "btn_confirm_no": i18n.btn_confirm_no(),
    }
