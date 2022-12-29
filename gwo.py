"""
Лабораторная работа Сиренко В. Н.
ИИС-Tg21

Стая волков по книге

"""


from random import uniform
import numpy as np
from numpy import arange
from numpy import meshgrid
from matplotlib import pyplot


# Защита от выхода за границу
borderPadding = 0.5


# Волк, умеет хранить свои координаты, рождаться и расчитывать свою позицию в фитнесс функции
class Wolf():
    def __init__(self, settings):
        self.settings = settings
        self.posX = None
        self.posY = None
        self.fitnessResult = None
        self.burnWolfPosition()
        self.calculateFitness()

    # Инициирует позицию волка после его рождения
    def burnWolfPosition(self):
        self.posX = uniform(self.settings.testFunction.getMinX()+borderPadding,
                            self.settings.testFunction.getMaxX()-borderPadding)

        self.posY = uniform(self.settings.testFunction.getMinX()+borderPadding,
                            self.settings.testFunction.getMaxX()-borderPadding)

    # Расчитывает значение фитнесс функции
    def calculateFitness(self):
        self.fitnessResult = self.settings.testFunction.calculateZ(self.posX, self.posY)


# Стая
class Flock:
    def __init__(self, settings):
        self.wolfs = []
        self.settings = settings
        self.iteration = settings.iteration

        # Позиции волков для отрисовки
        self.toDrawByStepXYCoordsOmega = []
        self.toDrawByStepXYCoordsAlpha = []
        self.toDrawByStepXYCoordsBetta = []
        self.toDrawByStepXYCoordsGamma = []

    def run(self):
        # Рождаем волков
        self.wolfs = [Wolf(self.settings) for x in range(self.settings.populationSize)]
        self.bestParticles = []

        # Эпохи
        for i in range(self.iteration):
            # Сортируем по лучшей позиции
            self.wolfs.sort(key=lambda x: x.fitnessResult)

            # Лучшие 3 волка
            alpha = self.wolfs[0]
            betta = self.wolfs[1]
            gamma = self.wolfs[2]

            # Добавляем координаты для отслеживания лучших
            self.toDrawByStepXYCoordsAlpha.append((alpha.posX, alpha.posY))
            self.toDrawByStepXYCoordsBetta.append((betta.posX, betta.posY))
            self.toDrawByStepXYCoordsGamma.append((gamma.posX, gamma.posY))

            # Компонент а служит для уменьшения (сужения круга волков вокруг добычи) с каждой итерацией
            a = 2 - (2 * i / self.settings.iteration)

            # Случайные компоненты разыгрываются для каждой итерации алгоритма
            r1XY = (uniform(0, 1), uniform(0, 1))
            r2XY = (uniform(0, 1), uniform(0, 1))

            # Расчетные компоненты A C для координат XY
            AXY = (2 * a * r1XY[0] - a,  2 * a * r1XY[1] - a)
            CXY = (2 * r2XY[0], 2 * r2XY[1])

            # Делаем операции над каждым волком
            for iWolf, wolf in enumerate(self.wolfs):
                # позиция по модулю для расчета движения волка
                posAbsAlphaX = abs(CXY[0] * alpha.posX - wolf.posX)
                posAbsAlphaY = abs(CXY[1] * alpha.posY - wolf.posY)

                posAbsBettaX = abs(CXY[0] * betta.posX - wolf.posX)
                posAbsBettaY = abs(CXY[1] * betta.posY - wolf.posY)

                posAbsGammaX = abs(CXY[0] * gamma.posX - wolf.posX)
                posAbsGammaY = abs(CXY[1] * gamma.posY - wolf.posY)

                # Рассчетные координаты волка по позициям трех волков
                x1 = alpha.posX - AXY[0] * posAbsAlphaX
                y1 = alpha.posY - AXY[1] * posAbsAlphaY

                x2 = betta.posX - AXY[0] * posAbsBettaX
                y2 = betta.posY - AXY[1] * posAbsBettaY

                x3 = gamma.posX - AXY[0] * posAbsGammaX
                y3 = gamma.posY - AXY[1] * posAbsGammaY

                # Высчитываем конечный вектор позиции
                unboundedWolfPosX = (x1+x2+x3) / 3
                unboundedWolfPosY = (y1+y2+y3) / 3

                # Функция для расчета того, чтобы позиция не выходила за рамки поля
                def keep_in_bounds(x, min_x, max_x):
                    global borderPadding
                    if x < min_x + borderPadding:
                        return min_x + borderPadding
                    elif x > max_x - borderPadding:
                        return max_x - borderPadding
                    else:
                        return x

                # Делаем так, чтобы волк не вышил за рамки фитнесс функции
                self.wolfs[iWolf].posX = keep_in_bounds(unboundedWolfPosX,
                                                    self.settings.testFunction.getMinX(),
                                                    self.settings.testFunction.getMaxX())
                self.wolfs[iWolf].posY = keep_in_bounds(unboundedWolfPosY,
                                                    self.settings.testFunction.getMinY(),
                                                    self.settings.testFunction.getMaxY())

                # Считаем фитнесс функцию
                self.wolfs[iWolf].calculateFitness()

            # Добавляем координаты отслеживания позиции Волков для отображения
            self.toDrawByStepXYCoordsOmega.append({"x": [], "y": []})
            for wolf in self.wolfs:
                self.toDrawByStepXYCoordsOmega[-1]["x"].append(wolf.posX)
                self.toDrawByStepXYCoordsOmega[-1]["y"].append(wolf.posY)

            print("ЭПОХА:", i, " Лучшая позиция X: ", alpha.posX, "Y: ", alpha.posY, "Фитнесс: ", alpha.fitnessResult)

    def drawInitArea(self):
        # Просто отрисовывает первоначальное состояние поля (тестовой функции)
        xaxis = arange(self.settings.testFunction.getMinX(),
                       self.settings.testFunction.getMaxX(), 0.1)
        yaxis = arange(self.settings.testFunction.getMinY(),
                       self.settings.testFunction.getMaxY(), 0.1)
        x, y = meshgrid(xaxis, yaxis)
        results = self.settings.testFunction.calculateZ(x, y)
        figure = pyplot.figure(figsize=(8, 7))
        axis = figure.add_subplot(projection='3d')

        axis.plot_surface(x, y, results, cmap='jet')
        return figure

    def drawHromoByStep(self, step):
        # А это отрисовывает состояние в зависимости от заданного шага
        fig = pyplot.figure(figsize=(8, 7))
        left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
        ax = fig.add_axes([left, bottom, width, height])
        ax.set_title("2D Пространство")

        xaxis = arange(self.settings.testFunction.getMinX(),
                       self.settings.testFunction.getMaxX(), 0.1)
        yaxis = arange(self.settings.testFunction.getMinY(),
                       self.settings.testFunction.getMaxY(), 0.1)
        x, y = meshgrid(xaxis, yaxis)
        results = self.settings.testFunction.calculateZ(x, y)
        if self.settings.testFunction.getLevels() > 0:
            cp = pyplot.contourf(x, y, results, levels=np.linspace(0,
                                                                   self.settings.testFunction.getLevels(),
                                                                   50))
        else:
            cp = pyplot.contourf(x, y, results, levels=np.linspace(self.settings.testFunction.getLevels(),
                                                                   0,
                                                                   50))
        pyplot.colorbar(cp)


        # Обычные волки
        if step < len(self.toDrawByStepXYCoordsOmega):
            pyplot.scatter(self.toDrawByStepXYCoordsOmega[step]["x"], self.toDrawByStepXYCoordsOmega[step]["y"],
                           s=3, c="gray"
                           )
        # лучшие волки
        # Альфа - красный, дельта - синий, гамма - зеленый
        pyplot.scatter(self.toDrawByStepXYCoordsAlpha[step][0], self.toDrawByStepXYCoordsAlpha[step][1],
                       s=6, c="red", alpha=0.6)
        pyplot.scatter(self.toDrawByStepXYCoordsBetta[step][0], self.toDrawByStepXYCoordsBetta[step][1],
                       s=6, c="blue", alpha=0.6)
        pyplot.scatter(self.toDrawByStepXYCoordsGamma[step][0], self.toDrawByStepXYCoordsGamma[step][1],
                       s=6, c="green", alpha=0.6)

        return fig