from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types


register = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Регистрация')]],
                           resize_keyboard=True)

exit = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= '🖊Внести изменения в анкету')]],
                           resize_keyboard=True)


exit_save = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= '🖊Внести изменения в анкету')],
                                     [KeyboardButton(text='⏳Отправить на проверку')]],
                           resize_keyboard=True)

user_profile = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Профиль')]],
                           resize_keyboard=True)

admin_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = '🔍Поиск пользователя'),
    KeyboardButton(text = '📢Рассылка')],
    [KeyboardButton(text='⏳Список ожидания')]],
    resize_keyboard=True)

inline_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔢 ID Telegram', callback_data='search_by_tg_id'),
     InlineKeyboardButton(text='📛 Имя', callback_data='search_by_name')],
    [InlineKeyboardButton(text='📞 Телефон', callback_data='search_by_phone'),
     InlineKeyboardButton(text='🏙️ Город', callback_data='search_by_city')],
    [InlineKeyboardButton(text='Марка автомобиля', callback_data='search_by_car_make'),
     InlineKeyboardButton(text='🚗 Гос номер автомобиля', callback_data='search_by_car_plate')],
    [InlineKeyboardButton(text='📜 Номер лицензии', callback_data='search_by_license')]
])


inline_edit_criteria = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ФИО", callback_data="edit_full_name"),
    InlineKeyboardButton(text="Город", callback_data="edit_city")],
    [InlineKeyboardButton(text="Марка автомобиля", callback_data="edit_car_make"),
    InlineKeyboardButton(text="Гос. номер автомобиля", callback_data="edit_car_plate")],
    [InlineKeyboardButton(text="Номер лицензии", callback_data="edit_license_number")]
])

admin_block_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Заблокировать'),
     KeyboardButton(text = 'Разблокировать')],
    [KeyboardButton(text = 'В главное меню')]
], resize_keyboard=True)

admin_block_user_2 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Без комментария')],
    [KeyboardButton(text = 'В главное меню')]
], resize_keyboard=True)

city_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Всем пользователям')],
    [KeyboardButton(text = 'По городам')]
], resize_keyboard=True)

approve_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Одобрить ')],
    [KeyboardButton(text = 'В главное меню')]
], resize_keyboard=True)

admin_back = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'В главное меню')]
], resize_keyboard=True)