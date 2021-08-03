import requests
from datetime import datetime
import json

vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
# ya_token = ''


class vk_user: #класс для работы с ВКонтакте
    url = 'https://api.vk.com/method/'

    def __init__(self, vk_token, version):
        self.params ={
            'access_token': vk_token,
            'v': version
        }
    def vk_get_photos(self, owner_id=31000938, count=5):
        #получаем json о фотографиях профиля
        get_photos_url = self.url + 'photos.get'
        get_photos_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': count
        }
        req = requests.get(get_photos_url, params={**self.params, **get_photos_params}).json()
        #проверяем, доступны ли нам фотографии
        if 'error' in req.keys():
            return print('Ошибка! Код', req['error']['error_code'])
        else:
            #обрабатываем json и передаём дальше только нужные нам параметры
            all_photos = req['response']['items']
            important_parameters=[]
            for photo in all_photos:
                important_parameters += [{'id' : photo['id'],
                    'url' : photo['sizes'][-1]['url'],
                    'date' : datetime.fromtimestamp(photo['date']).strftime("%d-%m-%Y"),
                    'likes' : photo['likes']['count'],
                    'size' : photo['sizes'][-1]['type']
                 }]
            print('Получаем данные о фотографиях из профиля Вконтакте ', owner_id)

            return ya_uploader(owner_id, important_parameters).upload()

class ya_uploader: #класс для работы с Яндекс Диском

    def __init__(self, file_path, important_parameters):
        self.file_path = file_path
        self.important_parameters = important_parameters
        # self.download_list = []

    def get_headers(self,):
        return {
                'Content-Type': 'application/json',
                'Authorization': 'OAuth ' + ya_token
        }

    def create_path(self): #создаём на ЯДиске папку с именем в виде id пользователя
        create_path_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {'path' : self.file_path}
        response = requests.put(create_path_url, headers=headers, params=params)
        print('Создаем папку ', owner_id, ', на вашем Яндекс Диске')

    def upload(self): #загружаем фотографии по полученному обработанному json'у
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        self.create_path()
        upload_list = []
        counter = 1
        ready_names = []
        for files in self.important_parameters: #проверяем, если ли уже такое имя файла
            file_name = str(files['likes'])
            # for file in upload_list:
            #     if file['file_name'] == str(files['likes']):
            #         file_name = str(files['likes']) + "_" + str(files['date'])
            #     else:
            #         file_name = str(files['likes'])
            if file_name in ready_names:
                file_name = file_name + '_' + files['date']
            ready_names += file_name
            path = '/' + self.file_path + '/' + file_name
            url = files['url']
            params = {'path': path, 'url': url}
            response = requests.post(upload_url, headers=headers, params=params)
            #добавляем в json нофрмацию о загруженных файлах
            upload_list += [{
                    "file_name": file_name,
                    "size": str(files['size'])
                }]
            print('Загружаем фото номер', counter)
            counter += 1
        print('Фотографии загружены, готовим отчет')
        self.upload_json(upload_list)


    def upload_json(self, upload_list): #сохраняем созданный json о загруженных файлах и отправляем на ЯДиск
        to_json = {'upload files': upload_list}
        with open('upload list', 'w') as f:
            f.write(json.dumps(to_json))
        upload_json_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        path = '/' + self.file_path + '/upload list.json'
        params = {'path': path, "overwrite": "true"}
        response = requests.get(upload_json_url, headers=headers, params=params)
        href = response.json().get("href")
        response = requests.put(href, data=open('upload list', 'rb'))
        print('Отчет на вашем Ядекс Диске в папке вместе с фотографими! \nРабота программы окончена!')

owner_id = str(input('Введите id пользователя vk: \n'))
ya_token = input('Введите токен Яндекс.Диска: \n')
count = int(input('Введите количество загружаемых фотографий: \n'))
vk_client = vk_user(vk_token, '5.131')
vk_client.vk_get_photos(owner_id, count)


