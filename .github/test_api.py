import urllib.request
from urllib.parse import urlencode
import json
import time
import concurrent.futures

API = "https://gaza-c.online/api.php"

# إعدادات الاختبار
START = 400000000
END = 900000000
STEP = 1
MAX_WORKERS = 200  # عدد الطلبات التي سيتم إرسالها في نفس الوقت (يمكنك زيادتها حسب قوة سيرفرك)

def fetch_id(number):
    """دالة لجلب بيانات ID واحد"""
    test_id = f"{number:09d}"
    params = {
        "id": test_id,
        "limit": 2500000,
        "offset": 0
    }
    
    url = API + "?" + urlencode(params)
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "GazaC-TestClient/2.0-Fast"}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            
        if data.get("ok"):
            found = data.get("results", [])
            if found:
                print(f"[FOUND] {test_id} -> {len(found)} result(s)")
                return found
            else:
                print(f"[EMPTY] {test_id}")
                return []
        else:
            print(f"[ERROR] {test_id}: {data.get('error', 'Unknown error')}")
            return []
            
    except Exception as e:
        print(f"[FAIL] {test_id}: {e}")
        return []

if __name__ == '__main__':
    start_time = time.time()
    results = []
    
    # تجهيز قائمة الأرقام التي سنفحصها
    numbers = list(range(START, END + 1, STEP))
    
    print(f"بدء جلب {len(numbers)} طلب باستخدام {MAX_WORKERS} مسارات متزامنة...")

    # استخدام ThreadPoolExecutor لتشغيل الطلبات في نفس الوقت
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # تنفيذ دالة fetch_id على كل رقم في القائمة
        # سيقوم الـ executor بإدارة الطلبات بحيث لا تتجاوز MAX_WORKERS في اللحظة الواحدة
        futures = [executor.submit(fetch_id, num) for num in numbers]
        
        # جمع النتائج فور انتهاء كل طلب
        for future in concurrent.futures.as_completed(futures):
            result_data = future.result()
            if result_data:
                results.extend(result_data)

    # إزالة النتائج المكررة
    unique = {}
    for row in results:
        key = str(row.get("id", ""))
        if key:
            unique[key] = row

    final_results = list(unique.values())

    # حفظ النتائج
    with open("test_results_fast.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)

    end_time = time.time()

    print()
    print("=" * 40)
    print("انتهى الاختبار السريع")
    print("=" * 40)
    print(f"الوقت المستغرق: {end_time - start_time:.2f} ثانية")
    print("عدد النتائج:", len(final_results))
    print("الملف: test_results_fast.json")
    print("=" * 40)

