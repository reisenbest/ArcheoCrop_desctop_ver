import shutil
import patoolib
import os
from rembg import remove
import re
from termcolor import colored

#регулярное выражение, которая проверяет цвет фона на валидность (4 числа из трех знаков макисмум. каждое число не больше 255, разделены запятыми без пробелов
regular_expression = r'^(?:\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]),(?:\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]),(?:\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]),(?:\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$'

# Жирный и цветной текст
text = colored('ARCHEO CROP V_1.0', 'red', attrs=['bold'])
about_author = colored('Powered by Selin Alexej. email: drgn96@gmail.com | tg: @reisen', 'green', attrs=['bold'])

def initial_text(text):
    print('\n')
    print(about_author)
    print('2023')
    print('\n')

    print(f'Добро пожаловать в программу обрезки фона у изображений {text}!')
    print('Эта программа может обрезать фон у отдельного изображения или у архива изображений')
    print("Перед использованием обязательно прочтите user_guide и README")
    print('\n')
    print('\n')


def initial_operation(num_of_operation):
    '''
    функция принимает цифру, отвечающую за определенный сценарий, и вызывает функционал,
    который соотвествует этому сценарию
    :param num_of_operation: int
    :return:
    '''
    if operation != 0 and operation != 1 and operation != 2:
        print('такой операции нет!')
        raise Exception("такой операции нет!")
    elif operation == 1:
        path_to_image = input('Введите полный путь к изображению, у которого хотите удалить фон: \n')
        result_name = input('Введите имя для обработанного изображения без расширения: \n')
        bg_color = input('Хотите ли вы какой-либо фон? y/n: \n')
        advanced_postprocess = input('Хотите ли вы использовать улучшенную обработку краев (влечет за собой снижение производительности)? y/n: \n')

        if bg_color == 'y':
            bg_color = input(
                'Введите желаемый цвет фона в формате R,G,B,A (числа через запятую, без пробелов. Например - 255,255,255,128): \n')
        else:
            bg_color = ''
        cropbg_one_img(path_to_image, result_name, bg_color, advanced_postprocess)

    elif operation == 2:
        path_to_archive = input('Введите полный путь к архиву ихображений, у которых вы хотите удалить фон: \n')
        folder_name = input('Введите имя для папки, с обработанными изображениями: \n')
        bg_color = input('Хотите ли вы какой-либо фон у обработанных фото? y/n: \n')
        advanced_postprocess = input('Хотите ли вы использовать улучшенную обработку краев (влечет за собой снижение производительности)? y/n: \n')

        if bg_color == 'y':
            bg_color = input(
                'Введите желаемый цвет фона в формате R,G,B,A (числа через запятую, без пробелов. Например - 255,255,255,128): \n')
        else:
            bg_color = ''
        cropbg_archive(path_to_archive, folder_name, bg_color, advanced_postprocess)

    elif operation == 0:
        exit()
    print('Спасибо, что воспользовались приложением. По контактным данным  в верхней части экрана вы можете связаться с автором и оставить свои отзывы\пожелания.')


def background_color_validity(bgcolor):
    '''
    функция проверяет валидность введенного пользователем фона.
    Если все ок - сохраняет его в необходимые переменные.
    Если ошибка - выдает текст ошибки и просит снова ввести цвет фона
    :param bgcolor: цвет фона в формате RGBA, введенный пользователем. тип str
    :return: возвращает bgcolor уже проверенный
        '''
    if bgcolor == '':
        pass
    else:
        cnt = 1
        while cnt == 1:
            regex = regular_expression
            if not re.match(regex, bgcolor):
                print('Некорректный формат цвета фона. Пожалуйста, введите в формате "R,G,B,A".')
                bgcolor = input(
                    'Введите желаемый цвет фона в формате R,G,B,A (числа через запятую, без пробелов. Например - 255,255,255,128: ')
            else:
                cnt = 0

    return bgcolor


def preprocess_bgcolor(bgcolor):
    '''
    функция предобрабатывает цвет фона, введенный пользователем.
    :param bgcolor: цвет фона в формате R,G,B,A, type str
    :return: list[int(R),int(G),int(B),int(A)]
    '''
    # удаляем пробелы. можно удалить так как это мы проверяем регулярным выражением
    bgcolor = bgcolor.replace(" ", "")

    # делим по запятой. получаем список
    bgcolor = bgcolor.split(',')

    # превращаем строковые значания в инты
    bgcolor = [int(el) for el in bgcolor]

    # распаковываем наш список в переменные

    return bgcolor





def cropbg_one_img(path_to_image, result_name, bgcolor='', advanced_postprocess=0): #принимает путь до изображения, у которого нужно кропнуть фон
    '''
    функция получает от пользователя путь до изображения, удаляет фон и сохраняет обработанное
    изображение под новым именем. Также принимает цвет для нового фона, по желанию пользователя.

    :param path_to_image: полный путь к изображению, которое хочет обработать пользователь str
    :param result_name: название для изображения, которое пользователь получит по итогу. Только название, путь будет такой же как у изначального изображения
    :param bgcolor: цвет фона в формате RGBA. По умолчанию пустая строка - отстутсвие фона
    :param advanced_postprocess: захотел ли пользователь делать улучшенню постобработку с уточнением краев
    :return:
    '''
    output_path = os.path.dirname(path_to_image) + '/'+result_name+'.png' # полный путь, по котором убудет сохранен результат

    bgcolor = background_color_validity(bgcolor)
    # Открываем исходное изображение для чтения в двоичном режиме
    with open(path_to_image, 'rb') as i:
        # Открываем выходной файл для записи в двоичном режиме
        with open(output_path, 'wb') as o:
            # Читаем содержимое исходного файла
            input_file = i.read()
            # Удаляем фон
            #bgcolor  (R, G, B, A) - можно задать фон у результирующего изображения. по умолчанию None
            # post_process_mask=True - сделает границы объектов резкими.
            #alpha_matting=True  - уточнит края
            #alpha_matting_erode_size >10, еще большее уточненеи края
            if advanced_postprocess == 'y':
                if bgcolor == '':
                    output = remove(input_file, post_process_mask=True, alpha_matting=True)
                else:
                    R, G, B, A = preprocess_bgcolor(bgcolor)  # распаковываем результат функции
                    output = remove(input_file, bgcolor=(R, G, B, A), post_process_mask=True, alpha_matting=True)  # оптимально, но можно лучше (потом разобраться)
            else:
                if bgcolor == '':
                    output = remove(input_file)
                else:
                    R, G, B, A = preprocess_bgcolor(bgcolor)  # распаковываем результат функции
                    output = remove(input_file, bgcolor=(R, G, B, A)) # Записываем результат в выходной файл
            o.write(output)
    print('путь до вашего изображения: ', output_path)


def cropbg_archive(path_to_archive, folder_name='', bgcolor='', advanced_postprocess=0):
    '''
    функция получает от пользователя путь до архива, создает папку, удаляет фон и сохраняет обработанное
    изображение под новым именем. Также принимает цвет для нового фона, по желанию пользователя.
    :param path_to_archive: полный путь к архиву, изображения в котором хочет обработать пользователь str
    :param result_name: название для изображения, которое пользователь получит по итогу. Только название, путь будет такой же как у изначального изображения
    :param bgcolor: цвет фона в формате RGBA. По умолчанию пустая строка - отстутсвие фон
    :param advanced_postprocess: захотел ли пользователь делать улучшенню постобработку с уточнением краев
    :return:
    '''


    bgcolor = background_color_validity(bgcolor)
    # Получаем путь к каталогу без расширения - для создания папки.
    directory_path = os.path.splitext(path_to_archive)[0]

    # Создаем каталог для извлеченных файлов
    os.mkdir(directory_path)

    # Извлекаем архив в указанный каталог
    patoolib.extract_archive(path_to_archive, outdir=directory_path)

    # Получаем список имен файлов в каталоге
    file_names = os.listdir(directory_path)

    # Создаем каталог для обрезанных изображений
    crop_directory = os.path.dirname(directory_path) + '/'+folder_name

    os.mkdir(crop_directory)


    # Обрезаем фон для каждого файла в папке
    for num, file_name in enumerate(file_names):
        cnt = num + 1

        # Путь к входному файлу
        input_path = os.path.join(directory_path, file_name)
        # Путь к выходному файлу
        output_path = os.path.join(crop_directory, os.path.splitext(file_name)[0] + '_00' + str(num + 1) + '.png')

        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                # Читаем содержимое входного файла
                input_data = i.read()
                # Удаляем фон
                # bgcolor  (R, G, B, A) - можно задать фон у результирующего изображения. по умолчанию None
                # post_process_mask=True - сделает границы объектов резкими.
                # alpha_matting=True  - уточнит края
                # alpha_matting_erode_size >10, еще большее уточненеи края
                if advanced_postprocess == 'y':
                    if bgcolor == '':
                        output_data = remove(input_data, post_process_mask=True, alpha_matting=True)
                    else:
                        R, G, B, A = preprocess_bgcolor(bgcolor)  # распаковываем результат функции
                        output_data = remove(input_data, bgcolor=(R, G, B, A), post_process_mask=True, alpha_matting=True)  # оптимально, но можно лучше (потом разобраться)
                else:
                    if bgcolor == '':
                        output_data = remove(input_data)
                    else:
                        R, G, B, A = preprocess_bgcolor(bgcolor)  # распаковываем результат функции
                        output_data = remove(input_data, bgcolor=(R, G, B, A))
                #счетчик примитивный
                print('COMPLETE:', cnt, '/', len(file_names))
                # Записываем результат в выходной файл
                o.write(output_data)
        cnt += 1

    shutil.rmtree(directory_path)
    print('Путь до папки, с обработанными изображениями: ', crop_directory )

initial_text(text)

operation = int(input('Выберите операцию: '))

initial_operation(operation)
print('\n')
print(about_author)
print('2023')
input('нажмите любую клавишу для выхода')







