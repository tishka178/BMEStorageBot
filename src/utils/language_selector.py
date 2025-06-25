def select_language(language_code):
    languages = {
        "en": {
            "code": "en",
            "select_item": "Please select an item:",
            "choose_quantity": "Please select the quantity for",
            "choose_action": "What would you like to do with {item}?",
            "take": "Take",
            "return": "Return",
            "item_taken": "{quantity} units of {item} have been taken.",
            "item_returned": "{quantity} units of {item} have been returned.",
        },
        "ru": {
            "code": "ru",
            "select_item": "Пожалуйста, выберите предмет:",
            "choose_quantity": "Пожалуйста, выберите количество для",
            "choose_action": "Что вы хотите сделать с {item}?",
            "take": "Взять",
            "return": "Вернуть",
            "item_taken": "{quantity} единиц {item} было взято.",
            "item_returned": "{quantity} единиц {item} было возвращено.",
        },
        "ka": {
            "code": "ka",
            "select_item": "გთხოვთ აირჩიოთ ნივთი:",
            "choose_quantity": "გთხოვთ აირჩიოთ რაოდენობა",
            "choose_action": "რას აპირებთ {item}-თან?",
            "take": "აღება",
            "return": "დაბრუნება",
            "item_taken": "{quantity} ერთეული {item} აღებულია.",
            "item_returned": "{quantity} ერთეული {item} დაბრუნებულია.",
        },
        "az": {
            "code": "az",
            "select_item": "Zəhmət olmasa bir əşya seçin:",
            "choose_quantity": "Zəhmət olmasa miqdarı seçin",
            "choose_action": "{item} ilə nə etmək istəyirsiniz?",
            "take": "Götür",
            "return": "Qaytar",
            "item_taken": "{quantity} vahid {item} götürüldü.",
            "item_returned": "{quantity} vahid {item} qaytarıldı.",
        },
    }
    return languages.get(language_code, languages["en"])  # По умолчанию English