#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
شبیه‌سازی ناحیه H II با استفاده از PyVista

این برنامه یک شبیه‌سازی ساده از ناحیه H II (منطقه هیدروژن یونیزه شده) را با استفاده از PyVista
ایجاد می‌کند. ناحیه H II منطقه‌ای از گاز بسیار رقیق است که در آن هیدروژن به صورت یونیزه وجود دارد.
این نواحی معمولاً در اطراف ستارگان جوان و داغ تشکیل می‌شوند.

نویسنده: عرفان محمدنیا
"""

import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.integrate import quad


class HIIRegion:
    """
    کلاس شبیه‌سازی ناحیه H II

    این کلاس یک مدل ساده از ناحیه H II را شبیه‌سازی می‌کند که شامل:
    - یک ستاره مرکزی به عنوان منبع تابش یونیزه کننده
    - توزیع چگالی گاز هیدروژن
    - محاسبه میزان یونیزاسیون در فواصل مختلف از ستاره
    - تجسم‌سازی نتایج با استفاده از PyVista
    """

    def __init__(self, radius=10.0, resolution=100, star_temperature=40000,
                 star_radius=10.0, density_profile='uniform', density_factor=1.0):
        """
        مقداردهی اولیه کلاس HIIRegion

        پارامترها:
            radius (float): شعاع ناحیه شبیه‌سازی بر حسب پارسک
            resolution (int): تعداد نقاط در هر بعد برای شبکه‌بندی
            star_temperature (float): دمای ستاره مرکزی بر حسب کلوین
            star_radius (float): شعاع ستاره مرکزی بر حسب شعاع خورشید
            density_profile (str): نوع پروفایل چگالی ('uniform', 'exponential', 'power_law')
            density_factor (float): ضریب مقیاس برای چگالی
        """
        self.radius = radius
        self.resolution = resolution
        self.star_temperature = star_temperature
        self.star_radius = star_radius
        self.density_profile = density_profile
        self.density_factor = density_factor

        # ایجاد شبکه سه بعدی
        self.grid = pv.ImageData(
            dimensions=(resolution, resolution, resolution),
            spacing=(2*radius/resolution, 2*radius/resolution, 2*radius/resolution),
            origin=(-radius, -radius, -radius)
        )

        # محاسبه فاصله هر نقطه از مرکز
        x, y, z = np.meshgrid(
            np.linspace(-radius, radius, resolution),
            np.linspace(-radius, radius, resolution),
            np.linspace(-radius, radius, resolution),
            indexing='ij'
        )

        self.distances = np.sqrt(x**2 + y**2 + z**2)

        # محاسبه چگالی گاز
        self.calculate_density()

        # محاسبه میزان یونیزاسیون
        self.calculate_ionization()

        # محاسبه دما
        self.calculate_temperature()

    def calculate_density(self):
        """
        محاسبه توزیع چگالی گاز هیدروژن بر اساس پروفایل انتخاب شده
        """
        if self.density_profile == 'uniform':
            # چگالی یکنواخت
            self.density = np.ones_like(self.distances) * self.density_factor

        elif self.density_profile == 'exponential':
            # چگالی نمایی کاهشی از مرکز
            scale_length = self.radius / 5.0  # طول مشخصه
            self.density = self.density_factor * np.exp(-self.distances / scale_length)

        elif self.density_profile == 'power_law':
            # چگالی با قانون توانی
            power = -2.0  # توان معمول در ابرهای مولکولی
            # اجتناب از تقسیم بر صفر در مرکز
            safe_distances = np.maximum(self.distances, 0.01 * self.radius)
            self.density = self.density_factor * (safe_distances / self.radius) ** power

        else:
            raise ValueError(f"پروفایل چگالی '{self.density_profile}' پشتیبانی نمی‌شود")

        # اضافه کردن چگالی به شبکه
        self.grid.point_data["density"] = self.density.flatten()

    def calculate_ionization(self):
        """
        محاسبه میزان یونیزاسیون در هر نقطه از فضا

        این تابع یک مدل ساده از یونیزاسیون را بر اساس فاصله از ستاره و
        با استفاده از تابع خطای مکمل محاسبه می‌کند.
        """
        # شعاع استرومگرن (شعاع تقریبی ناحیه یونیزه)
        # این مقدار در واقعیت به شار یونیزاسیون ستاره و چگالی محیط بستگی دارد
        stromgren_radius = self.radius / 2.0

        # پهنای لایه انتقالی
        transition_width = stromgren_radius / 10.0

        # محاسبه کسر یونیزاسیون با استفاده از تابع خطای مکمل
        # در فاصله کمتر از شعاع استرومگرن، گاز تقریباً کاملاً یونیزه است
        # و با افزایش فاصله، میزان یونیزاسیون کاهش می‌یابد
        self.ionization_fraction = 0.5 * (1.0 - erf((self.distances - stromgren_radius) / transition_width))

        # اضافه کردن کسر یونیزاسیون به شبکه
        self.grid.point_data["ionization"] = self.ionization_fraction.flatten()

    def calculate_temperature(self):
        """
        محاسبه توزیع دما در ناحیه H II

        دما در ناحیه H II به میزان یونیزاسیون بستگی دارد. در نواحی با یونیزاسیون بالا،
        دما بالاتر است (حدود 10000 کلوین) و در نواحی خنثی، دما پایین‌تر است.
        """
        # دمای ناحیه یونیزه (حدود 10000 کلوین)
        ionized_temp = 10000.0

        # دمای ناحیه خنثی (حدود 100 کلوین)
        neutral_temp = 100.0

        # محاسبه دما بر اساس میزان یونیزاسیون
        self.temperature = neutral_temp + (ionized_temp - neutral_temp) * self.ionization_fraction

        # اضافه کردن دما به شبکه
        self.grid.point_data["temperature"] = self.temperature.flatten()

    def visualize(self, property_name="ionization", cmap="plasma", opacity=0.7,
                  show_star=True, background_color="black", show_boundaries=True,
                  add_dust=True, add_stars=True):
        """
        تجسم‌سازی ناحیه H II با استفاده از PyVista

        پارامترها:
            property_name (str): نام ویژگی برای نمایش ("density", "ionization", "temperature")
            cmap (str): نام نقشه رنگی برای استفاده
            opacity (float): میزان شفافیت نمایش (بین 0 تا 1)
            show_star (bool): آیا ستاره مرکزی نمایش داده شود
            background_color (str): رنگ پس‌زمینه
            show_boundaries (bool): آیا مرزهای ناحیه نمایش داده شود
            add_dust (bool): آیا ذرات غبار به صورت تصادفی اضافه شوند
            add_stars (bool): آیا ستارگان پس‌زمینه اضافه شوند
        """
        # ایجاد پنجره نمایش با قابلیت تعامل
        plotter = pv.Plotter(window_size=[1024, 768])
        plotter.background_color = background_color

        # تنظیم عنوان
        title = f"شبیه‌سازی سه‌بعدی ناحیه H II - {property_name}"
        plotter.add_title(title, font_size=16)

        # اضافه کردن ناحیه H II به صورت حجمی با کیفیت بالاتر
        plotter.add_volume(
            self.grid,
            scalars=property_name,
            cmap=cmap,
            opacity=opacity,
            shade=True,
            ambient=0.3,
            diffuse=0.7,
            specular=0.5,
            specular_power=15
        )

        # اضافه کردن ستاره مرکزی با جلوه نورانی
        if show_star:
            # ستاره اصلی
            star = pv.Sphere(radius=self.radius/20, center=(0, 0, 0))
            plotter.add_mesh(star, color="white", ambient=0.6, specular=1.0, specular_power=15)

            # جلوه نورانی اطراف ستاره
            glow = pv.Sphere(radius=self.radius/15, center=(0, 0, 0))
            plotter.add_mesh(glow, color="yellow", opacity=0.3, ambient=0.8, emissive=True)

        # اضافه کردن مرزهای ناحیه
        if show_boundaries:
            # ایجاد کره برای نمایش مرز تقریبی ناحیه H II (شعاع استرومگرن)
            stromgren_radius = self.radius / 2.0
            boundary = pv.Sphere(radius=stromgren_radius, center=(0, 0, 0))
            plotter.add_mesh(boundary, style='wireframe', color='cyan', opacity=0.3, line_width=1)

        # اضافه کردن ذرات غبار به صورت تصادفی
        if add_dust:
            # تعداد ذرات غبار
            n_dust = 500

            # ایجاد موقعیت‌های تصادفی برای ذرات غبار
            np.random.seed(42)  # برای تکرارپذیری

            # موقعیت‌های تصادفی در فضای کروی
            theta = np.random.uniform(0, 2*np.pi, n_dust)
            phi = np.random.uniform(0, np.pi, n_dust)
            r = np.random.uniform(self.radius/2, self.radius, n_dust)

            # تبدیل به مختصات کارتزین
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)

            # ایجاد نقاط برای ذرات غبار
            dust_points = np.column_stack((x, y, z))
            dust_cloud = pv.PolyData(dust_points)

            # اضافه کردن ذرات غبار با اندازه‌های متفاوت
            plotter.add_points(dust_cloud, color='gray', opacity=0.5, point_size=3, render_points_as_spheres=True)

        # اضافه کردن ستارگان پس‌زمینه
        if add_stars:
            # تعداد ستارگان پس‌زمینه
            n_stars = 1000

            # ایجاد موقعیت‌های تصادفی برای ستارگان
            np.random.seed(123)  # برای تکرارپذیری

            # موقعیت‌های تصادفی در فضای کروی بزرگتر از ناحیه H II
            theta = np.random.uniform(0, 2*np.pi, n_stars)
            phi = np.random.uniform(0, np.pi, n_stars)
            r = np.random.uniform(self.radius*1.5, self.radius*3, n_stars)

            # تبدیل به مختصات کارتزین
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)

            # ایجاد نقاط برای ستارگان
            star_points = np.column_stack((x, y, z))
            background_stars = pv.PolyData(star_points)

            # اندازه‌های متفاوت برای ستارگان که برای رنگ‌آمیزی نیز استفاده می‌شوند
            sizes = np.random.uniform(1, 4, n_stars)

            # اضافه کردن ستارگان پس‌زمینه با رنگ‌های متفاوت بر اساس اندازه
            plotter.add_points(background_stars, scalars=sizes, render_points_as_spheres=True,
                              point_size=3, cmap='coolwarm')

        # اضافه کردن محورهای مختصات برای درک بهتر فضا
        plotter.add_axes(interactive=True, line_width=2)

        # فعال کردن نمایش اطلاعات در گوشه صفحه
        plotter.add_text(
            "برای چرخش: کلیک چپ و حرکت موس\nبرای بزرگنمایی: اسکرول موس\nبرای جابجایی: کلیک راست و حرکت موس",
            position='upper_left',
            font_size=12,
            color='white'
        )

        # نمایش نتیجه با قابلیت تعامل
        plotter.show()

    def create_slice(self, property_name="ionization", cmap="plasma", plane="xy"):
        """
        ایجاد یک برش دوبعدی از ناحیه H II

        پارامترها:
            property_name (str): نام ویژگی برای نمایش ("density", "ionization", "temperature")
            cmap (str): نام نقشه رنگی برای استفاده
            plane (str): صفحه برش ("xy", "xz", "yz")
        """
        # تعیین صفحه برش
        if plane == "xy":
            slice_normal = (0, 0, 1)
            slice_origin = (0, 0, 0)
        elif plane == "xz":
            slice_normal = (0, 1, 0)
            slice_origin = (0, 0, 0)
        elif plane == "yz":
            slice_normal = (1, 0, 0)
            slice_origin = (0, 0, 0)
        else:
            raise ValueError(f"صفحه '{plane}' پشتیبانی نمی‌شود")

        # ایجاد برش
        slice_data = self.grid.slice(normal=slice_normal, origin=slice_origin)

        # ایجاد پنجره نمایش
        plotter = pv.Plotter()
        plotter.background_color = "black"

        # تنظیم عنوان
        title = f"برش {plane} از ناحیه H II - {property_name}"
        plotter.add_title(title, font_size=16)

        # اضافه کردن برش به نمایش
        plotter.add_mesh(slice_data, scalars=property_name, cmap=cmap)

        # نمایش نتیجه
        plotter.show()

    def plot_radial_profile(self, property_name="ionization"):
        """
        رسم نمودار تغییرات یک ویژگی بر حسب فاصله از مرکز

        پارامترها:
            property_name (str): نام ویژگی برای نمایش ("density", "ionization", "temperature")
        """
        # ایجاد آرایه فاصله‌ها برای نمودار
        r = np.linspace(0, self.radius, 1000)

        # محاسبه مقادیر ویژگی در هر فاصله
        if property_name == "density":
            if self.density_profile == 'uniform':
                values = np.ones_like(r) * self.density_factor
            elif self.density_profile == 'exponential':
                scale_length = self.radius / 5.0
                values = self.density_factor * np.exp(-r / scale_length)
            elif self.density_profile == 'power_law':
                safe_r = np.maximum(r, 0.01 * self.radius)
                values = self.density_factor * (safe_r / self.radius) ** (-2.0)

        elif property_name == "ionization":
            stromgren_radius = self.radius / 2.0
            transition_width = stromgren_radius / 10.0
            values = 0.5 * (1.0 - erf((r - stromgren_radius) / transition_width))

        elif property_name == "temperature":
            stromgren_radius = self.radius / 2.0
            transition_width = stromgren_radius / 10.0
            ionization = 0.5 * (1.0 - erf((r - stromgren_radius) / transition_width))
            values = 100.0 + (10000.0 - 100.0) * ionization

        else:
            raise ValueError(f"ویژگی '{property_name}' پشتیبانی نمی‌شود")

        # رسم نمودار
        plt.figure(figsize=(10, 6))
        plt.plot(r, values, 'b-', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.xlabel('فاصله از مرکز (پارسک)', fontsize=12)

        if property_name == "density":
            plt.ylabel('چگالی نسبی', fontsize=12)
            plt.title('پروفایل شعاعی چگالی در ناحیه H II', fontsize=14)
        elif property_name == "ionization":
            plt.ylabel('کسر یونیزاسیون', fontsize=12)
            plt.title('پروفایل شعاعی یونیزاسیون در ناحیه H II', fontsize=14)
        elif property_name == "temperature":
            plt.ylabel('دما (کلوین)', fontsize=12)
            plt.title('پروفایل شعاعی دما در ناحیه H II', fontsize=14)

        plt.tight_layout()
        plt.show()


def main():
    """
    تابع اصلی برنامه
    """
    print("شبیه‌سازی ناحیه H II با استفاده از PyVista")
    print("=" * 50)

    # ایجاد یک نمونه از کلاس HIIRegion با پارامترهای پیش‌فرض
    print("در حال ایجاد مدل ناحیه H II...")
    hii_region = HIIRegion(
        radius=5.0,              # شعاع ناحیه شبیه‌سازی (پارسک)
        resolution=50,           # وضوح شبکه
        star_temperature=40000,  # دمای ستاره (کلوین)
        density_profile='exponential',  # پروفایل چگالی
        density_factor=1.0       # ضریب مقیاس چگالی
    )

    # نمایش پیام
    print("مدل با موفقیت ایجاد شد.")
    print("\nگزینه‌های نمایش:")
    print("1. نمایش سه‌بعدی کامل فضای ناحیه H II (با ستارگان و غبار)")
    print("2. نمایش سه‌بعدی میزان یونیزاسیون")
    print("3. نمایش سه‌بعدی توزیع چگالی")
    print("4. نمایش سه‌بعدی توزیع دما")
    print("5. نمایش برش دوبعدی از میزان یونیزاسیون")
    print("6. نمایش نمودار تغییرات شعاعی یونیزاسیون")
    print("7. نمایش نمودار تغییرات شعاعی چگالی")
    print("8. نمایش نمودار تغییرات شعاعی دما")
    print("0. خروج")

    while True:
        try:
            choice = int(input("\nلطفاً یک گزینه را انتخاب کنید: "))

            if choice == 0:
                print("خروج از برنامه...")
                break

            elif choice == 1:
                print("نمایش سه‌بعدی کامل فضای ناحیه H II...")
                # نمایش کامل با تمام جزئیات
                hii_region.visualize(
                    property_name="ionization",
                    cmap="plasma",
                    opacity=0.6,
                    show_star=True,
                    show_boundaries=True,
                    add_dust=True,
                    add_stars=True
                )

            elif choice == 2:
                print("نمایش سه‌بعدی میزان یونیزاسیون...")
                hii_region.visualize(
                    property_name="ionization",
                    cmap="plasma",
                    show_boundaries=False,
                    add_dust=False,
                    add_stars=False
                )

            elif choice == 3:
                print("نمایش سه‌بعدی توزیع چگالی...")
                hii_region.visualize(
                    property_name="density",
                    cmap="viridis",
                    show_boundaries=False,
                    add_dust=False,
                    add_stars=False
                )

            elif choice == 4:
                print("نمایش سه‌بعدی توزیع دما...")
                hii_region.visualize(
                    property_name="temperature",
                    cmap="inferno",
                    show_boundaries=False,
                    add_dust=False,
                    add_stars=False
                )

            elif choice == 5:
                print("نمایش برش دوبعدی از میزان یونیزاسیون...")
                plane = input("لطفاً صفحه برش را انتخاب کنید (xy/xz/yz): ").lower()
                if plane not in ["xy", "xz", "yz"]:
                    print("صفحه نامعتبر! از xy استفاده می‌شود.")
                    plane = "xy"
                hii_region.create_slice(property_name="ionization", plane=plane)

            elif choice == 6:
                print("نمایش نمودار تغییرات شعاعی یونیزاسیون...")
                hii_region.plot_radial_profile(property_name="ionization")

            elif choice == 7:
                print("نمایش نمودار تغییرات شعاعی چگالی...")
                hii_region.plot_radial_profile(property_name="density")

            elif choice == 8:
                print("نمایش نمودار تغییرات شعاعی دما...")
                hii_region.plot_radial_profile(property_name="temperature")

            else:
                print("گزینه نامعتبر! لطفاً یک گزینه معتبر وارد کنید.")

        except ValueError:
            print("ورودی نامعتبر! لطفاً یک عدد وارد کنید.")

        except Exception as e:
            print(f"خطا: {e}")


if __name__ == "__main__":
    main()
