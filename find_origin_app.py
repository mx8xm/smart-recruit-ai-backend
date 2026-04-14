from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test Backend for Tauri Desktop App")

# ========================================
# CORS مؤقت: نسمح بأي origin فقط للاختبار
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # مؤقت فقط للاختبار
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Middleware لتسجيل كل الطلبات والـ Origin
# ========================================
@app.middleware("http")
async def log_request_info(request: Request, call_next):
    print("✅ Request received")
    print("Path:", request.url.path)
    print("Method:", request.method)
    print("Origin:", request.headers.get("origin"))
    print("Headers:", request.headers)
    response = await call_next(request)
    return response

# ========================================
# مثال endpoint تسجيل الدخول
# ========================================
@app.post("/api/v1/auth/login")
async def login(data: dict):
    print("🔑 Login attempt data:", data)
    # فقط للاختبار: نرسل response نجاح
    return {"status": "ok", "message": "Login received", "data": data}

# ========================================
# Root endpoint
# ========================================
@app.get("/")
async def root():
    return {"message": "Test Backend Running"}

# ========================================
# تشغيل server
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("find_origin_app:app", host="0.0.0.0", port=8000, reload=True)


"""
✅ Request received
Path: /api/v1/auth/login
Method: POST
Origin: http://tauri.localhost
Headers: Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'content-length': '32', 'sec-ch-ua-platform': '"Windows"', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0', 'accept': 'application/json, text/plain, */*', 'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144", "Microsoft Edge WebView2";v="144"', 'content-type': 'application/x-www-form-urlencoded', 'sec-ch-ua-mobile': '?0', 'origin': 'http://tauri.localhost', 'sec-fetch-site': 'cross-site', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'http://tauri.localhost/', 'accept-encoding': 'gzip, deflate, br, zstd', 'accept-language': 'en-US,en;q=0.9'})
"""