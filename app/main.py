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
from slowapi.errors import RateLimitExceeded

# Importar configurações
from app.core.config import settings

# Importar rate limiter
from app.core.rate_limiter import limiter, custom_rate_limit_handler

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema completo de gestão de imóveis e aluguéis",
    version="5.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Adicionar rate limiter à aplicação
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

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
from app.routes import auth, proprietarios, imoveis, usuarios, alugueis, participacoes, participacoes_versoes, relatorios, transferencias, import_routes, dashboard
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(proprietarios.router)
app.include_router(imoveis.router)
app.include_router(usuarios.router)
app.include_router(alugueis.router)
app.include_router(participacoes.router)
app.include_router(participacoes_versoes.router)
app.include_router(relatorios.router)
app.include_router(transferencias.router)
app.include_router(import_routes.router)

@app.get("/", response_class=RedirectResponse)
async def root():
    """Rota raiz - redireciona para login"""
    return "/login"

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Página de teste"""
    return templates.TemplateResponse("test.html", {"request": request})

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

@app.get("/usuarios", response_class=HTMLResponse)
async def usuarios_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de gestão de usuários (apenas admins)"""
    if not current_user.is_admin:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("usuarios.html", {
        "request": request,
        "title": "Usuários",
        "user": current_user
    })

@app.get("/participacoes", response_class=HTMLResponse)
async def participacoes_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de gestão de participações"""
    return templates.TemplateResponse("participacoes.html", {
        "request": request,
        "title": "Participações",
        "user": current_user
    })

@app.get("/relatorios", response_class=HTMLResponse)
async def relatorios_page(request: Request, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Página de relatórios financeiros"""
    return templates.TemplateResponse("relatorios.html", {
        "request": request,
        "title": "Relatórios",
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
