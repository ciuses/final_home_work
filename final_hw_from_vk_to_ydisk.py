import requests

from tokenators import vk_access_token as vk_token
from tokenators import vk_user_id as vk_id
from json_writer import json_writer as j_w


class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self) -> dict:
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def photo_info(self) -> dict:
        url = 'https://api.vk.com/method/photos.get'
        # params = {'user_ids': self.id}
        params = {'owner_id': self.id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1} # Фото профиля
        params = {'owner_id': self.id, 'album_id': 'wall', 'extended': 1, 'photo_sizes': 1} # Фото профиля
        response = requests.get(url, params={**self.params, **params})
        return response.json()


if __name__ == '__main__':
    vk = VK(vk_token, vk_id)
    # print(vk.users_info())
    # print(vk.photo_info())
    j_w(vk.photo_info(), 'my_j_wall.json')
