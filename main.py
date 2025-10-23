from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
import sqlite3
from datetime import datetime
import os

# تنظیم اندازه پنجره برای موبایل
Window.size = (360, 640)

class DatabaseManager:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                date TEXT,
                initial INTEGER DEFAULT 0,
                production INTEGER DEFAULT 0,
                shipment INTEGER DEFAULT 0,
                returns INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # محصولات پیش‌فرض
        default_products = [
            'Kabab Kobideh', 'Fileh Zafrani', 'Fileh Mast',
            'Ba Ostokhan', 'Shishlik', 'Barg'
        ]
        
        for product in default_products:
            cursor.execute('INSERT OR IGNORE INTO products (name) VALUES (?)', (product,))
        
        conn.commit()
        conn.close()
    
    def get_products(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM products')
        products = cursor.fetchall()
        conn.close()
        return products
    
    def save_inventory(self, product_id, date, initial, production, shipment, returns):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO inventory 
            (product_id, date, initial, production, shipment, returns)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, date, initial, production, shipment, returns))
        
        conn.commit()
        conn.close()
    
    def get_today_inventory(self, date):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, i.initial, i.production, i.shipment, i.returns
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id AND i.date = ?
        ''', (date,))
        
        data = cursor.fetchall()
        conn.close()
        
        result = {}
        for row in data:
            name = row[0]
            result[name] = {
                'initial': row[1] or 0,
                'production': row[2] or 0,
                'shipment': row[3] or 0,
                'returns': row[4] or 0
            }
        
        return result

class QuickEntryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # هدر
        header = Label(
            text=f'Quick Data Entry\n{self.current_date}',
            size_hint_y=None,
            height=80,
            font_size='20sp',
            bold=True
        )
        layout.add_widget(header)
        
        # اسکرول برای محصولات
        scroll = ScrollView()
        self.products_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))
        scroll.add_widget(self.products_layout)
        layout.add_widget(scroll)
        
        # دکمه‌های پایین
        buttons_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        report_btn = Button(text='📊 Reports', background_color=(0.2, 0.6, 0.8, 1))
        report_btn.bind(on_press=self.show_reports)
        buttons_layout.add_widget(report_btn)
        
        save_btn = Button(text='💾 Save All', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=self.save_all_data)
        buttons_layout.add_widget(save_btn)
        
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def load_data(self):
        self.products_layout.clear_widgets()
        self.data_inputs = {}
        
        inventory_data = self.db.get_today_inventory(self.current_date)
        products = self.db.get_products()
        
        for product_id, product_name in products:
            product_data = inventory_data.get(product_name, {})
            
            # کارت محصول
            product_card = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height=180,
                padding=10
            )
            product_card.background_color = (0.95, 0.95, 0.95, 1)
            
            # نام محصول
            name_label = Label(
                text=product_name,
                size_hint_y=None,
                height=30,
                bold=True,
                font_size='16sp'
            )
            product_card.add_widget(name_label)
            
            # فیلدهای ورودی
            fields_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120)
            
            inputs = {}
            for field in ['initial', 'production', 'shipment', 'returns']:
                field_layout = BoxLayout(orientation='vertical', spacing=2)
                
                field_label = Label(
                    text=field.upper(),
                    size_hint_y=None,
                    height=20,
                    font_size='12sp'
                )
                field_layout.add_widget(field_label)
                
                field_input = TextInput(
                    text=str(product_data.get(field, 0)),
                    size_hint_y=None,
                    height=40,
                    multiline=False,
                    input_filter='int'
                )
                field_layout.add_widget(field_input)
                
                fields_layout.add_widget(field_layout)
                inputs[field] = field_input
            
            product_card.add_widget(fields_layout)
            self.products_layout.add_widget(product_card)
            self.data_inputs[product_name] = inputs
    
    def save_all_data(self, instance):
        try:
            products = self.db.get_products()
            
            for product_id, product_name in products:
                if product_name in self.data_inputs:
                    inputs = self.data_inputs[product_name]
                    
                    initial = int(inputs['initial'].text) if inputs['initial'].text else 0
                    production = int(inputs['production'].text) if inputs['production'].text else 0
                    shipment = int(inputs['shipment'].text) if inputs['shipment'].text else 0
                    returns = int(inputs['returns'].text) if inputs['returns'].text else 0
                    
                    self.db.save_inventory(
                        product_id, self.current_date, 
                        initial, production, shipment, returns
                    )
            
            self.show_popup("Success", "All data saved successfully!")
            
        except Exception as e:
            self.show_popup("Error", f"Save failed: {str(e)}")
    
    def show_reports(self, instance):
        self.manager.current = 'reports'
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        
        close_btn = Button(text='OK', size_hint_y=None, height=50)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(close_btn)
        
        popup.open()

class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # هدر
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text='← Back', size_hint_x=None, width=100)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        title = Label(text='Inventory Reports', font_size='20sp', bold=True)
        header.add_widget(title)
        layout.add_widget(header)
        
        # محتوای گزارش
        self.report_content = ScrollView()
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.report_content.add_widget(self.content_layout)
        layout.add_widget(self.report_content)
        
        # دکمه بروزرسانی
        refresh_btn = Button(
            text='🔄 Refresh Report', 
            size_hint_y=None, 
            height=50,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        refresh_btn.bind(on_press=self.generate_report)
        layout.add_widget(refresh_btn)
        
        self.add_widget(layout)
        
        # تولید گزارش اولیه
        Clock.schedule_once(lambda dt: self.generate_report(None), 0.1)
    
    def generate_report(self, instance):
        self.content_layout.clear_widgets()
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        inventory_data = self.db.get_today_inventory(current_date)
        
        # خلاصه موجودی
        summary_card = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=120,
            padding=10
        )
        summary_card.background_color = (0.9, 0.95, 1, 1)
        
        summary_label = Label(
            text='📊 TODAY\'S SUMMARY',
            size_hint_y=None,
            height=30,
            bold=True,
            font_size='16sp'
        )
        summary_card.add_widget(summary_label)
        
        total_initial = sum(data['initial'] for data in inventory_data.values())
        total_production = sum(data['production'] for data in inventory_data.values())
        total_shipment = sum(data['shipment'] for data in inventory_data.values())
        total_returns = sum(data['returns'] for data in inventory_data.values())
        total_final = total_initial + total_production - total_shipment + total_returns
        
        summary_text = f"""Initial: {total_initial} | Production: {total_production}
Shipment: {total_shipment} | Returns: {total_returns}
FINAL: {total_final} skewers"""
        
        summary_details = Label(
            text=summary_text,
            size_hint_y=None,
            height=80,
            font_size='14sp'
        )
        summary_card.add_widget(summary_details)
        self.content_layout.add_widget(summary_card)
        
        # جزئیات محصولات
        for product_name, data in inventory_data.items():
            final = data['initial'] + data['production'] - data['shipment'] + data['returns']
            
            product_card = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height=100,
                padding=10
            )
            product_card.background_color = (0.95, 0.95, 0.95, 1)
            
            product_header = Label(
                text=f"🍢 {product_name}",
                size_hint_y=None,
                height=30,
                bold=True,
                font_size='14sp'
            )
            product_card.add_widget(product_header)
            
            details_text = f"""I:{data['initial']} + P:{data['production']} - S:{data['shipment']} + R:{data['returns']} = {final}"""
            
            product_details = Label(
                text=details_text,
                size_hint_y=None,
                height=60,
                font_size='12sp'
            )
            product_card.add_widget(product_details)
            self.content_layout.add_widget(product_card)
    
    def go_back(self, instance):
        self.manager.current = 'main'

class InventoryApp(App):
    def build(self):
        self.title = "Kabab Inventory"
        
        sm = ScreenManager()
        sm.add_widget(QuickEntryScreen(name='main'))
        sm.add_widget(ReportsScreen(name='reports'))
        
        return sm

if __name__ == '__main__':
    InventoryApp().run()
