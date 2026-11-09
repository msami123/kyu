# Kyu Creative Studio — عقل الوكالة الإبداعية

ثمانية وكلاء على نموذجين يشتغلون من سطر الأوامر **باشتراكاتك، بدون أي مفتاح API**:
- وكلاء كلود عبر **Claude Code** (دخول بحساب كلود)
- وكلاء ChatGPT عبر **Codex CLI** (دخول بحساب ChatGPT)

كل وكيل يقرأ مدخلاته ويكتب **ملفه بنفسه** في `work/`، والمشغّل يتحقق أن الملف انكتب.

## مين يكتب أي ملف

| الوكيل | الأداة | الملفات التي يكتبها |
|---|---|---|
| creative-director | Claude Code | `01-brief.md`، `06-concept-decision.md`، `13-final.md` |
| researcher-strategist | Claude Code | `02-research-product.md`، `02-research-audience.md`، `02-research-competitors.md`، `02-research-library.md`، `02-research-trends.md`، ثم `02-research.md` |
| generator-a | Codex | `03-concepts-A.md` |
| generator-b | Claude Code | `03-concepts-B.md` |
| critic | Claude Code | `04-tournament-juror.md`، `04-tournament-scroller.md`، `04-tournament-shopper.md`، `04-tournament-brand.md`، ثم `04-tournament.md`؛ يضيف حكمه داخل ملفات السيناريو؛ `10-review-critic.md` |
| producer | Claude Code | `05-feasibility.md`؛ يضيف فحص الخطة داخل `09-shotlist.md`؛ `10-review-producer.md` |
| writer | Codex | `07-characters.md`، `08-script-v1-a.md`، `08-script-v1-b.md` |
| dop | Codex | `09-shotlist.md`؛ يضيف إصلاح البرومبتات في `12-qc-log.md` |
| qc-supervisor | Claude Code | `11-qc-spec.md`، `12-qc-log.md`، `10-review-qc.md` |

كل الوكلاء يضيفون قراراتهم إلى `decision-log.md` (إضافة فقط، بدون تعديل).

**ملفات تكتبها أنت:**
- `00-client-notes.md`: كلام العميل.
- `08-script-approved.md`: نسخة السيناريو الذي اجتاز البوابة.
- `work/production/`: صور المرحلة ٠٨.
- `work/cut/`: إطارات النسخة للمراجعة.

## التشغيل لأول مرة

```bash
# 1) الأدوات وتسجيل الدخول (مرة واحدة)
claude auth login          # بحساب كلود (اشتراك)
codex login                # اختر Sign in with ChatGPT

# 2) المشروع
cd kyu-creative-studio
pip install pyyaml
git init && git add -A && git commit -m "init"     # Codex يحتاج مستودع git، ويعطيك سجل كل تعديل
python3 scripts/build.py
python3 scripts/run.py --doctor                    # يتحقق من كل شيء قبل البدء
```

## التشغيل اليومي

```bash
python3 scripts/run.py --list               # كل الخطوات وحالتها (✓ تم · باقي)
python3 scripts/run.py --stage 01           # مرحلة كاملة، والمتوازي يشتغل معاً
python3 scripts/run.py --stage 06 --step 2  # خطوة واحدة من مرحلة
python3 scripts/run.py --run 08-2-1-qc-supervisor.md   # تشغيل واحد (مثلاً فحص لقطة)
python3 scripts/run.py --stage 02 --dry-run # يعرض الأوامر بدون تشغيل
```

**كيف يتصرف المشغّل:**
- **التخطّي:** يتخطى أي تشغيل ملفه موجود. لإعادته استخدم `--force`.
- **عند الفشل:** يتوقف إذا فشل وكيل أو لم يكتب ملفه، ويحفظ السجل في `logs/`.
- **نهاية المرحلة:** **يتوقف دائماً** ويعرض البوابة أو نقطة موافقة العميل. لا يبدأ المرحلة التالية بنفسه.
- **مرحلة الإنتاج ٠٨:** يدوية. تشغّل فحص الجودة لكل لقطة بـ `--run` عند جاهزيتها.
- **التوازي:** `--parallel 3` افتراضياً. خففه إن وصلت لحدود اشتراكك، لأن كل تشغيل متوازٍ يستهلك من نفس الاشتراك.

**أو من داخل Claude Code:** افتح `claude` في المجلد. الجلسة الرئيسية تعرف من `CLAUDE.md` أنها المنسّق، فتشغّل وكلاء كلود كوكلاء فرعيين، ووكلاء Codex عبر `scripts/run.py --run`.

## التوزيع الحالي

| الوكيل | النموذج |
|---|---|
| creative-director، producer، researcher-strategist، generator-b، critic، qc-supervisor | كلود |
| generator-a، writer، dop | ChatGPT (Codex) |

القاعدة: **من يصنع لا يحكم.** `build.py` يرفض البناء إذا كان الناقد والكاتب، أو مراقب الجودة ومدير التصوير، على نفس النموذج. بعد اختبار المقارنة (`bakeoff/`) عدّل `config/agents.yaml` وأعد البناء.

## البنية

```
agents/            ← المصدر: الأساس المشترك + ملف لكل دور (عدّل هنا)
config/            ← agents.yaml (النموذج لكل وكيل) و pipeline.yaml (المراحل والتوازي)
knowledge/         ← ملف كيو، تصنيف الهوكات، قالب التشريح، الترندات، الاختبار التقني، المكتبة
work/              ← مخرجات الوكلاء والسجلات
bakeoff/           ← اختبار المقارنة الأعمى
scripts/           ← build.py (البناء والتحقق)، run.py (التشغيل)، bakeoff_blind.py
── مولّدة (لا تعدّلها يدوياً) ──
CLAUDE.md, AGENTS.md, .claude/agents/, codex/, kickoffs/
```

## تنبيهات

- **لا مفاتيح:** لا يوجد أي مفتاح API في المشروع. ملفات الدخول المحفوظة (`~/.codex/auth.json` وبيانات Claude Code) عاملها ككلمة مرور، ولا ترفعها لأي مكان.
- **الصلاحيات:** وكلاء كلود يعدّلون الملفات داخل المجلد فقط (`acceptEdits`)، وCodex داخل المجلد فقط وبدون إنترنت (`workspace-write`). لا يُستخدم أي وضع يتجاوز الصلاحيات.
- **بيانات العميل:** تذهب لمزوّدين اثنين. احصل على موافقة كيو وسجّلها في `kyu-brand.md`، ولا صور لأشخاص حقيقيين ولا بيانات عملاء في الـ POC.
- **الامتثال:** مراجعة أنظمة الإعلان السعودية ووسم المحتوى المولّد في تيك توك مسؤولية بشرية قبل النشر.
