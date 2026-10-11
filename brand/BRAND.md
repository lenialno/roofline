# roofline · brand

## Цвета

| Роль            | Hex       |
|-----------------|-----------|
| Фон, dark       | `#0E0E0F` |
| Текст, dark     | `#ECEAE6` |
| Фон, light      | `#F5F4F1` |
| Текст, light    | `#151515` |
| Акцент (подъём) | `#D25C55` |

Акцент один для обеих тем. Контраст к фону: 5.0:1 на dark, 3.5:1 на light (для графики достаточно, мелкий текст акцентом не набирать).
Акцентом красится только подъём (memory-bound) вместе со скруглением; полка и wordmark в цвете текста. Ч/б версия: вся линия в цвете текста.

## Шрифт

Geist Medium (500), Vercel, SIL Open Font License 1.1.
https://github.com/vercel/geist-font
Wordmark: «Roofline» с заглавной R (имя пакета остаётся строчным). Трекинг −0.02em. Wordmark в SVG переведён в кривые, шрифт для отображения логотипа не нужен.
OFL разрешает использовать шрифт в логотипах и графике; сами файлы логотипа можно публиковать под MIT. Если кладёте файлы шрифта в репозиторий, они остаются под OFL.

## Геометрия знака

Подъём 45°, подъём : полка = 4 : 7, излом скруглён радиусом 0.625 × подъём, концы круглые.
- Иконка (favicon, аватар, знак отдельно): сетка 16, штрих 2, полка ровно на пиксельной сетке в 16 и 32 px.
- Знак в лого: штрих = стем Geist Medium (0.108 em), верх полки на высоте строчных выносных (0.71 em), низ подъёма на базовой линии. Отступ до слова 0.3 em.

## Файлы

svg/ и png/:
- mark-on-dark / mark-on-light / mark-mono-on-dark / mark-mono-on-light
- wordmark-on-dark / wordmark-on-light
- logo-on-dark / logo-on-light / logo-mono-on-dark / logo-mono-on-light
- favicon.svg (сам переключается по prefers-color-scheme), favicon-16.png, favicon-32.png, apple-touch-icon-180.png
- avatar-512.png, avatar-1024.png (поля рассчитаны и на квадрат, и на круглую обрезку)
- social-preview-1280x640.png
- readme-header-dark/light-1200x400.png (+ @2x)

«on-dark» = для тёмного фона, «on-light» = для светлого. У mark/wordmark/logo фон прозрачный.

## HTML

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32">
<link rel="icon" href="/favicon-16.png" sizes="16x16">
<link rel="apple-touch-icon" href="/apple-touch-icon-180.png">
```

## README

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/png/readme-header-dark-1200x400-2x.png">
  <img alt="roofline" src="brand/png/readme-header-light-1200x400-2x.png" width="1200">
</picture>
```

## Терминал

См. ascii.txt.
