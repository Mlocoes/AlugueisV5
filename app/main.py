"""
AlugueisV5 - Sistema de Gestão de Aluguéis
Aplicação FastAPI principal
"""
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario

# Importar configurações
from app.core.config import settings

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema completo de gestão de imóveis e aluguéis",
    version="5.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler para redirecionar 401 para login em rotas HTML
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Redireciona para login em caso de 401 em rotas HTML"""
    # Se for erro 401 e a requisição aceita HTML, redireciona
    if exc.status_code == 401:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login", status_code=303)
    # Caso contrário, retorna erro JSON
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Importar e incluir rotas
from app.routes import auth, proprietarios, imoveis, usuarios, alugueis
app.include_router(auth.router)
app.include_router(proprietarios.router)
app.include_router(imoveis.router)
app.include_router(usuarios.router)
app.include_router(alugueis.router)

@app.get("/", response_class=RedirectResponse)
async def root():
    """Rota raiz - redireciona para login"""
    return "/login"

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página do dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "title": "Dashboard",
        "user": current_user
    })

@app.get("/proprietarios", response_class=HTMLResponse)
async def proprietarios_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de gestão de proprietários"""
    return templates.TemplateResponse("proprietarios.html", {
        "request": request,
        "title": "Proprietários",
        "user": current_user
    })

@app.get("/imoveis", response_class=HTMLResponse)
async def imoveis_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de gestão de imóveis"""
    return templates.TemplateResponse("imoveis.html", {
        "request": request,
        "title": "Imóveis",
        "user": current_user
    })

@app.get("/alugueis", response_class=HTMLResponse)
async def alugueis_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de gestão de aluguéis"""
    return templates.TemplateResponse("alugueis.html", {
        "request": request,
        "title": "Aluguéis",
        "user": current_user
    })

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
