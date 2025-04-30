# H II Region Visualization | تجسم‌سازی ناحیه H II

A 3D visualization tool for H II regions using Streamlit and PyVista.

یک ابزار تجسم‌سازی سه‌بعدی برای نواحی H II با استفاده از Streamlit و PyVista.

## Introduction | مقدمه

H II regions are areas of ionized hydrogen gas, typically found around young, hot stars that emit strong ultraviolet radiation capable of ionizing hydrogen atoms.

ناحیه H II منطقه‌ای از گاز بسیار رقیق است که در آن هیدروژن به صورت یونیزه وجود دارد. این نواحی معمولاً در اطراف ستارگان جوان و داغ تشکیل می‌شوند که تابش فرابنفش شدیدی دارند و می‌توانند اتم‌های هیدروژن را یونیزه کنند.

## Features | ویژگی‌ها

This visualization includes:

- Interactive 3D visualization with Streamlit
- Adjustable parameters (star temperature, density profile, etc.)
- Real-time updates of the model
- Visualization of different properties (ionization, density, temperature)
- Star color changes based on temperature
- Stromgren radius adjusts based on star temperature
- Modeling gas density distribution with different profiles (uniform, exponential, power law)
- Calculation of ionization levels at different distances from the central star
- Temperature distribution calculation in the H II region
- Radial profile plots of various properties

این تجسم‌سازی شامل موارد زیر است:

- تجسم‌سازی سه‌بعدی تعاملی با Streamlit
- پارامترهای قابل تنظیم (دمای ستاره، پروفایل چگالی و غیره)
- به‌روزرسانی مدل در زمان واقعی
- تجسم‌سازی ویژگی‌های مختلف (یونیزاسیون، چگالی، دما)
- تغییر رنگ ستاره بر اساس دما
- تنظیم شعاع استرومگرن بر اساس دمای ستاره
- مدل‌سازی توزیع چگالی گاز با پروفایل‌های مختلف (یکنواخت، نمایی، قانون توانی)
- محاسبه میزان یونیزاسیون در فواصل مختلف از ستاره مرکزی
- محاسبه توزیع دما در ناحیه H II
- رسم نمودارهای تغییرات شعاعی ویژگی‌های مختلف

## Requirements | نیازمندی‌ها

To run this visualization, you need the following libraries:

```
numpy
scipy
matplotlib
pyvista
streamlit
stpyvista
```

You can install these libraries using:

```bash
pip install numpy scipy matplotlib pyvista streamlit stpyvista
```

برای اجرای این تجسم‌سازی به کتابخانه‌های زیر نیاز دارید:

```
numpy
scipy
matplotlib
pyvista
streamlit
stpyvista
```

می‌توانید این کتابخانه‌ها را با استفاده از دستور زیر نصب کنید:

```bash
pip install numpy scipy matplotlib pyvista streamlit stpyvista
```

## Usage | نحوه استفاده

To run the visualization, execute:

```bash
streamlit run hii_region_streamlit.py
```

This will open a web interface where you can interact with the 3D model and adjust various parameters.

برای اجرای تجسم‌سازی، دستور زیر را اجرا کنید:

```bash
streamlit run hii_region_streamlit.py
```

این دستور یک رابط وب باز می‌کند که می‌توانید با مدل سه‌بعدی تعامل داشته باشید و پارامترهای مختلف را تنظیم کنید.

## Physical Concepts | مفاهیم فیزیکی

### Stromgren Radius | شعاع استرومگرن

The Stromgren radius is the approximate radius of the ionized region around a star. This radius depends on the star's ionizing photon flux and the density of the surrounding environment, calculated using:

شعاع استرومگرن، شعاع تقریبی ناحیه یونیزه در اطراف یک ستاره است. این شعاع به شار فوتون‌های یونیزه‌کننده ستاره و چگالی محیط اطراف بستگی دارد و از رابطه زیر محاسبه می‌شود:

R_s = (3 * Q_0 / (4 * π * n_H^2 * α_B))^(1/3)

Where:
- Q_0: Number of ionizing photons emitted by the star per unit time
- n_H: Hydrogen atom density
- α_B: Recombination coefficient

که در آن:
- Q_0: تعداد فوتون‌های یونیزه‌کننده منتشر شده توسط ستاره در واحد زمان
- n_H: چگالی اتم‌های هیدروژن
- α_B: ضریب بازترکیب

### Transition Layer | لایه انتقالی

At the boundary of the H II region, there is a transition layer where the ionization level decreases from nearly 100% to zero. The thickness of this layer depends on the mean free path of ionizing photons.

در مرز ناحیه H II، یک لایه انتقالی وجود دارد که در آن میزان یونیزاسیون از تقریباً 100% به صفر کاهش می‌یابد. ضخامت این لایه به میانگین مسیر آزاد فوتون‌های یونیزه‌کننده بستگی دارد.

### Star Temperature and Color | دمای ستاره و رنگ

The temperature of a star determines its color:
- O stars: 30,000 - 50,000 K (blue)
- B stars: 10,000 - 30,000 K (blue-white)
- A stars: 7,500 - 10,000 K (white)
- F stars: 6,000 - 7,500 K (yellow-white)
- G stars: 5,000 - 6,000 K (yellow) - like our Sun
- K stars: 3,500 - 5,000 K (orange)
- M stars: 2,000 - 3,500 K (red)

In this visualization, the star's color changes based on the temperature you set, following the blackbody radiation principles.

دمای ستاره رنگ آن را تعیین می‌کند:
- ستارگان نوع O: 30,000 - 50,000 کلوین (آبی)
- ستارگان نوع B: 10,000 - 30,000 کلوین (آبی-سفید)
- ستارگان نوع A: 7,500 - 10,000 کلوین (سفید)
- ستارگان نوع F: 6,000 - 7,500 کلوین (زرد-سفید)
- ستارگان نوع G: 5,000 - 6,000 کلوین (زرد) - مانند خورشید ما
- ستارگان نوع K: 3,500 - 5,000 کلوین (نارنجی)
- ستارگان نوع M: 2,000 - 3,500 کلوین (قرمز)

در این تجسم‌سازی، رنگ ستاره بر اساس دمایی که تنظیم می‌کنید، مطابق با اصول تابش جسم سیاه تغییر می‌کند.

## Author | نویسنده

Erfan Mohamadnia | عرفان محمدنیا
