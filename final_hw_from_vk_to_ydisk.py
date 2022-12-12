import time
import requests
from tokenators import vk_access_token as vk_token
from tokenators import vk_user_id as vk_id
from tokenators import ya_disk_token as ya_token
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
        # params = {'owner_id': self.id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1} # Фото профиля
        params = {'owner_id': self.id, 'album_id': 'wall', 'extended': 1, 'photo_sizes': 1}  # Фото профиля
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def preparation(self) -> dict:
        dict_with_info = {}
        for data_set in self.photo_info()['response']['items']:
            # print(time.ctime(data_set['date']).replace(' ', '_'))
            # print(data_set['likes']['count'])
            data_time = data_set['date']
            count_likes = data_set['likes']['count']  # {'count': 24, 'user_likes': 1}
            for img_inf in data_set['sizes']:
                if img_inf['type'] == 'z':  # in ['z', 'w']:
                    dict_with_info[data_time] = (count_likes, img_inf['type'], img_inf['url'])
        return dict_with_info

    def downloader_picture(self, my_structure, filo_path: str = '.\\papko\\pikto\\'):
        for data_time, likes_size_link in my_structure.items():
            part_of_name = time.ctime(data_time).replace(' ', '_').replace(':', '')
            likes = likes_size_link[0]
            size = likes_size_link[1]
            link = likes_size_link[2]
            full_path = f'{filo_path}{part_of_name}_{likes}.png'
            response = requests.get(link)
            picto = response.content
            with open(full_path, 'wb') as filo:
                filo.write(picto)
            print(f'Загружено {full_path}')

    def send_to_ydisk(self, yandex_token: str, dict_with_date: dict):
        head = {'Authorization': f'OAuth {yandex_token}', 'Content-Type': 'application/json'}
        for data_time, likes_size_link in dict_with_date.items():

            '''Подготовка даннных из входного словаря'''
            data_time_name = time.ctime(data_time).replace(' ', '_').replace(':', '')
            likes = likes_size_link[0]
            size = likes_size_link[1]
            link = likes_size_link[2]
            name_for_yadisk = f'{data_time_name}_likes_{likes}.png'

            '''Получаем картинку с API VK'''
            response_from_vk = requests.get(link)
            print(response_from_vk.status_code)

            '''Готовим ссылку для API yadisk и получаем её'''
            picto_object = response_from_vk.content
            param = {'path': f'disk:/Netology/{name_for_yadisk}', 'overwrite': 'true'}
            response_from_yadisk_with_link = requests.get('https://cloud-api.yandex.net:443/v1/disk/resources/upload',
                                                          headers=head, params=param)
            print(response_from_yadisk_with_link.status_code)

            '''Берём ссылку и заливаем файловый объект на яндекс диск'''
            resp_dict = response_from_yadisk_with_link.json()
            special_link = resp_dict.get('href')
            response_from_yadisk_with_upload = requests.put(special_link, data=picto_object)
            print(response_from_yadisk_with_upload.text, response_from_yadisk_with_upload.status_code)


if __name__ == '__main__':
    # vk = VK(vk_token, vk_id)
    # print(vk.users_info())
    # print(vk.photo_info())
    # j_w(vk.photo_info(), 'my_j_wall.json')
    # raw_data = vk.photo_info()  # dict with all date
    # vk.downloader_picture(vk.preparation())
    vk = VK(vk_token, vk_id)
    my_super_dict = vk.preparation()
    vk.send_to_ydisk(ya_token, my_super_dict)

    # TODO написать логику сортировки фоток от дублей меньшего размера
    # TODO оформить покрасивше
