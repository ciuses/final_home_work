import json
import time
import requests
from tokenators import vk_access_token as vk_token
from tokenators import vk_user_id as vk_id
from tokenators import ya_disk_token as ya_token


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

    def photo_info(self, album: str) -> dict:
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': album, 'extended': 1, 'photo_sizes': 1}  # Фото профиля
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def preparation(self, album: str = 'wall') -> dict:
        dict_with_info = {}
        for data_set in self.photo_info(album)['response']['items']:
            data_time = data_set['date']
            count_likes = data_set['likes']['count']  # {'count': 24, 'user_likes': 1}
            for img_inf in data_set['sizes']:
                if img_inf['type'] == 'z':  # in ['z', 'w']:
                    dict_with_info[data_time] = (count_likes, img_inf['type'], img_inf['url'])
        return dict_with_info

    def json_generator(self, dict_with_date: dict) -> list:
        filo_list = []
        for data_time, likes_size_link in dict_with_date.items():
            '''Подготовка даннных из входного словаря'''
            data_time_name = time.ctime(data_time).replace(' ', '_').replace(':', '')
            likes = likes_size_link[0]
            size = likes_size_link[1]
            name_for_yadisk = f'{data_time_name}_likes_{likes}.png'
            filo_list.append({'file_name': name_for_yadisk, 'size': size})

        j_name = time.ctime().replace(' ', '_').replace(':', '')
        with open(f'{j_name}.json', 'w', encoding='utf8') as filo:
            json.dump(filo_list, filo, indent=4, ensure_ascii=False)
        return filo_list

    def new_dir(self, yandex_token: str, dir_name: str) -> str:
        head = {'Authorization': f'OAuth {yandex_token}', 'Content-Type': 'application/json'}
        param = {'path': dir_name}
        resp = requests.put('https://cloud-api.yandex.net:443/v1/disk/resources', headers=head, params=param)
        print(f'Папка {dir_name} успешно создана, статус код: {resp.status_code}')
        return dir_name

    def send_to_ydisk(self, yandex_token: str, dict_with_date: dict, dir_name: str = 'Test3'):
        head = {'Authorization': f'OAuth {yandex_token}', 'Content-Type': 'application/json'}
        self.json_generator(dict_with_date)
        directory_name = self.new_dir(yandex_token, dir_name)

        for data_time, likes_size_link in dict_with_date.items():

            '''Подготовка даннных из входного словаря'''
            data_time_name = time.ctime(data_time).replace(' ', '_').replace(':', '')
            likes = likes_size_link[0]
            link = likes_size_link[2]
            name_for_yadisk = f'{data_time_name}_likes_{likes}.png'

            '''Получаем картинку с API VK'''
            response_from_vk = requests.get(link)
            print(f'Картинка получена, статус код: {response_from_vk.status_code}')  # Ожидаем 200

            '''Готовим ссылку для API yadisk и получаем её'''
            picto_object = response_from_vk.content
            param = {'path': f'disk:/{directory_name}/{name_for_yadisk}', 'overwrite': 'true'}
            response_from_yadisk_with_link = requests.get('https://cloud-api.yandex.net:443/v1/disk/resources/upload',
                                                          headers=head, params=param)
            print(f'Ссылка получена, статус код: {response_from_yadisk_with_link.status_code}')  # Ожидаем 200

            '''Берём ссылку и заливаем файловый объект на яндекс диск'''
            resp_dict = response_from_yadisk_with_link.json()
            special_link = resp_dict.get('href')
            response_from_yadisk_with_upload = requests.put(special_link, data=picto_object)
            print(
                f'Файл {name_for_yadisk} загружен на Диск, статус код: {response_from_yadisk_with_upload.status_code}')  # Ожидаем 201
        print('Загрузка файлов успешно завершена!')


if __name__ == '__main__':
    vk = VK(vk_token, vk_id)
    my_super_dict = vk.preparation()
    vk.send_to_ydisk(ya_token, my_super_dict, 'Netology')

    # TODO написать логику сортировки фоток от дублей меньшего размера
