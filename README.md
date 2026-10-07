<div align="center">
  <img src="https://github.com/NastyaNoTamashii/Chromite/blob/main/assets/Chromitel.png" alt="Chromite" width="200" height="200">
  <h1>Chromite</h1>
</div>

<div align="center">

[![GitHub release](https://img.shields.io/github/release/NastyaNoTamashii/Chromite.svg?style=for-the-badge)](https://github.com/NastyaNoTamashii/Chromite/releases/)
[![GitHub license](https://img.shields.io/github/license/NastyaNoTamashii/Chromite.svg?style=for-the-badge)](https://github.com/NastyaNoTamashii/Chromite/blob/main/LICENSE)
[![Pypi downloads](https://img.shields.io/pypi/dm/Chromite?style=for-the-badge&color=pink)](https://pypi.org/project/Chromite/)
[![Commit activity](https://img.shields.io/github/commit-activity/m/NastyaNoTamashii/Chromite?style=for-the-badge)](https://github.com/NastyaNoTamashii/Chromite/)
[![Repo size](https://img.shields.io/github/repo-size/NastyaNoTamashii/Chromite?style=for-the-badge&color=orange)](https://GitHub.com/NastyaNoTamashii/Chromite/)
[![GitHub All Releases](https://img.shields.io/github/downloads/NastyaNoTamashii/Chromite/total?style=for-the-badge)](https://GitHub.com/NastyaNoTamashii/Chromite/releases/)

</div>

## ✨ About
<strong>Chromite</strong> is a lightweight, zero-dependency Python library for building rich terminal user interfaces (TUI). It offers an elegant, object-oriented toolkit for styling output, handling interactive input, and rendering custom UI components.

An optimized library that simplifies writing code and helps with the tasks provided.

## 📦 Installation
 
### Via pip (Recommended)
 
```bash
pip install Chromite
```
 
### From source
 
```bash
git clone https://github.com/NastyaNoTamashii/Chromite
cd Chromite
pip install -e .
```

## 🚀 Quick start

```python
from Chromite import Color, Style, Write

Write("Hello, Chromite!", compose=[Color.Green, Style.Bold]).display()
```

## 🎨 Inline markup

Use `$style$` for colors/styles and `:emoji:` for emoji right inside the text.
`$reset$` clears everything.

```python
from Chromite import Write

Write("$bold$Build passed$reset$ :white_check_mark: $hex#FFFF00$2 warnings$reset$ :warning:").display()
Write("$bg_red$$white$ ERROR $reset$ disk is full").display()
```

## 🌈 Colors

```python
from Chromite import Color, ColorBG, Write

Write("From HEX", compose=Color.hex("#ff5733")).display()
Write("Red background", compose=ColorBG.Red).display()
Write("256-color palette", compose=Color.x256(208)).display()
```

## 📋 Lists

```python
from Chromite import List, Color, Style

List.numbered(
    ["Install", "Import", "Enjoy"],
    compose=Color.Cyan,
    bullet_compose=Style.Bold,
).display()

List.pointed(["fast", "no dependencies"], bullet="→", bullet_compose=Color.Green).display()
```

## 📊 Tables

```python
from Chromite import Table

data = [["Name", "Stars"], {"Chromite": "5", "Other": "10"}]
print(Table.createTable(data, header_separator=True))
```

```
    Name | Stars
---------+------
Chromite |     5
   Other |    10
```

## ⌨️ Input

```python
from Chromite import Read, Color

name = Read("Your name > ", compose=Color.Blue, value_compose=Color.LightBlue).execute()
pin = Read("PIN > ", type="pin").execute()   # also: "password", "hidden", "int"
print(f"Hi {name}!")
```

---

<a href="https://github.com/NastyaNoTamashii/Chromite/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NastyaNoTamashii/Chromite" />
</a>

---
### If a feature doesn't work, check if your console supports it.
---

<div align="center">
Any question? Contact me in discord <code>uwawuwa</code>
<br>
<br>
<p align="center">
  Made with ❤️ by <a href="https://github.com/NastyaNoTamashii">NastyaNoTamashii</a>
</p>
 
[⬆ Back to top](#-Chromite)
 
</div>
