

---

# NovaEngine

**Версія:** 1.9.2

**Автор:** Minkx1

**Призначення:** Легкий Python-фреймворк на базі PyGame для швидкої розробки 2D-ігор із системою сцен, спрайтів, анімацій, звуком, сейвами та інструментами розробника.

---

## Зміст

1. [Особливості](#особливості)
2. [Встановлення](#встановлення)
3. [Швидкий старт](#швидкий-старт)
4. [Система сцен](#система-сцен)
5. [Класи спрайтів](#класи-спрайтів)
6. [Sprite-like класи та GUI](#sprite-like-класи-та-gui)
7. [Групи спрайтів](#групи-спрайтів)
8. [Час: інтервали, таймери, кулдауни](#час-інтервали-таймери-кулдауни)
9. [Менеджер збережень](#менеджер-збережень)
10. [Менеджер звуку](#менеджер-звуку)
11. [Утиліти](#утиліти)
12. [DevTools](#devtools)
13. [Приклад гри](#приклад-гри)

---

## Особливості

* **Система сцен** — організація логіки ігор через `Scene`, з підтримкою перемикання і відокремленого оновлення.
* **Спрайти** — базовий клас `Sprite` з методами руху, анімації, колізій та трансформацій.
* **Sprite-like класи** — додаткові елементи (`Projectile`, `Dummy`, `ProgressBar`, `TextLabel`, `Button`, `PopUp`).
* **Групи** — колекції спрайтів із масовим оновленням і перевіркою колізій.
* **Час** — клас `nova.Time` для `Timer`, `Cooldown`, `Interval`.
* **Менеджери**:

  * `SoundManager` — звуки та музика.
  * `SaveManager` — прості збереження у JSON.
* **Утиліти** — текст, фон, кольори, прості рендери.
* **DevTools** — збірка `.exe` або архівів для релізу.
* **Оптимізація** та доступ до паралельної обробки.

---

## Встановлення

```bash
pip install pygame
```

* Скопіювати папку **NovaEngine** з репозиторію у папку вашого проекту.
* Імпортувати як модуль:

```python
import NovaEngine as nova
```

---

## Швидкий старт

### Варіант зі сценами

```python
import NovaEngine as nova

Engine = nova.NovaEngine(window_size=(900, 600))
Scene1 = nova.Scene()

with Scene1.sprites():
    text = nova.TextLabel("Hello NovaEngine!", size=40, center=True).place_centred(450, 300)

Engine.run()
```

### Варіант з `@main`

```python
import NovaEngine as nova

Engine = nova.NovaEngine(window_size=(900, 600))

@Engine.main()
def game_loop():
    nova.Utils.fill_background(nova.Colors.WHITE)
    nova.Utils.render_text("Hello NovaEngine!", 450, 300, size=40, center=True)

Engine.run()
```

---

## Система сцен

**Scene** — основний контейнер для об’єктів:

* `with Scene.sprites():` — автоматична реєстрація створених спрайтів.
* `Scene.function()` — декоратор для головної функції сцени.
* `Scene.update()` — оновлення спрайтів.

**Керування сценами:**

```python
nova.Scene.set_active_scene(Menu)
nova.Scene.run_active_scene()
```

---

## Класи спрайтів

**Sprite(engine, img\_path, width=None, height=None, solid=False)**

| Метод                                               | Опис                           |
| --------------------------------------------------- | ------------------------------ |
| `draw()`                                            | Малює спрайт                   |
| `set_update()`                                      | Декоратор для кастомної логіки |
| `set_position(x, y)`                                | Задати координати              |
| `place_centered(x, y)`                              | Центрувати                     |
| `move(dx, dy)`                                      | Рух на відстань                |
| `move_to(target, speed)`                            | Рух до точки/спрайта           |
| `scale(width, height)`                              | Масштабування                  |
| `rotate(angle)`                                     | Поворот                        |
| `look_at(target)`                                   | Повернутись до точки/спрайта   |
| `collide(other/rect)`                               | Колізія                        |
| `kill()`                                            | Видалення                      |
| `set_animation(name, frames, speed=0.1, loop=True)` | Додати анімацію                |
| `play_animation(name=None)`                         | Запустити анімацію             |

---

## Sprite-like класи та GUI

* **Projectile(Sprite)** — прості кулі/снаряди.
* **Dummy(Sprite)** — базовий пустий спрайт для логіки.
* **ProgressBar(Sprite)** — індикатор значень (`set_value()`, `add_value()`).
* **TextLabel(Sprite)** — текстовий елемент.
* **Button(Sprite)** — клікабельна кнопка (`check()`).
* **PopUp** — спливаюче повідомлення.

---

## Групи спрайтів

```python
bullets = nova.Group()
bullets.add(b1, b2)
bullets.update()
hits = bullets.collide(player)
```

---

## Час: інтервали, таймери, кулдауни

**Таймер:**

```python
@nova.Time.Timer(2)
def say_hi():
    print("Hi after 2s")
```

**Кулдаун:**

```python
cooldown1 = nova.Time.Cooldown(0.5)
if cooldown1.check():
    shoot()
    cooldown1.start() # restarts cooldown
```

**Інтервал:**

```python
@nova.Time.Interval(5, 1)
def spawn_enemy():
    print("Enemy!")
```

---

## Менеджер збережень

```python
from NovaEngine import NovaEngine, SaveManager 

app = NovaEngine() # IMPORTANT : all NovaEngine instances MUST be initialised AFTER main engine is initialized

saves = nova.SaveManager(
    appdata=True,
    path="ZombieKillerGame", # In what folder the game-files will be saved
    name="data" # Name of file with data
    )

# strings of varaibles to be saved and loaded
saves.set_vars(["player.money", "Engine.record_time", "player.max_hp"]) 

# if in Engine.run(savemanager=saves), then Engine will autmoticaly load data from file and after finishing progress will save them back 

```

---

## Менеджер звуку

```python
from NovaEngine import SoundManager

sound = SoundManager # class with static methods, NOT object
sound.load_sound("shot", "assets/shot.wav")
sound.play_sound("shot", volume=0.5)

sound.play_music("assets/music.mp3", volume=0.8)
sound.pause_music()
sound.continue_music()
sound.stop_music()
```

---

## Утиліти

```python
nova.Utils.fill_background(nova.Colors.BLACK)
nova.Utils.render_text("Score: 100", 20, 20, size=24)
```

---

## DevTools

**Створення `.exe`:**

```python
nova.DevTools.build_exe(main_file="main.py", name="MyGame", noconsole=True)
```

**Створення архіву:**

```python
nova.DevTools.build_archive(
    main_file="main.py",
    name="MyGame",
    sprite_dir="assets",
    archive_dist="releases"
)
```

---

## Приклад гри

```python
import NovaEngine as nova

Engine = nova.NovaEngine(window_size=(900, 600))
Menu = nova.Scene()
Main = nova.Scene()

with Main.sprites():
    player = nova.Sprite("assets/player.png", 100, 100)
    player.place_centered(450, 300)

    @player.set_update()
    def player_update():
        player.draw()
        player.look_at(nova.Utils.get_mouse_pos())
        if Engine.MouseClicked():
            player.move_angle(50)

with Menu.sprites():
    title = nova.TextLabel("MENU", size=32, center=True).place_centred(450, 250)

@Menu.function()
def _():
    Menu.update()
    if Engine.KeyPressed(pygame.K_m):
        nova.Scene.set_active_scene(Main)

Engine.run(Menu)
```

---


