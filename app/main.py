"""
AlugueisV5 - Sistema de Gestão de Aluguéis
Aplicação FastAPI principal
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

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

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Importar e incluir rotas
from app.routes import auth, imoveis, usuarios
app.include_router(auth.router)
app.include_router(imoveis.router)
app.include_router(usuarios.router)

@app.get("/", response_class=RedirectResponse)
async def root():
    """Rota raiz - redireciona para login"""
    return "/login"

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página do dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "title": "Dashboard"
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
