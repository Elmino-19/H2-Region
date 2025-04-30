#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
تجسم‌سازی ساده سه‌بعدی فضای ستاره‌ای و ناحیه H II

این برنامه یک تجسم‌سازی سه‌بعدی ساده از فضای ستاره‌ای و ناحیه H II ارائه می‌دهد.

نویسنده: عرفان محمدنیا
"""

import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt


class SimpleSpaceVisualization:
    """
    کلاس تجسم‌سازی ساده سه‌بعدی فضای ستاره‌ای
    """
    
    def __init__(self, universe_radius=100.0, hii_radius=20.0, n_stars=2000, n_dust=1000):
        """
        مقداردهی اولیه کلاس SimpleSpaceVisualization
        
        پارامترها:
            universe_radius (float): شعاع کلی فضای شبیه‌سازی شده
            hii_radius (float): شعاع ناحیه H II
            n_stars (int): تعداد ستارگان پس‌زمینه
            n_dust (int): تعداد ذرات غبار
        """
        self.universe_radius = universe_radius
        self.hii_radius = hii_radius
        self.n_stars = n_stars
        self.n_dust = n_dust
        
        # ایجاد پلاتر PyVista
        self.plotter = pv.Plotter(window_size=[1024, 768])
        self.plotter.background_color = 'black'
        
        # ایجاد اجزای صحنه
        self._create_stars()
        self._create_central_star()
        self._create_hii_region()
        self._create_dust()
        
        # اضافه کردن راهنما
        self._add_instructions()
    
    def _create_stars(self):
        """
        ایجاد ستارگان پس‌زمینه
        """
        # ایجاد موقعیت‌های تصادفی برای ستارگان
        np.random.seed(42)  # برای تکرارپذیری
        
        # موقعیت‌های تصادفی در فضای کروی
        theta = np.random.uniform(0, 2*np.pi, self.n_stars)
        phi = np.random.uniform(0, np.pi, self.n_stars)
        r = np.random.uniform(self.hii_radius*1.5, self.universe_radius, self.n_stars)
        
        # تبدیل به مختصات کارتزین
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # ایجاد نقاط برای ستارگان
        star_points = np.column_stack((x, y, z))
        background_stars = pv.PolyData(star_points)
        
        # اندازه‌های متفاوت برای ستارگان
        sizes = np.random.uniform(1, 4, self.n_stars)
        
        # اضافه کردن ستارگان به صحنه
        self.plotter.add_points(background_stars, scalars=sizes, render_points_as_spheres=True, 
                               point_size=2, cmap='coolwarm')
    
    def _create_central_star(self):
        """
        ایجاد ستاره مرکزی
        """
        # ستاره اصلی
        central_star = pv.Sphere(radius=self.hii_radius/20, center=(0, 0, 0))
        self.plotter.add_mesh(central_star, color="yellow")
        
        # جلوه نورانی اطراف ستاره
        glow = pv.Sphere(radius=self.hii_radius/15, center=(0, 0, 0))
        self.plotter.add_mesh(glow, color="yellow", opacity=0.3)
    
    def _create_hii_region(self):
        """
        ایجاد ناحیه H II
        """
        # ایجاد یک کره برای نمایش مرز تقریبی ناحیه H II
        hii_boundary = pv.Sphere(radius=self.hii_radius, center=(0, 0, 0))
        
        # اضافه کردن ناحیه H II به صحنه
        self.plotter.add_mesh(hii_boundary, opacity=0.2, color="cyan", style='wireframe')
        
        # اضافه کردن ساختارهای داخلی ناحیه H II
        self._add_internal_structures()
    
    def _add_internal_structures(self):
        """
        اضافه کردن ساختارهای داخلی به ناحیه H II
        """
        # تعداد ساختارهای داخلی
        n_structures = 5
        
        # ایجاد ساختارهای ابری داخلی
        for i in range(n_structures):
            # موقعیت تصادفی درون ناحیه H II
            r = np.random.uniform(0, self.hii_radius * 0.8)
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            # اندازه تصادفی
            size = np.random.uniform(self.hii_radius/10, self.hii_radius/5)
            
            # ایجاد یک ساختار ابری (استفاده از کره)
            structure = pv.Sphere(radius=size, center=(x, y, z))
            
            # اضافه کردن ساختار به صحنه
            opacity = np.random.uniform(0.1, 0.3)
            color = 'cyan'
            
            self.plotter.add_mesh(structure, opacity=opacity, color=color)
    
    def _create_dust(self):
        """
        ایجاد ذرات غبار در اطراف ناحیه H II
        """
        # ایجاد موقعیت‌های تصادفی برای ذرات غبار
        np.random.seed(123)  # برای تکرارپذیری
        
        # موقعیت‌های تصادفی در فضای کروی
        theta = np.random.uniform(0, 2*np.pi, self.n_dust)
        phi = np.random.uniform(0, np.pi, self.n_dust)
        r = np.random.uniform(self.hii_radius*0.9, self.hii_radius*1.3, self.n_dust)
        
        # تبدیل به مختصات کارتزین
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # ایجاد نقاط برای ذرات غبار
        dust_points = np.column_stack((x, y, z))
        dust_cloud = pv.PolyData(dust_points)
        
        # اضافه کردن ذرات غبار به صحنه
        self.plotter.add_points(dust_cloud, color='gray', opacity=0.5, point_size=2, 
                               render_points_as_spheres=True)
    
    def _add_instructions(self):
        """
        اضافه کردن راهنمای کاربری به صحنه
        """
        instructions = (
            "راهنمای کاربری:\n"
            "- چرخش: کلیک چپ و حرکت موس\n"
            "- بزرگنمایی: اسکرول موس\n"
            "- جابجایی: کلیک راست و حرکت موس\n"
            "- خروج: کلید ESC"
        )
        
        self.plotter.add_text(instructions, position='upper_left', font_size=12, color='white')
    
    def show(self):
        """
        نمایش صحنه به صورت تعاملی
        """
        # تنظیم عنوان
        self.plotter.add_title("تجسم‌سازی سه‌بعدی ناحیه H II", font_size=16)
        
        # نمایش صحنه
        self.plotter.show()


def create_nebula_visualization():
    """
    ایجاد یک تجسم‌سازی ساده‌تر از سحابی با استفاده از نقاط
    """
    # ایجاد پلاتر
    plotter = pv.Plotter(window_size=[1024, 768])
    plotter.background_color = 'black'
    
    # تعداد نقاط
    n_points = 10000
    
    # ایجاد نقاط تصادفی در یک شکل کروی
    np.random.seed(42)
    theta = np.random.uniform(0, 2*np.pi, n_points)
    phi = np.random.uniform(0, np.pi, n_points)
    
    # توزیع شعاعی با تمرکز بیشتر در لبه‌ها
    r = 20 * np.random.beta(2, 2, n_points)
    
    # تبدیل به مختصات کارتزین
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    
    # اضافه کردن اغتشاش به موقعیت‌ها برای ایجاد ظاهر ابری
    x += np.random.normal(0, 2, n_points)
    y += np.random.normal(0, 2, n_points)
    z += np.random.normal(0, 2, n_points)
    
    # ایجاد نقاط برای سحابی
    points = np.column_stack((x, y, z))
    cloud = pv.PolyData(points)
    
    # محاسبه فاصله از مرکز برای رنگ‌آمیزی
    distances = np.sqrt(x**2 + y**2 + z**2)
    
    # اضافه کردن سحابی به صحنه
    plotter.add_points(cloud, scalars=distances, cmap='coolwarm', 
                      render_points_as_spheres=True, point_size=5, opacity=0.5)
    
    # اضافه کردن ستاره مرکزی
    star = pv.Sphere(radius=1, center=(0, 0, 0))
    plotter.add_mesh(star, color="yellow")
    
    # اضافه کردن راهنما
    instructions = (
        "راهنمای کاربری:\n"
        "- چرخش: کلیک چپ و حرکت موس\n"
        "- بزرگنمایی: اسکرول موس\n"
        "- جابجایی: کلیک راست و حرکت موس\n"
        "- خروج: کلید ESC"
    )
    plotter.add_text(instructions, position='upper_left', font_size=12, color='white')
    
    # تنظیم عنوان
    plotter.add_title("تجسم‌سازی سه‌بعدی سحابی", font_size=16)
    
    # نمایش صحنه
    plotter.show()


def main():
    """
    تابع اصلی برنامه
    """
    print("تجسم‌سازی سه‌بعدی فضای ستاره‌ای و ناحیه H II")
    print("=" * 50)
    
    # نمایش منو
    print("\nگزینه‌های نمایش:")
    print("1. نمایش فضای ستاره‌ای و ناحیه H II")
    print("2. نمایش سحابی ساده")
    print("0. خروج")
    
    while True:
        try:
            choice = int(input("\nلطفاً یک گزینه را انتخاب کنید: "))
            
            if choice == 0:
                print("خروج از برنامه...")
                break
            
            elif choice == 1:
                print("در حال بارگذاری نمایش فضای ستاره‌ای و ناحیه H II...")
                visualization = SimpleSpaceVisualization(
                    universe_radius=100.0,
                    hii_radius=20.0,
                    n_stars=2000,
                    n_dust=1000
                )
                visualization.show()
            
            elif choice == 2:
                print("در حال بارگذاری نمایش سحابی ساده...")
                create_nebula_visualization()
            
            else:
                print("گزینه نامعتبر! لطفاً یک گزینه معتبر وارد کنید.")
        
        except ValueError:
            print("ورودی نامعتبر! لطفاً یک عدد وارد کنید.")
        
        except Exception as e:
            print(f"خطا: {e}")


if __name__ == "__main__":
    main()
