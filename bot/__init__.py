from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from .start import start, get_contact, report_issue, get_topic, topic_description, \
    printer_id_input, get_data, issue_description, getting_company, getting_location, user_attachment, \
    admin_choice, company_change_lock, adding_company, select_company, company_select_step, action_commit, \
    user_change_lock, select_user_from_list, select_user, user_selected_step, delete_certificated_user
from .help import help, help_descr
from .bot_commands import bot_commands
from .applied_commands import get_report
from .states import Register, Report, Several, Admin, CompanyPanelClass, UserPanelClass


def register_user_commands(router: Router) -> None:
    router.message.register(start, CommandStart())
    router.message.register(help, Command(commands=['help']))
    router.message.register(help_descr, F.text == 'Помощь')
    router.message.register(get_report, Command(commands=['report']))

    router.message.register(get_contact, Register.get_numbers)

    router.message.register(get_topic, Report.topic)
    router.message.register(topic_description, Several.get_topic_description)
    router.message.register(printer_id_input, Several.get_printer_id)
    router.message.register(get_data, Report.data)
    router.message.register(issue_description, Several.get_issue_description)
    router.message.register(report_issue, Report.issue)
    router.message.register(getting_company, Register.get_company)
    router.message.register(getting_location, Register.get_location)
    router.message.register(user_attachment, Register.attachment)

    router.message.register(admin_choice, Admin.choice)

    router.message.register(company_change_lock, CompanyPanelClass.lock_panel)
    router.message.register(adding_company, CompanyPanelClass.adding_company_name)
    router.message.register(select_company, CompanyPanelClass.selecting_company)
    router.message.register(company_select_step, CompanyPanelClass.select_step)
    router.message.register(action_commit, CompanyPanelClass.action)

    router.message.register(user_change_lock, UserPanelClass.lock_panel)
    router.message.register(select_user, UserPanelClass.selecting_user)
    router.message.register(user_selected_step, UserPanelClass.select_step)
    router.message.register(delete_certificated_user, UserPanelClass.delete_action)
