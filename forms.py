from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange



class UserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=6, max=128)])
    role = SelectField('الدور', choices=[
        ('admin', 'مدير النظام'),
        ('manager', 'مدير متجر'),
        ('cashier', 'كاشير'),
        ('inventory', 'مسؤول مخزون')
    ], validators=[DataRequired()])
    is_active = BooleanField('نشط')
    submit = SubmitField('حفظ المستخدم')

class ProductForm(FlaskForm):
    name = StringField('اسم المنتج', validators=[DataRequired()])
    brand = StringField('الماركة', validators=[DataRequired()])
    model = StringField('الموديل', validators=[DataRequired()])
    color = StringField('اللون', validators=[Optional()])
    description = TextAreaField('الوصف', validators=[Optional()])
    price_buy = DecimalField('سعر الشراء', validators=[DataRequired(), NumberRange(min=0)])
    price_sell = DecimalField('سعر البيع', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('الكمية', validators=[DataRequired(), NumberRange(min=0)])
    min_quantity = IntegerField('الحد الأدنى للكمية', validators=[DataRequired(), NumberRange(min=0)])
    barcode = StringField('الباركود', validators=[Optional()])
    imei = StringField('رقم IMEI', validators=[Optional()])
    warranty_period = IntegerField('مدة الضمان بالأيام', validators=[Optional(), NumberRange(min=0)])
    category_id = SelectField('الفئة', coerce=int, validators=[Optional()])
    supplier_id = SelectField('المورد', coerce=int, validators=[Optional()])
    submit = SubmitField('حفظ المنتج')

class CustomerForm(FlaskForm):
    name = StringField('اسم العميل', validators=[DataRequired()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email()])
    address = TextAreaField('العنوان', validators=[Optional()])
    submit = SubmitField('حفظ العميل')

class SupplierForm(FlaskForm):
    name = StringField('اسم المورد', validators=[DataRequired()])
    company = StringField('الشركة', validators=[Optional()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email()])
    address = TextAreaField('العنوان', validators=[Optional()])
    submit = SubmitField('حفظ المورد')

class CategoryForm(FlaskForm):
    name = StringField('اسم الفئة', validators=[DataRequired()])
    description = TextAreaField('الوصف', validators=[Optional()])
    submit = SubmitField('حفظ الفئة')

class BrandForm(FlaskForm):
    name = StringField('اسم الماركة', validators=[DataRequired()])
    submit = SubmitField('حفظ الماركة')

class StoreSettingsForm(FlaskForm):
    store_name = StringField('اسم المتجر (إنجليزي)', validators=[DataRequired()])
    store_name_ar = StringField('اسم المتجر (عربي)', validators=[DataRequired()])
    address = StringField('العنوان', validators=[Optional()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email()])
    currency_name = StringField('اسم العملة', validators=[DataRequired()])
    currency_symbol = StringField('رمز العملة', validators=[DataRequired()])
    submit = SubmitField('حفظ الإعدادات')

class SaleForm(FlaskForm):
    customer_id = SelectField('العميل', coerce=int, validators=[Optional()])
    total_amount = DecimalField('المبلغ الإجمالي', validators=[DataRequired(), NumberRange(min=0)])
    discount = DecimalField('الخصم', default=0, validators=[Optional(), NumberRange(min=0)])
    payment_method = SelectField('طريقة الدفع', choices=[('نقدي', 'نقدي'), ('بطاقة', 'بطاقة'), ('تحويل', 'تحويل')], validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    final_amount = DecimalField('المبلغ النهائي', validators=[DataRequired(), NumberRange(min=0)])

    submit = SubmitField('إتمام البيع')

class ReturnForm(FlaskForm):
    sale_id = SelectField('رقم الفاتورة الأصلية', coerce=int, validators=[DataRequired()])
    customer_id = SelectField('العميل', coerce=int, validators=[Optional()])
    total_amount = DecimalField('المبلغ الإجمالي للمرتجع', validators=[Optional(), NumberRange(min=0)])
    reason = TextAreaField('سبب الارجاع', validators=[Optional()])
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])
    submit = SubmitField('إضافة مرتجع')