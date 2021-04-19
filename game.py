# Created by Helga on 07.12.2020

import sys
import pygame
from random import randrange, randint


def print_text(message, x, y, font, font_color=(0, 0, 0)):  # печать текста
    text = font.render(message, True, font_color)
    screen.blit(text, (x, y))


def draw_image(x, y, width, height, pict):  # отрисовка картинки
    rect = pygame.Rect(x, y, x + width, y + height)
    pygame.Surface.blit(screen, pict, rect)


class Button:  # класс кнопки
    def __init__(self, width, height, inactive_color, active_color):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, action=None):  # отрисовка кнопки
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height))  # отрисовка при нажатии
            if click[0] == 1 and action is not None:
                action()
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))  # отрисовка неактивной

        print_text(message, x + 45, y + 7, font_medium, text_color_dark)  # печать текста на кнопке


def getCountMinesNear(mine, i, j):
    n = 0
    for k in range(-1, 2):
        for l in range(-1, 2):
            # икл по клееткам рядом
            x = i + k
            y = j + l
            if x < 0 or x >= N or y < 0 or y >= N:
                continue
            if mine[x][y] < 0:
                n += 1  # нашли мину увеличиваем счетчик

    return n


def makeMap(mine):
    n = M
    while n > 0:
        # рандомно выбираем координаты мины пока количество мин не будет равно выбранному
        i = randrange(N)
        j = randrange(N)
        if mine[i][j] != 0:
            continue  # еслимина стоит пропускаем
        mine[i][j] = -1
        n -= 1

    for i in range(N):
        for j in range(N):
            if mine[i][j] >= 0:
                mine[i][j] = getCountMinesNear(mine, i, j)  # считаем сколько мин вокруг каждой клетки


def debug_print(field):  # печать в консоль переданного поля (карта мин или текущее состояние поля для дебага
    for i in range(N):
        for j in range(N):
            print(str(field[j][i]).rjust(3), end="")
        print()


def show_field(map):  # отрисовка текущего состояния поля
    for i in range(N):
        for j in range(N):
            default_color = (250, 245, 120)
            mine_indicate_color = (255, 0, 0)
            white = (255, 255, 255)
            # координаты нужного места в поле
            x = i * width + (i + 1) * margin
            y = j * height + (j + 1) * margin

            if map[i][j] == -1:  # бомба - отрисовка картинки
                pict = pict_bomb
                pict_width = pict.get_width()
                pict_height = pict.get_height()

                # изменение размера изображения
                scale = pygame.transform.scale(pict,
                                               (pict_width * width // pict_width, pict_height * height // pict_height))
                scale_rect = scale.get_rect(center=(x + width // 2, y + width // 2))
                screen.blit(scale, scale_rect)
            # неоткрытая клетка
            elif map[i][j] == -2:
                pygame.draw.rect(screen, default_color, (x, y, width, height))
            # индикатор мины, для правой кнокпи мыши
            elif map[i][j] == -3:
                pygame.draw.rect(screen, mine_indicate_color, (x, y, width, height))
            # цифры
            else:
                pygame.draw.rect(screen, white, (x, y, width, height))
                # шрифт для размерности поля
                text = font_game.render(str(map[i][j]), True, font_color_list[map[i][j]])
                text_rect = text.get_rect()
                text_rect.center = [x + width // 2, y + height // 2]  # центруем текст в ячейке
                screen.blit(text, text_rect)
    pygame.display.update()


def choose_cell():  # ыбор ячейки
    global x, y
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_mouse, y_mouse = pygame.mouse.get_pos()
            x = x_mouse // (margin + width)  # номер колонки где было нажатие
            y = y_mouse // (margin + height)  # номер строки где было нажатие
            return (x, y, event.button == pygame.BUTTON_RIGHT)  # координаты ячейки в поле
            # проверка правой или левой кнопкой мыши нажатие
    return (-1, -1, -1)  # не нажал в поле


def getOpenEntyMinesNear(i, j):  # после пустышки открываем стоящие рядом
    # цикл по 8 клеткам вокруг заданной клетки
    for k in range(-1, 2):
        for l in range(-1, 2):
            x = i + k
            y = j + l
            # перестаем проверять если попадает за границы или уже проверена
            if x < 0 or x >= N or y < 0 or y >= N or cell_checked[x][y] == 1:
                continue
            cell_checked[x][y] = 1  # записываем какие проверены
            if mine[x][y] == 0:
                field[x][y] = mine[x][y]
                getOpenEntyMinesNear(x, y)  # оиск следующей
            elif mine[x][y] > 0:
                field[x][y] = mine[x][y]  # след нет, открываем границы цифр


def getState(field, mine):  # получение состояния игры
    for i in range(N):
        for j in range(N):
            # открыта мина
            if field[i][j] > -2 and mine[i][j] < 0: return STATE_LOSE  # проигрыш

    for i in range(N):
        for j in range(N):
            # клетка помечена без мины
            if field[i][j] == -3 and mine[i][j] != -1: return STATE_PLAY  # продолжаем

    finded = True
    for i in range(N):
        for j in range(N):
            if field[i][j] != -3 and mine[i][j] == -1:
                finded = False
                break

    if finded:
            return STATE_WIN  # выигрыш, если не все ячейки открыты, но все мины расставлены верно правой кнопкой мыши)

    for i in range(N):
        for j in range(N):
            # не открыты все клетки
            if field[i][j] == -2 and mine[i][j] >= 0: return STATE_PLAY  # продолжаем

    return STATE_WIN


def NisClick(x_mouse, y_mouse):  # где было нажатие, какую размерность поля выбрал пльзователь
    for i in range(9):
        x = 40 if i % 3 == 0 else (170 if i % 3 == 1 else 300)
        y = 40 if i < 3 else (170 if i < 6 else 300)
        if x < x_mouse < x + map_size and y < y_mouse < y + map_size:
            return i + 2
    return 0


def showMenuLevel():  # смена экрана меню на уровни
    global menu
    menu = MENU_LEVEL


def exit():  # выход из игры
    pygame.quit()
    sys.exit(0)


def game_render():
    global field, mine, cell_checked, N, M, map_size, state, menu, width, height, margin, font_game
    map_size = 115

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()  # выход

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x_mouse, y_mouse = pygame.mouse.get_pos()
                if menu == MENU_LEVEL:
                    N = NisClick(x_mouse, y_mouse)  # проверка выбрал ли пользователь Поле и какой размерности
                    if N > 0:  # выбрал поле N
                        # создаем игру, рассчитываем поле
                        font_game = pygame.font.SysFont("Algerian", font_size_list[N - 2])  # выбираем шрифт для букв
                        state = STATE_PLAY  # статус игры
                        menu = MENU_GAME  # игровое поле
                        M = randint(N, N + 1 * N // 3)  # генерация количества мин
                        margin = 5
                        width = height = ((size[0] - margin) // N) - margin
                        field = [[-2] * N for i in range(N)]  # неоткрытая ячейка -2 в поле
                        mine = [[0] * N for i in range(N)]
                        makeMap(mine)  # постановка мин, подсчет сколько вокруг, генерация поля
                        debug_print(mine)  # вывод для дебага сгенерированного поля
                        print('\n')

        screen.fill(background_color)

        if menu == MENU_MAIN:
            button_play.draw(30, 335, "ИГРАТЬ", showMenuLevel)  # вызываем по нажатию следующее меню
            button_quit.draw(235, 335, "ВЫЙТИ", exit)  # выход
            # отрисовка главного меню:
            draw_image(175, 160, 105, 105, pict_logo)
            draw_image(240, 350, 35, 35, pict_exit)
            draw_image(35, 350, 35, 35, pict_start)
            print_text("САПЕР", 95, 0, font_big, (255, 255, 255))

        elif menu == MENU_LEVEL:
            for i in range(9):
                # отрисовка картинок для уровней
                x = 40 if i % 3 == 0 else (170 if i % 3 == 1 else 300)
                y = 40 if i < 3 else (170 if i < 6 else 300)
                draw_image(x, y, map_size, map_size, pict_maps[i])

        elif menu == MENU_GAME:
            pygame.draw.rect(screen, background_color, (0, 0, size[0], size[1]))
            show_field(field)  # отрисовка текущего состояния поля

            if state == STATE_PLAY:  # играем
                # debug_print(field) #вывод для дебага текущаго состояние поля
                # print('\n')
                x, y, flag = choose_cell()  # выбор ячейки
                if x >= 0 and y >= 0:
                    field[x][y] = -3 if flag else mine[x][y]  # правая кнопка - ставим значок мины, левая - значение из карты
                    if field[x][y] == 0:  # если пустая ячейка открываем все пустые рядом до границы
                        cell_checked = [[0] * N for i in range(N)]
                        getOpenEntyMinesNear(x, y)
                state = getState(field, mine)  # проверяем состояние игры

            else:  # конец игры
                pygame.time.delay(500)
                show_field(mine)  # показываем мины
                pygame.time.delay(1000)
                s = pygame.Surface((1000, 750), pygame.SRCALPHA)
                s.fill((137, 137, 137, 57))
                screen.blit(s, (0, 0))  # атемняем поле
                # уведомляем пользователя о победе или поражении
                if state == STATE_LOSE:
                    draw_image(80, 90, 295, 215, pict_beating)
                    print("Вы проиграли")
                elif state == STATE_WIN:
                    draw_image(80, 90, 295, 215, pict_win)
                    print("Вы выиграли")
                pygame.display.flip()
                pygame.time.delay(1000)
                menu = MENU_MAIN  # возвращаемся в главное меню

        pygame.display.flip()  # обновляем экран


if __name__ == '__main__':
    pygame.init()  # запускаем пайгем
    size = (455, 455)
    background_color = (59, 0, 96)
    text_color_dark = (59, 0, 96)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Сапер")

    # загрузка картинок для лого, иконок, уведомлений  и бомбы
    pict_beating = pygame.image.load("images/beating.png")
    pict_win = pygame.image.load("images/win.png")
    pict_bomb = pygame.image.load("images/bomb.png")
    pict_logo = pygame.image.load("images/logo.png")
    pict_exit = pygame.image.load("images/icon_exit.png")
    pict_start = pygame.image.load("images/icon_start.png")

    # загрузка картинок для уровней
    pict_maps = []
    for i in range(2, 11):
        pict_maps.append(pygame.image.load("images/map" + str(i * i) + ".png"))

    font_big = pygame.font.SysFont("Segoe Print", 65)  # загрузка шрифтов для Названия
    font_medium = pygame.font.SysFont("Segoe Print", 30)  # загрузка шрифтов для кнопок
    # размеры шрифтов цифр для разных типов полей
    font_size_list = [220, 150, 115, 85, 70, 60, 50, 40, 35]
    # цвета для шрифта цифр
    font_color_list = [(255, 255, 255), (0, 141, 255), (18, 212, 117),
                       (0, 25, 156), (158, 0, 214), (10, 175, 155),
                       (255, 138, 0), (15, 71, 180), (36, 255, 0)]

    active_but_color = (255, 255, 255)
    inactive_but_color = (232, 234, 255)
    button_play = Button(190, 65, active_but_color, inactive_but_color)
    button_quit = Button(190, 65, active_but_color, inactive_but_color)

    # указатель окна меню
    MENU_MAIN = 0
    MENU_LEVEL = 1
    MENU_GAME = 2

    # указатель состояния игры, выигрыш, проигрыш или продолжаем играть
    STATE_PLAY = 0
    STATE_WIN = 1
    STATE_LOSE = -1

    menu = MENU_MAIN
    game_render()  # запуск цикла игры
