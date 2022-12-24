import re
from dataclasses import dataclass

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

DRIVER_PATH = "C:\\Users\\user\\PycharmProjects\\selenium\\chromedriver.exe"
BASE_URL = "https://petfriends.skillfactory.ru/"
ALL_PETS_URL = f"{BASE_URL}all_pets"
MY_PETS_URL = f"{BASE_URL}my_pets"
LOGIN_URL = f"{BASE_URL}login"
LOGIN = "ann@spbivc.ru"
PASSWORD = "tLRysrVq5REhdFx"


@dataclass
class Pet:
    name: str
    animal_type: str
    age: int

    @staticmethod
    def from_table_tr(pet):
        attrs = pet.find_elements(By.TAG_NAME, "td")
        return Pet(
            name=attrs[0].text,
            animal_type=attrs[1].text,
            age=int(attrs[2].text)
        )

    def __hash__(self):
        return hash((self.name, self.animal_type, self.age))


@pytest.fixture(scope="session")
def my_pets_page():
    pytest.driver = webdriver.Chrome(DRIVER_PATH)
    pytest.driver.get(LOGIN_URL)
    pytest.driver.find_element(By.ID, 'email').send_keys(LOGIN)
    pytest.driver.find_element(By.ID, 'pass').send_keys(PASSWORD)
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    assert pytest.driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"
    pytest.driver.get(MY_PETS_URL)
    yield pytest.driver

    pytest.driver.quit()


def test_show_all_my_pets(my_pets_page):
    """
    Присутствуют все питомцы.
    """
    pet_stats = WebDriverWait(my_pets_page, timeout=10).until(lambda el: el.find_element(By.CLASS_NAME, "task3"))
    pet_count_in_stats = int(re.findall(r"Питомцев: (\d)", pet_stats.text)[0])
    my_pets_table = my_pets_page.find_element(By.TAG_NAME, "tbody")
    my_pets_count_in_table = len(my_pets_table.find_elements(By.TAG_NAME, "tr"))
    assert pet_count_in_stats == my_pets_count_in_table


def test_my_pets_photo(my_pets_page):
    """
    Хотя бы у половины питомцев есть фото.
    """
    pet_count_in_stats = int(re.findall(r"Питомцев: (\d)", my_pets_page.find_element(By.CLASS_NAME, "task3").text)[0])
    my_pets_table = my_pets_page.find_element(By.TAG_NAME, "tbody")
    my_pets_with_photo = len(
        [
            pet for pet in my_pets_table.find_elements(By.TAG_NAME, "th")
            if pet.find_element(By.TAG_NAME, "img").get_attribute("src")
        ]
    )
    assert my_pets_with_photo * 2 >= pet_count_in_stats


def test_all_info_filled(my_pets_page):
    """
    У всех питомцев есть имя, возраст и порода.
    """
    my_pets_table = my_pets_page.find_element(By.TAG_NAME, "tbody")
    for pet in my_pets_table.find_elements(By.TAG_NAME, "tr"):
        for pet_attribute in pet.find_elements(By.TAG_NAME, "td")[:3]:
            assert pet_attribute.text.strip()


def test_all_pets_with_different_name(my_pets_page):
    """
    У всех питомцев разные имена.
    """
    my_pets_table = my_pets_page.find_element(By.TAG_NAME, "tbody")
    pet_names = [
        pet.find_element(By.TAG_NAME, "td").text.strip() for pet in
        my_pets_table.find_elements(By.TAG_NAME, "tr")
    ]
    assert len(pet_names) == len(set(pet_names))


def test_all_pets_with_different(my_pets_page):
    """
    В списке нет повторяющихся питомцев. (Сложное задание).
    """
    my_pets_table = my_pets_page.find_element(By.TAG_NAME, "tbody")
    pets = [Pet.from_table_tr(pet) for pet in my_pets_table.find_elements(By.TAG_NAME, "tr")]
    assert len(pets) == len(set(pets))
