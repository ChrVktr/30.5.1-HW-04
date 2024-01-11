import re

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get("https://petfriends.skillfactory.ru/login")
    yield driver
    driver.quit()


def test_checking_my_pets(driver):
    # Заполнение логина и пароля
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "email"))
    ).send_keys("sh.sergey.yur@yandex.ru")

    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "pass"))
    ).send_keys("Equilibrium")

    # Авторизация
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    ).click()

    # Переход на сраницу моих питомцев
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//a[@href='/my_pets']"))
    ).click()

    # Елемент данных пользователя
    user_data_element = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'SergeyYur')]//.."))
    )

    # Количество питомцев в елементе данных пользователя
    match = re.search(r"Питомцев: (?P<count_pets>\d+)", user_data_element.get_attribute("innerHTML"))
    assert match is not None
    count_my_pets = int(match.group("count_pets"))

    # Таблица моих питомцев
    pet_table_element = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//div[@id='all_my_pets']//tbody"))
    )

    # Заполнение данных о моих питомцах
    all_my_pets = []
    for pet_element in WebDriverWait(pet_table_element, 10).until(
            expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "tr"))
    ):
        photo_element = pet_element.find_element(By.TAG_NAME, "th").find_element(By.TAG_NAME, "img")
        data_elements = pet_element.find_elements(By.TAG_NAME, "td")
        all_my_pets.append({
            "photo": photo_element.get_attribute("src"),
            "name": data_elements[0].text,
            "breed": data_elements[1].text,
            "age": int(data_elements[2].text)
        })

    # 1. Присутствуют все питомцы.
    assert len(all_my_pets) == count_my_pets

    # 2. Хотя бы у половины питомцев есть фото
    assert len([
        my_pet
        for my_pet in all_my_pets
        if my_pet["photo"]
    ]) >= count_my_pets / 2

    # 3. У всех питомцев есть имя, возраст и порода.
    assert len([
        my_pet
        for my_pet in all_my_pets
        if my_pet["name"] and my_pet["breed"] and my_pet["age"]
    ]) == count_my_pets

    # 4. У всех питомцев разные имена.
    assert len(set(
        my_pet["name"]
        for my_pet in all_my_pets
    )) == count_my_pets

    # 5. В списке нет повторяющихся питомцев. (Сложное задание).
    assert len(set(
        (my_pet["photo"], my_pet["name"], my_pet["breed"], my_pet["age"])
        for my_pet in all_my_pets
    )) == count_my_pets
