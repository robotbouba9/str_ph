# -*- coding: utf-8 -*-
"""
مولد الفواتير الحرارية للطابعات الحرارية 80mm
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

class ThermalInvoiceGenerator:
    """مولد الفواتير الحرارية"""
    
    def __init__(self):
        self.width = 80 * mm  # عرض الفاتورة الحرارية
        self.height = 120 * mm  # ارتفاع مناسب للطابعات الحرارية الحديثة

        # تسجيل الخطوط العربية
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf')) # Fallback or specific Arabic font
        except Exception as e:
            print(f"Error registering fonts: {e}")

        # تعريف الأنماط مع الخطوط العربية
        self.arabic_normal_style = ParagraphStyle(
            'ArabicNormal',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Arabic',
            fontSize=7,
            alignment=TA_RIGHT,
            spaceAfter=0.5
        )
        self.arabic_title_style = ParagraphStyle(
            'ArabicTitle',
            parent=getSampleStyleSheet()['Heading1'],
            fontName='Arabic',
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=2,
            textColor=colors.black
        )
        self.arabic_final_style = ParagraphStyle(
            'ArabicFinal',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Arabic',
            fontSize=9,
            alignment=TA_RIGHT,
            spaceAfter=1,
            textColor=colors.black
        )
        
    def generate_sale_invoice(self, sale, store_settings=None):
        """إنشاء فاتورة بيع حرارية"""
        buffer = BytesIO()
        
        # إعداد الصفحة
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(self.width, self.height),
            rightMargin=2*mm,
            leftMargin=2*mm,
            topMargin=2*mm,
            bottomMargin=2*mm
        )
        
        # إعداد الأنماط
        title_style = self.arabic_title_style
        normal_style = self.arabic_normal_style
        right_style = self.arabic_normal_style
        
        story = []
        
        # عنوان المتجر
        store_name = store_settings.store_name if store_settings else "متجر الهواتف"
        story.append(Paragraph(store_name, title_style))
        
        if store_settings and store_settings.address:
            story.append(Paragraph(store_settings.address, normal_style))
        
        if store_settings and store_settings.phone:
            story.append(Paragraph(f"هاتف: {store_settings.phone}", normal_style))
        
        story.append(Spacer(1, 0.5*mm))
        
        # معلومات الفاتورة
        story.append(Paragraph("فاتورة بيع", title_style))
        story.append(Paragraph(f"رقم الفاتورة: {sale.id}", right_style))
        story.append(Paragraph(f"التاريخ: {sale.created_at.strftime('%Y-%m-%d %H:%M')}", right_style))
        
        if sale.customer:
            story.append(Paragraph(f"العميل: {sale.customer.name}", right_style))
        
        story.append(Spacer(1, 1*mm))
        
        # جدول المنتجات
        data = [['المنتج', 'الكمية', 'السعر', 'المجموع']]
        
        for item in sale.items:
            product_name = item.product.name[:20] + "..." if len(item.product.name) > 20 else item.product.name
            data.append([
                product_name,
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total_price:.2f}"
            ])
        
        table = Table(data, colWidths=[25*mm, 10*mm, 15*mm, 15*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 1*mm))
        
        # المجاميع
        currency = store_settings.currency_symbol if store_settings else "د.ج"
        
        story.append(Paragraph(f"المجموع الفرعي: {sale.subtotal:.2f} {currency}", self.arabic_normal_style))
        
        if sale.discount_amount > 0:
            story.append(Paragraph(f"الخصم: {sale.discount_amount:.2f} {currency}", self.arabic_normal_style))
        
        if sale.tax_amount > 0:
            story.append(Paragraph(f"الضريبة: {sale.tax_amount:.2f} {currency}", self.arabic_normal_style))
        
        # المجموع النهائي
        story.append(Paragraph(f"<b>المجموع النهائي: {sale.final_amount:.2f} {currency}</b>", self.arabic_final_style))
        
        story.append(Spacer(1, 1*mm))
        
        # رسالة الشكر
        story.append(Paragraph("شكراً لزيارتكم", normal_style))
        story.append(Paragraph("نتمنى لكم يوماً سعيداً", normal_style))
        
        # بناء الـ PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_purchase_invoice(self, purchase, store_settings=None):
        """إنشاء فاتورة شراء حرارية"""
        buffer = BytesIO()
        
        # إعداد الصفحة
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(self.width, self.height),
            rightMargin=2*mm,
            leftMargin=2*mm,
            topMargin=2*mm,
            bottomMargin=2*mm
        )
        
        # إعداد الأنماط
        title_style = self.arabic_title_style
        normal_style = self.arabic_normal_style
        right_style = self.arabic_normal_style
        
        story = []
        
        # عنوان المتجر
        store_name = store_settings.store_name if store_settings else "متجر الهواتف"
        story.append(Paragraph(store_name, title_style))
        
        story.append(Spacer(1, 0.5*mm))
        
        # معلومات الفاتورة
        story.append(Paragraph("فاتورة شراء", title_style))
        story.append(Paragraph(f"رقم الفاتورة: {purchase.id}", right_style))
        story.append(Paragraph(f"التاريخ: {purchase.created_at.strftime('%Y-%m-%d %H:%M')}", right_style))
        
        if purchase.supplier:
            story.append(Paragraph(f"المورد: {purchase.supplier.name}", right_style))
        
        story.append(Spacer(1, 0.5*mm))
        
        # جدول المنتجات
        data = [['المنتج', 'الكمية', 'السعر', 'المجموع']]
        
        for item in purchase.items:
            product_name = item.product.name[:20] + "..." if len(item.product.name) > 20 else item.product.name
            data.append([
                product_name,
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total_price:.2f}"
            ])
        
        table = Table(data, colWidths=[25*mm, 10*mm, 15*mm, 15*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*mm))
        
        # المجموع النهائي
        currency = store_settings.currency_symbol if store_settings else "د.ج"
        
        final_style = ParagraphStyle(
            'FinalStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_RIGHT,
            spaceAfter=1
        )
        
        story.append(Paragraph(f"<b>المجموع النهائي: {purchase.total_amount:.2f} {currency}</b>", final_style))
        
        # بناء الـ PDF
        doc.build(story)
        buffer.seek(0)
        return buffer