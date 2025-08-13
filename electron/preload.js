const { contextBridge, ipcRenderer } = require('electron');

// تعريض APIs آمنة للعارض
contextBridge.exposeInMainWorld('electronAPI', {
    // معلومات التطبيق
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    getServerStatus: () => ipcRenderer.invoke('get-server-status'),
    
    // وظائف النسخ الاحتياطي
    createBackup: () => ipcRenderer.invoke('create-backup'),
    
    // معلومات النظام
    platform: process.platform,
    
    // وظائف مساعدة
    openExternal: (url) => {
        // التحقق من صحة الرابط قبل فتحه
        if (url.startsWith('http://') || url.startsWith('https://')) {
            ipcRenderer.send('open-external', url);
        }
    }
});

// إضافة تحسينات للواجهة
window.addEventListener('DOMContentLoaded', () => {
    // إضافة كلاس للتطبيق للتمييز عن المتصفح
    document.body.classList.add('electron-app');
    
    // تحسين التمرير
    document.body.style.overflow = 'auto';
    
    // منع السحب والإفلات للملفات
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });
    
    document.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });
    
    // تحسين النقر بالزر الأيمن
    document.addEventListener('contextmenu', (e) => {
        // السماح بالقائمة المنبثقة في حقول الإدخال فقط
        if (!e.target.matches('input, textarea')) {
            e.preventDefault();
        }
    });
    
    // إضافة معلومات التطبيق إلى الصفحة
    const addAppInfo = async () => {
        try {
            const version = await window.electronAPI.getAppVersion();
            const serverStatus = await window.electronAPI.getServerStatus();
            
            // إضافة معلومات في الفوتر إذا كان موجود
            const footer = document.querySelector('footer, .footer');
            if (footer) {
                const appInfo = document.createElement('small');
                appInfo.className = 'text-muted electron-info';
                appInfo.innerHTML = `
                    <i class="fas fa-desktop me-1"></i>
                    تطبيق سطح المكتب v${version} | 
                    الخادم: ${serverStatus.isReady ? '🟢 متصل' : '🔴 غير متصل'}
                `;
                footer.appendChild(appInfo);
            }
        } catch (error) {
            console.log('لا يمكن الحصول على معلومات التطبيق:', error);
        }
    };
    
    // تشغيل بعد تحميل الصفحة
    setTimeout(addAppInfo, 1000);
});

// إضافة CSS مخصص للتطبيق
const electronStyles = `
    /* تحسينات خاصة بـ Electron */
    .electron-app {
        -webkit-app-region: no-drag;
    }
    
    .electron-info {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 11px;
        z-index: 9999;
        pointer-events: none;
    }
    
    /* تحسين شريط التمرير */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* تحسين النماذج */
    input:focus, textarea:focus, select:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(0,123,255,.25);
    }
    
    /* تحسين الأزرار */
    .btn:focus {
        box-shadow: 0 0 0 2px rgba(0,123,255,.25);
    }
    
    /* إخفاء شريط التمرير الأفقي غير المرغوب فيه */
    body {
        overflow-x: hidden;
    }
    
    /* تحسين الجداول في الشاشات الصغيرة */
    @media (max-width: 768px) {
        .table-responsive {
            font-size: 0.875rem;
        }
    }
`;

// إضافة الأنماط عند تحميل الصفحة
window.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = electronStyles;
    document.head.appendChild(style);
});