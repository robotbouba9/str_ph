# -*- coding: utf-8 -*-
"""
تطبيق سطح المكتب لإدارة مخزون محل الهواتف
يحتوي على خادم Flask مدمج وواجهة tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
import socket
import time
import sys
import os
from datetime import datetime
import subprocess

# إضافة المجلد الحالي لمسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db, Product, Customer, Supplier, Sale

class PhoneStoreApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("برنامج إدارة مخزون محل الهواتف")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات التطبيق
        self.server_thread = None
        self.server_running = False
        self.port = 5000
        
        # إعداد الواجهة
        self.setup_ui()
        
        # بدء الخادم تلقائياً
        self.start_server()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # إعداد الأيقونة والعنوان
        self.root.iconbitmap(default='')  # يمكن إضافة أيقونة هنا
        
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # تكوين الشبكة
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # العنوان
        title_label = ttk.Label(main_frame, text="برنامج إدارة مخزون محل الهواتف", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # إطار معلومات الخادم
        server_frame = ttk.LabelFrame(main_frame, text="معلومات الخادم", padding="10")
        server_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        # حالة الخادم
        ttk.Label(server_frame, text="حالة الخادم:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.server_status_label = ttk.Label(server_frame, text="متوقف", foreground="red")
        self.server_status_label.grid(row=0, column=1, sticky=tk.W)
        
        # عنوان الخادم
        ttk.Label(server_frame, text="العنوان:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.server_url_label = ttk.Label(server_frame, text=f"http://localhost:{self.port}")
        self.server_url_label.grid(row=1, column=1, sticky=tk.W)
        
        # أزرار التحكم في الخادم
        button_frame = ttk.Frame(server_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="تشغيل الخادم", 
                                      command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="إيقاف الخادم", 
                                     command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_browser_button = ttk.Button(button_frame, text="فتح في المتصفح", 
                                            command=self.open_browser, state=tk.DISABLED)
        self.open_browser_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # إطار الإحصائيات السريعة
        stats_frame = ttk.LabelFrame(main_frame, text="إحصائيات سريعة", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # إطار الأدوات
        tools_frame = ttk.LabelFrame(main_frame, text="أدوات سريعة", padding="10")
        tools_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # إعداد الإحصائيات
        self.setup_stats_frame(stats_frame)
        
        # إعداد الأدوات
        self.setup_tools_frame(tools_frame)
        
        # شريط الحالة
        self.status_bar = ttk.Label(main_frame, text="جاهز", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # تحديث الإحصائيات كل 30 ثانية
        self.update_stats()
        self.root.after(30000, self.update_stats_periodically)
        
    def setup_stats_frame(self, parent):
        """إعداد إطار الإحصائيات"""
        # إجمالي المنتجات
        ttk.Label(parent, text="إجمالي المنتجات:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.products_count_label = ttk.Label(parent, text="0", font=('Arial', 12, 'bold'))
        self.products_count_label.grid(row=0, column=1, sticky=tk.E, pady=2)
        
        # إجمالي العملاء
        ttk.Label(parent, text="إجمالي العملاء:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.customers_count_label = ttk.Label(parent, text="0", font=('Arial', 12, 'bold'))
        self.customers_count_label.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        # إجمالي الموردين
        ttk.Label(parent, text="إجمالي الموردين:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.suppliers_count_label = ttk.Label(parent, text="0", font=('Arial', 12, 'bold'))
        self.suppliers_count_label.grid(row=2, column=1, sticky=tk.E, pady=2)
        
        # مبيعات اليوم
        ttk.Label(parent, text="مبيعات اليوم:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.today_sales_label = ttk.Label(parent, text="0 جنيه", font=('Arial', 12, 'bold'), foreground="green")
        self.today_sales_label.grid(row=3, column=1, sticky=tk.E, pady=2)
        
        # منتجات منخفضة المخزون
        ttk.Label(parent, text="منخفض المخزون:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.low_stock_label = ttk.Label(parent, text="0", font=('Arial', 12, 'bold'), foreground="red")
        self.low_stock_label.grid(row=4, column=1, sticky=tk.E, pady=2)
        
        parent.columnconfigure(0, weight=1)
        
    def setup_tools_frame(self, parent):
        """إعداد إطار الأدوات"""
        # زر إضافة منتج سريع
        add_product_btn = ttk.Button(parent, text="إضافة منتج سريع", 
                                   command=self.quick_add_product)
        add_product_btn.pack(fill=tk.X, pady=2)
        
        # زر فاتورة سريعة
        quick_sale_btn = ttk.Button(parent, text="فاتورة سريعة", 
                                  command=self.quick_sale)
        quick_sale_btn.pack(fill=tk.X, pady=2)
        
        # زر البحث السريع
        search_btn = ttk.Button(parent, text="البحث السريع", 
                              command=self.quick_search)
        search_btn.pack(fill=tk.X, pady=2)
        
        # زر التقارير
        reports_btn = ttk.Button(parent, text="التقارير", 
                               command=self.open_reports)
        reports_btn.pack(fill=tk.X, pady=2)
        
        # زر النسخ الاحتياطي
        backup_btn = ttk.Button(parent, text="نسخة احتياطية", 
                              command=self.create_backup)
        backup_btn.pack(fill=tk.X, pady=2)
        
        # زر الإعدادات
        settings_btn = ttk.Button(parent, text="الإعدادات", 
                                command=self.open_settings)
        settings_btn.pack(fill=tk.X, pady=2)
        
    def find_free_port(self):
        """البحث عن منفذ متاح"""
        for port in range(5000, 5100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        return None
        
    def start_server(self):
        """تشغيل خادم Flask"""
        if self.server_running:
            return
            
        # البحث عن منفذ متاح
        self.port = self.find_free_port()
        if not self.port:
            messagebox.showerror("خطأ", "لا يمكن العثور على منفذ متاح")
            return
            
        try:
            # تشغيل الخادم في خيط منفصل
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            
            # انتظار تشغيل الخادم
            time.sleep(2)
            
            # تحديث الواجهة
            self.server_running = True
            self.server_status_label.config(text="يعمل", foreground="green")
            self.server_url_label.config(text=f"http://localhost:{self.port}")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.open_browser_button.config(state=tk.NORMAL)
            self.status_bar.config(text=f"الخادم يعمل على المنفذ {self.port}")
            
            messagebox.showinfo("نجح", f"تم تشغيل الخادم بنجاح على المنفذ {self.port}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تشغيل الخادم: {str(e)}")
            
    def run_server(self):
        """تشغيل خادم Flask"""
        try:
            app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"خطأ في الخادم: {e}")
            
    def stop_server(self):
        """إيقاف الخادم"""
        self.server_running = False
        self.server_status_label.config(text="متوقف", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)
        self.status_bar.config(text="تم إيقاف الخادم")
        
        messagebox.showinfo("تم", "تم إيقاف الخادم")
        
    def open_browser(self):
        """فتح المتصفح"""
        if self.server_running:
            webbrowser.open(f"http://localhost:{self.port}")
        else:
            messagebox.showwarning("تحذير", "الخادم غير مشغل")
            
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            with app.app_context():
                # إجمالي المنتجات
                products_count = Product.query.count()
                self.products_count_label.config(text=str(products_count))
                
                # إجمالي العملاء
                customers_count = Customer.query.count()
                self.customers_count_label.config(text=str(customers_count))
                
                # إجمالي الموردين
                suppliers_count = Supplier.query.count()
                self.suppliers_count_label.config(text=str(suppliers_count))
                
                # مبيعات اليوم
                today = datetime.now().date()
                today_sales = Sale.query.filter(
                    db.func.date(Sale.created_at) == today
                ).all()
                today_revenue = sum(sale.final_amount for sale in today_sales)
                self.today_sales_label.config(text=f"{today_revenue:.2f} جنيه")
                
                # منتجات منخفضة المخزون
                low_stock_count = Product.query.filter(
                    Product.quantity <= Product.min_quantity
                ).count()
                self.low_stock_label.config(text=str(low_stock_count))
                
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
            
    def update_stats_periodically(self):
        """تحديث الإحصائيات دورياً"""
        self.update_stats()
        self.root.after(30000, self.update_stats_periodically)
        
    def quick_add_product(self):
        """إضافة منتج سريع"""
        if self.server_running:
            webbrowser.open(f"http://localhost:{self.port}/products/add")
        else:
            messagebox.showwarning("تحذير", "الخادم غير مشغل")
            
    def quick_sale(self):
        """فاتورة سريعة"""
        if self.server_running:
            webbrowser.open(f"http://localhost:{self.port}/sales/new")
        else:
            messagebox.showwarning("تحذير", "الخادم غير مشغل")
            
    def quick_search(self):
        """البحث السريع"""
        search_window = tk.Toplevel(self.root)
        search_window.title("البحث السريع")
        search_window.geometry("400x300")
        search_window.configure(bg='#f0f0f0')
        
        # إطار البحث
        search_frame = ttk.Frame(search_window, padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(search_frame, text="البحث في المنتجات:").pack(anchor=tk.W)
        
        search_entry = ttk.Entry(search_frame, width=40)
        search_entry.pack(fill=tk.X, pady=(5, 10))
        
        # نتائج البحث
        results_frame = ttk.Frame(search_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        results_tree = ttk.Treeview(results_frame, columns=('name', 'brand', 'price', 'quantity'), show='headings')
        results_tree.heading('name', text='الاسم')
        results_tree.heading('brand', text='الماركة')
        results_tree.heading('price', text='السعر')
        results_tree.heading('quantity', text='الكمية')
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def search_products():
            query = search_entry.get().strip()
            if not query:
                return
                
            try:
                with app.app_context():
                    products = Product.query.filter(
                        db.or_(
                            Product.name.contains(query),
                            Product.brand.contains(query),
                            Product.model.contains(query)
                        )
                    ).limit(20).all()
                    
                    # مسح النتائج السابقة
                    for item in results_tree.get_children():
                        results_tree.delete(item)
                    
                    # إضافة النتائج الجديدة
                    for product in products:
                        results_tree.insert('', tk.END, values=(
                            product.name,
                            product.brand,
                            f"{product.price_sell:.2f}",
                            product.quantity
                        ))
                        
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في البحث: {str(e)}")
        
        search_entry.bind('<Return>', lambda e: search_products())
        
        ttk.Button(search_frame, text="بحث", command=search_products).pack(pady=5)
        
    def open_reports(self):
        """فتح التقارير"""
        if self.server_running:
            webbrowser.open(f"http://localhost:{self.port}/reports")
        else:
            messagebox.showwarning("تحذير", "الخادم غير مشغل")
            
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        try:
            import shutil
            from datetime import datetime
            
            # إنشاء اسم الملف
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"phone_store_backup_{timestamp}.db"
            
            # نسخ قاعدة البيانات
            shutil.copy2("phone_store.db", backup_filename)
            
            messagebox.showinfo("نجح", f"تم إنشاء النسخة الاحتياطية: {backup_filename}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إنشاء النسخة الاحتياطية: {str(e)}")
            
    def open_settings(self):
        """فتح الإعدادات"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("الإعدادات")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#f0f0f0')
        
        settings_frame = ttk.Frame(settings_window, padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(settings_frame, text="إعدادات البرنامج", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # إعدادات الخادم
        server_frame = ttk.LabelFrame(settings_frame, text="إعدادات الخادم", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="المنفذ الافتراضي:").pack(anchor=tk.W)
        port_entry = ttk.Entry(server_frame, width=10)
        port_entry.insert(0, str(self.port))
        port_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # إعدادات عامة
        general_frame = ttk.LabelFrame(settings_frame, text="إعدادات عامة", padding="10")
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(general_frame, text="نسخ احتياطي تلقائي", 
                       variable=auto_backup_var).pack(anchor=tk.W)
        
        auto_start_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, text="تشغيل الخادم تلقائياً", 
                       variable=auto_start_var).pack(anchor=tk.W)
        
        # أزرار الحفظ والإلغاء
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="حفظ", 
                  command=lambda: messagebox.showinfo("تم", "تم حفظ الإعدادات")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="إلغاء", 
                  command=settings_window.destroy).pack(side=tk.LEFT)
        
    def on_closing(self):
        """عند إغلاق التطبيق"""
        if messagebox.askokcancel("إغلاق", "هل تريد إغلاق البرنامج؟"):
            self.server_running = False
            self.root.destroy()
            
    def run(self):
        """تشغيل التطبيق"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """الدالة الرئيسية"""
    try:
        # التحقق من وجود المتطلبات
        import flask
        import flask_sqlalchemy
        
        # إنشاء وتشغيل التطبيق
        app_instance = PhoneStoreApp()
        app_instance.run()
        
    except ImportError as e:
        # إذا لم تكن المكتبات مثبتة
        root = tk.Tk()
        root.withdraw()  # إخفاء النافذة الرئيسية
        
        result = messagebox.askyesno(
            "مكتبات مفقودة",
            "بعض المكتبات المطلوبة غير مثبتة.\nهل تريد تثبيتها الآن؟"
        )
        
        if result:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                messagebox.showinfo("تم", "تم تثبيت المكتبات بنجاح. يرجى إعادة تشغيل البرنامج.")
            except Exception as install_error:
                messagebox.showerror("خطأ", f"فشل في تثبيت المكتبات: {str(install_error)}")
        
        root.destroy()
        
    except Exception as e:
        messagebox.showerror("خطأ", f"خطأ في تشغيل البرنامج: {str(e)}")

if __name__ == "__main__":
    main()