from aiogram.fsm.state import StatesGroup, State

class Driver(StatesGroup):
    last_name = State()
    first_name = State()
    middle_name = State()
    phone = State()
    city = State()
    car_make = State()
    car_plate = State()
    license_number = State()
    license_front = State()
    license_back = State()
    car_photo_1 = State()
    car_photo_2 = State()
    car_photo_3 = State()
    selfie_with_car = State()
    save =State()

class SearchState(StatesGroup):
    waiting_for_field_value = State()  # Ожидание значения для выбранного критерия
    selected_user = State()  # Выбранный пользователь для редактирования
    waiting_for_edit_criteria = State()
    waiting_for_edit_value = State()
    block_user = State()


class RassylkaStates(StatesGroup):
    choosing_rassylka_type = State()  # Выбор типа рассылки
    awaiting_city_name = State()  # Ожидание ввода города
    awaiting_rassylka_text = State()  # Ожидание ввода текста рассылки
    awaiting_rassylka_text_city = State()