import re
import torch
import logging

from app.ai.model_loader import get_gliner_model

logger = logging.getLogger(__name__)

class SmartCVExtractor:
    def __init__(self):
        logger.info("⚙️ Loading GLiNER Model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"⚡ Running on: {self.device.upper()}")
        
        try:
            self.model = get_gliner_model()
            logger.info("✅ GLiNER Model Loaded Successfully.")
        except Exception as e:
            logger.error(f"❌ Error loading GLiNER model: {e}")
            self.model = None

    def extract_email_regex(self, text):
        """
        استخراج الإيميل بالمعادلات الرياضية (دقة 100%)
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            return emails[0]
        return "Unknown"

    def chunk_text(self, text, max_words=100):
        """ تقسيم النص إلى 100 كلمة لتجنب خطأ Truncation في GLiNER """
        words = text.split()
        return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

    def extract_info(self, text: str) -> dict:
        if not text or not self.model:
            return {"name": "Unknown", "university": [], "email": "Unknown", "skills": []}

        # 1. استخراج الإيميل بالـ Regex أولاً
        exact_email = self.extract_email_regex(text)

        labels = ["person", "university", "skill"] 

        extracted_data = {
            "name": "Unknown",
            "university": [],
            "email": exact_email,
            "skills": []
        }

        best_name_score = 0.0

        # ==========================================
        # ⛔ القائمة السوداء الشاملة (Bad Words)
        # ==========================================
        bad_words = [
            # --- General & Layout ---
            "resume", "cv", "curriculum", "vitae", "profile", "personal", "info",
            "summary", "objective", "experience", "education", "skills", "projects",
            "page", "of", "contact", "me", "about", "history",
            
            # --- Contact Info ---
            "email", "phone", "mobile", "address", "tel", "fax", "website",
            "linkedin", "github", "gmail", "yahoo", "hotmail", "outlook",
            
            # --- Personal Details ---
            "date", "birth", "nationality", "gender", "marital", "status", "single", "married",
            
            # --- Corporate & Education ---
            "university", "school", "college", "institute", "academy",
            "company", "corporation", "ltd", "gmbh", "inc", "group", "holdings",
            "department", "faculty", "center", "centre", "solutions", "technologies",
            
            # --- Locations (Cities/Countries - EN/FR) ---
            "usa", "uk", "uae", "ksa", "canada", "france", "germany", "india",
            "paris", "london", "new york", "dubai", "cairo", "riyadh", "casablanca",
            "street", "road", "avenue", "boulevard", "lane", "drive", "block", "floor",
            "city", "town", "village", "state", "province", "region", "district",
            "rue", "place", "ville", "pays", "maroc", "tunisie", "algerie",
            
            # --- Job Titles (Common false positives) ---
            "manager", "director", "engineer", "developer", "consultant",
            "assistant", "specialist", "coordinator", "officer", "analyst",
            "senior", "junior", "lead", "head", "executive", "intern",
            "ingénieur", "développeur", "directeur", "technicien",
            
            # --- Arabic Terms (الكلمات العربية الممنوعة) ---
            "جامعة", "مدرسة", "معهد", "كلية", "شركة", "مؤسسة",
            "شارع", "حي", "منطقة", "مدينة", "دولة", "محافظة",
            "مصر", "السعودية", "الإمارات", "المغرب", "الجزائر", "تونس",
            "القاهرة", "الرياض", "دبي", "جدة", "عمان", "الدار البيضاء",
            "سيرة", "ذاتية", "ملف", "شخصي", "معلومات", "اتصال",
            "هاتف", "جوال", "بريد", "إلكتروني", "عنوان", "تاريخ", "ميلاد",
            "مهندس", "مدير", "مبرمج", "محاسب", "طبيب", "أستاذ", "خبير"
        ]

        chunks = self.chunk_text(text, max_words=100)

        # 4. تشغيل GLiNER
        for chunk in chunks:
            try:
                entities = self.model.predict_entities(chunk, labels, threshold=0.35)
            except Exception as e:
                logger.error(f"Prediction Error on chunk: {e}")
                continue

            for entity in entities:
                text_val = entity["text"].strip()
                label = entity["label"]
                score = entity["score"]

                if label == "person":
                    clean_val = text_val.lower()
                    
                    # 1. فحص القائمة السوداء (المدن، الوظائف، إلخ)
                    is_bad = False
                    for bad in bad_words:
                        # نفحص إذا الكلمة الممنوعة موجودة ككلمة كاملة
                        if f" {bad} " in f" {clean_val} ": 
                            is_bad = True
                            break
                        # فحص جزئي للكلمات الخطيرة جداً
                        if bad in clean_val and len(bad) > 4: 
                             is_bad = True
                             break
                    
                    if is_bad: continue
                    # 2. شروط إضافية للدقة
                    if len(text_val.split()) < 2: continue # نرفض الاسم المكون من كلمة واحدة
                    if any(char.isdigit() for char in clean_val) or "@" in clean_val: continue
                    if len(text_val) < 4: continue # نرفض الأسماء القصيرة جداً

                    # اختيار الاسم صاحب أعلى دقة
                    if score > best_name_score:
                        best_name_score = score
                        # تنظيف النجوم (**) التي يضيفها Markdown للـ bold
                        extracted_data["name"] = text_val.replace('*', '').strip()

                elif label == "university":
                    clean_uni = text_val.replace('*', '').strip()
                    if clean_uni and clean_uni not in extracted_data["university"]:
                        extracted_data["university"].append(clean_uni)
                
                elif label == "skill":
                    clean_skill = text_val.replace('*', '').strip()
                    if clean_skill and clean_skill not in extracted_data["skills"]:
                        extracted_data["skills"].append(clean_skill)

        return extracted_data

# ==========================================
# للتجربة بشكل مستقل (اختياري)
# ==========================================
if __name__ == "__main__":
    extractor = SmartCVExtractor()
    sample_text = "Contact: [mahmoudabdelghani0997@gmail.com](mailto:mahmoudabdelghani0997@gmail.com) \n Name: MAHMOUD ABDELGHANY \n Education: Faculty of Engineering, Alexandria University"
    print(extractor.extract_info(sample_text))
