bugbountyassistant/
├── main.py                 <-- نقطة الانطلاق (The Brain)
├── config.py               <-- الإعدادات والمسارات
├── core/                   <-- محرك التشغيل والطلب
│   ├── requester.py        # لإجراء طلبات HTTP
│   ├── logger.py           # تسجيل العمليات
│   └── browser_manager.py  # إدارة المتصفح للـ Screenshots
├── storage/                <-- مستودع البيانات (The Loot)
│   ├── active_target.txt   # الهدف الحالي
│   ├── subdomain_results/  # نتائج Amass/Subfinder
│   ├── crawl_results/      # نتائج Gospider/Wayback
│   ├── param_discovery/    # نتائج x8/Arjun
│   ├── web/                # نتائج FFUF (Dirs/Files)
│   ├── loot/               # (SQLmap, JWT, Audit)
│   └── wordlists/          # القواميس المستخدمة
└── tools/                  <-- ترسانة الأسلحة
    ├── recon_tools/        # (Sub-enum, Crawler, Visualizer)
    └── web_tools/          # (Dir/File Discovery, SQLmap, JWT)