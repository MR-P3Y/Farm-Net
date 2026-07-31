# Barzegar AI API

برزگر دستیار کشاورزی Farm-Net است. این ماژول برای کاربر کشاورز، بر پایهٔ
اشتراک و سهمیهٔ سراسری، دادهٔ مزرعه‌ای که خود کاربر انتخاب کرده و منابع علمی
تأییدشده کار می‌کند. برزگر جایگزین کارشناس، پزشک یا بررسی حضوری نیست.

## مرزهای ایمنی و مالی

- دسترسی به مزرعه فقط با Consent صریح، محدود و قابل لغو مالک انجام می‌شود.
- متن گفتگو، مختصات مزرعه و شناسه‌های کاربر وارد Metrics نمی‌شوند.
- توصیهٔ پرخطر باید منبع، بیان عدم قطعیت و ارجاع به کارشناس داشته باشد.
- تحلیل یک تصویر به‌تنهایی تشخیص قطعی تولید نمی‌کند.
- پیشنهاد دفتر مزرعه تا تأیید صریح مالک هیچ داده‌ای را تغییر نمی‌دهد.
- سهمیه فقط برای خروجی قابل‌استفاده مصرف می‌شود؛ شکست و لغو Reservation را
  آزاد می‌کنند.
- قیمت‌های داخلی محصول بر حسب تومان هستند. اگر Provider هزینه‌ای را به ریال
  گزارش کند، تبدیل به تومان باید در مرز مالی صریح و قابل ممیزی باشد.
- تولید زنده فعلاً با `AI_PROVIDER_ENABLED=false` غیرفعال است تا Billing
  حساب OpenAI فعال شود.

## Farmer operations

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/ai/context-consents` | ایجاد رضایت دسترسی به Farm/Plot/Cycle منتخب |
| GET | `/ai/context-consents` | فهرست رضایت‌های مالک |
| POST | `/ai/context-consents/{consent_id}/revoke` | لغو رضایت |
| POST | `/ai/conversations` | ایجاد گفتگوی خصوصی |
| GET | `/ai/conversations` | فهرست گفتگوهای مالک |
| GET | `/ai/conversations/{conversation_id}` | جزئیات گفتگو |
| POST | `/ai/conversations/{conversation_id}/deletion-requests` | پنهان‌سازی فوری و زمان‌بندی حذف مطابق Retention |
| POST | `/ai/conversations/{conversation_id}/requests` | ثبت درخواست صف‌شونده |
| GET | `/ai/requests/{request_id}` | وضعیت و نتیجهٔ درخواست مالک |
| POST | `/ai/requests/{request_id}/feedback` | بازخورد exact-once مالک درباره پاسخ نهایی |
| POST | `/ai/requests/{request_id}/cancel` | لغو درخواست مجاز |
| POST | `/ai/requests/{request_id}/escalate` | ارجاع صریح به مشاور انسانی |
| GET | `/ai/diary-suggestions` | پیشنهادهای دفتر مزرعه |
| POST | `/ai/diary-suggestions/{suggestion_id}/accept` | تأیید و ثبت عملیات واقعی |
| POST | `/ai/diary-suggestions/{suggestion_id}/reject` | رد پیشنهاد |
| GET | `/ai/farmer-reports` | گزارش‌های Snapshot‌شدهٔ مالک |

`feature_code` و `request_kind` باید زوج معتبر باشند:

| Feature | Kind |
| --- | --- |
| `ai.text_chat` | `text` |
| `ai.farm_context` | `farm_context` |
| `ai.deep_analysis` | `deep_analysis` |
| `ai.image_analysis` | `image_analysis` |
| `ai.smart_diary` | `smart_diary` |
| `ai.report_export` | `report` |

درخواست‌های Context‌دار به Consent فعال و تازه با Purpose متناسب نیاز دارند.
تحلیل تصویر علاوه بر Consent، به `media_file_key` خصوصی و متعلق به همان کاربر
نیاز دارد. هر کاربر حداکثر پنج درخواست `queued/running` هم‌زمان دارد.

Feedback فقط برای پاسخ `succeeded` یا پاسخ ایمنی `blocked` مجاز است. ارسال
دوبارهٔ همان مقدار idempotent و تغییر مقدار قبلی Conflict است. درخواست حذف
تنها برای گفت‌وگوی متعلق به کاربر و فاقد کار فعال پذیرفته می‌شود؛ گفتگو فوراً
به `deletion_pending` می‌رود و حذف نهایی زودتر از `retention_until` انجام
نمی‌شود.

## Admin operations

| Method | Path | Permission/Purpose |
| --- | --- | --- |
| GET | `/admin/ai/overview` | نمای عملیاتی امن |
| GET | `/admin/ai/requests` | Metadata اجراها بدون Prompt/Context |
| GET | `/admin/ai/usage` | Token، latency و هزینهٔ Provider |
| GET | `/admin/ai/feedback` | بازخورد کاربران |
| GET | `/admin/ai/knowledge-sources` | منابع دانش |
| POST | `/admin/ai/knowledge-sources` | ثبت منبع Draft |
| POST | `/admin/ai/knowledge-sources/{source_id}/submit` | ارسال برای بررسی |
| POST | `/admin/ai/knowledge-sources/{source_id}/review` | تأیید یا رد مستند |
| GET | `/admin/ai/audit` | Audit امن |
| GET | `/admin/ai/policies` | نسخه‌های Policy |
| GET | `/admin/ai/models` | Registry مدل بدون Credential |
| POST | `/admin/ai/evaluation/suites` | ساخت Suite به حالت Draft |
| POST | `/admin/ai/evaluation/suites/{suite_id}/activate` | فعال‌سازی تراکنشی نسخه |
| POST | `/admin/ai/evaluation/runs` | اجرای Release Gate قطعی |

سه عملیات Evaluation به `ai.evaluation.manage` نیاز دارند. فعال‌سازی نسخهٔ
جدید، نسخهٔ فعال قبلی همان `suite_key` را Retired می‌کند. Runها exact-once
هستند و متن Candidate ذخیره نمی‌شود؛ فقط SHA-256 و Failure Code محدود نگهداری
می‌شود.

## Common failures

- `401`: توکن وجود ندارد یا معتبر نیست.
- `403`: Permission یا Entitlement کافی نیست.
- `409`: تعارض Idempotency، Consent منقضی، وضعیت نامعتبر یا Suite غیرفعال.
- `422`: Payload، زوج Feature/Kind یا Candidateهای Evaluation نامعتبر است.
- `429 AI_ACTIVE_REQUEST_LIMIT`: پنج درخواست فعال برای کاربر وجود دارد.
- Provider-disabled: درخواست زنده نباید به‌عنوان موفق یا مصرف‌شده ثبت شود.

تمام پاسخ‌ها از Envelope استاندارد `success/data/message/meta` استفاده
می‌کنند و `meta.trace_id` برای پیگیری عملیاتی ارائه می‌شود.
