// ملف JavaScript رئيسي لتطبيق إدارة مخزون محل الهواتف

// تحديث الوقت الحالي
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ar-DZ', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// تحديث التاريخ الحالي
function updateDate() {
    const now = new Date();
    const dateString = now.toLocaleDateString('ar-DZ', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        dateElement.textContent = dateString;
    }
}

// تنسيق العملة
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-DZ', {
        style: 'currency',
        currency: 'DZD',
        minimumFractionDigits: 2
    }).format(amount);
}

// عرض رسالة إشعار
function showNotification(title, message, type = 'info') {
    const notificationBar = document.getElementById('notification-bar');
    if (!notificationBar) return;

    const notificationTitle = document.getElementById('notification-bar-title');
    const notificationMessage = document.getElementById('notification-bar-message');

    // تحديث محتوى الإشعار
    notificationTitle.textContent = title;
    notificationMessage.textContent = message;

    // تغيير نوع الإشعار
    notificationBar.className = `alert alert-${type} alert-dismissible fade text-center`;

    // عرض الإشعار
    notificationBar.style.display = 'block';

    // إخفاء الإشعار بعد 5 ثواني
    setTimeout(() => {
        notificationBar.classList.remove('show');
        setTimeout(() => {
            notificationBar.style.display = 'none';
        }, 150);
    }, 5000);
}

// التحقق من وجود إشعارات جديدة
function checkForNewNotifications() {
    fetch('/api/notifications?limit=1')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                const notification = data.notifications[0];
                if (!notification.read) {
                    showNotification(notification.title, notification.message, 'warning');
                }
            }
        })
        .catch(error => {
            console.error('Error checking notifications:', error);
        });
}

// عرض رسالة تأكيد
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// عرض رسالة خطأ
function showError(message) {
    showNotification('خطأ', message, 'danger');
}

// عرض رسالة نجاح
function showSuccess(message) {
    showNotification('نجاح', message, 'success');
}

// عرض رسالة تحذير
function showWarning(message) {
    showNotification('تحذير', message, 'warning');
}

// التحقق من صحة النموذج
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// تحميل الصور المصغرة
function loadThumbnail(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    if (input && preview) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }

                reader.readAsDataURL(file);
            }
        });
    }
}

// البحث التلقائي
function setupAutocomplete(inputId, apiUrl, resultsId, onSelectCallback) {
    const input = document.getElementById(inputId);
    const resultsContainer = document.getElementById(resultsId);

    if (!input || !resultsContainer) return;

    let searchTimeout;

    input.addEventListener('input', function() {
        clearTimeout(searchTimeout);

        const query = this.value.trim();
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`${apiUrl}?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displaySearchResults(data.results, resultsContainer, onSelectCallback);
                    } else {
                        showError(data.message || 'حدث خطأ في البحث');
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    showError('حدث خطأ في الاتصال بالخادم');
                });
        }, 300);
    });

    // إخفاء النتائج عند النقر خارجها
    document.addEventListener('click', function(event) {
        if (!input.contains(event.target) && !resultsContainer.contains(event.target)) {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
        }
    });
}

// عرض نتائج البحث
function displaySearchResults(results, container, onSelectCallback) {
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="p-2 text-muted">لا توجد نتائج</div>';
        container.style.display = 'block';
        return;
    }

    container.innerHTML = '';

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'p-2 hover:bg-light cursor-pointer border-bottom';

        // بناء محتوى العنصر حسب نوع البيانات
        let content = '';

        if (result.product_name) {
            // منتج
            content = `
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${result.product_name}</strong>
                        <br>
                        <small class="text-muted">${result.brand} - ${result.model}</small>
                    </div>
                    <div class="text-end">
                        <div>${formatCurrency(result.price_sell)}</div>
                        <small class="text-muted">الكمية: ${result.quantity}</small>
                    </div>
                </div>
            `;
        } else if (result.name) {
            // عميل أو مورد
            content = `
                <div>
                    <strong>${result.name}</strong>
                    ${result.phone ? `<br><small class="text-muted">${result.phone}</small>` : ''}
                    ${result.email ? `<br><small class="text-muted">${result.email}</small>` : ''}
                </div>
            `;
        } else if (result.customer_name) {
            // مبيعات
            content = `
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>#${result.id}</strong>
                        <br>
                        <small class="text-muted">${result.customer_name}</small>
                    </div>
                    <div class="text-end">
                        <div>${formatCurrency(result.final_amount)}</div>
                        <small class="text-muted">${new Date(result.created_at).toLocaleDateString('ar-DZ')}</small>
                    </div>
                </div>
            `;
        }

        item.innerHTML = content;

        // إضافة حدث النقر
        item.addEventListener('click', function() {
            onSelectCallback(result);
            container.innerHTML = '';
            container.style.display = 'none';
        });

        container.appendChild(item);
    });

    container.style.display = 'block';
}

// تهيء وظائف عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحديث الوقت والتاريخ
    updateTime();
    updateDate();
    setInterval(updateTime, 1000);

    // التحقق من الإشعارات كل دقيقة
    setInterval(checkForNewNotifications, 60000);

    // تهيء الأزرار المتقدمة
    document.querySelectorAll('.btn-confirm').forEach(button => {
        button.addEventListener('click', function() {
            const message = this.getAttribute('data-confirm-message') || 'هل أنت متأكد؟';
            confirmAction(message, () => {
                // إرسال النموذج أو تنفيذ الإجراء
                const formId = this.getAttribute('data-form-id');
                if (formId) {
                    document.getElementById(formId).submit();
                } else {
                    this.submit();
                }
            });
        });
    });
});
