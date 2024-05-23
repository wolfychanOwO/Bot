from aiogram.filters.state import State, StatesGroup


class Register(StatesGroup):
    get_company = State()
    get_location = State()
    attachment = State()
    get_numbers = State()


class Report(StatesGroup):
    topic = State()
    data = State()
    issue = State()


class Several(StatesGroup):
    get_topic_description = State()
    get_topic_choice = State()
    get_printer_id = State()
    get_issue_description = State()
    go_back_topic = State()
    go_back_description = State()


class Admin(StatesGroup):
    choice = State()


class CompanyPanelClass(StatesGroup):
    lock_panel = State()
    adding_company_name = State()
    selecting_company = State()
    select_step = State()
    action = State()


class UserPanelClass(StatesGroup):
    lock_panel = State()
    selecting_user = State()
    select_step = State()
    delete_action = State()
